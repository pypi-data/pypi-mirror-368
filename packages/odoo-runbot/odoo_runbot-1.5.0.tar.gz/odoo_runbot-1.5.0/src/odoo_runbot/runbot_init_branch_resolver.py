from __future__ import annotations

import dataclasses
import logging
import subprocess
import typing
from pathlib import Path

import gitlab
from addons_installer import git_addons

if typing.TYPE_CHECKING:
    from addons_installer.addons_installer import OdooAddonsDef

    from .runbot_env import RunbotEnvironment

_logger = logging.getLogger("odoo_runbot")


@dataclasses.dataclass(frozen=True)
class AddonsToInstall:
    """Simple dataclass to hold the Odoo addons to install.

    With wich git branch is tried, the one chosen to clone,
    and if this addons need installation (git clone + pip install).

    Attributes:
        addon: The minimal definition of this addons
        branch_try: The complete liste of git branch (or tag) tried
        branch_to_use: The element in `branch_try` chossen to use on installation process
        to_install: This addons needs to be installed (False if already installed, or disabled)

    """

    addon: OdooAddonsDef
    branch_try: list[str] = dataclasses.field(default_factory=list)
    branch_to_use: str = dataclasses.field(default="")
    to_install: bool = True


class AddonsBranchResolver:
    """Contains the main logic to resolve branch (or tag) to use for each GitAddons found in the current environement.

    See `resolve_branch_addons_git` for more details
    Attributes:
        env: The current environement.
        addons_info: The addons to apply logic
    """

    def __init__(self, env: RunbotEnvironment, addons_info: set[OdooAddonsDef]) -> None:
        self.env = env
        self.addons_info = addons_info

    def _get_gitlab_api(self) -> gitlab.Gitlab | None:
        if not self.env.GITLAB_READ_API_TOKEN:
            return None

        gitlab_api = gitlab.Gitlab(self.env.CI_SERVER_URL, private_token=self.env.GITLAB_READ_API_TOKEN)
        try:
            gitlab_api.auth()
        except gitlab.GitlabAuthenticationError:
            gitlab_api = None
        return gitlab_api

    def resolve_branch_addons_git(self) -> list[AddonsToInstall]:
        """Main function for resolving branch addons.
        Important: Only support gitlab remote git server and it's API to resolve branch

        Get the list to try with `branch_to_try` function, then for each make an api call
        if this branch existe on the remote project then it's the choosen when and no futher try is perform.

        """
        results: list[AddonsToInstall] = []

        gitlab_api = self._get_gitlab_api()
        do_resolve_git = True
        if not gitlab_api:
            msg = "Disable auto find suitable branch"
            if not self.env.CI_API_V4_URL:
                msg += ", missing $CI_API_V4_URL"
            if not self.env.GITLAB_READ_API_TOKEN:
                msg += ", missing $GITLAB_READ_API_TOKEN"
            else:
                msg += ", $GITLAB_READ_API_TOKEN is set but probably not valid anymore. \nPlease contact your Tech Lead"
            _logger.error(msg)
            do_resolve_git = False

        for addon_info in self.addons_info:
            if not isinstance(addon_info, git_addons.GitOdooAddonsResult):
                _logger.warning(
                    "Addons %s isn't a git addons, so we can't change the branche",
                    addon_info.name,
                )
                results.append(AddonsToInstall(addon_info, ["[red] -"], "[red] -"))
                continue
            if Path(addon_info.addons_path).exists():
                branch_name = self._get_branch_name_of_path(addon_info)
                results.append(AddonsToInstall(addon_info, ["[red] already cloned"], "[green] " + branch_name))
                continue

            if not do_resolve_git:
                continue

            current_gl_project = gitlab_api.projects.get(self.env.CI_PROJECT_PATH)
            branch_to_try = self.branch_to_ty(addon_info, current_gl_project)
            remote_project = gitlab_api.projects.get(addon_info.git_path)
            branch_to_use = self.try_find_suitable_branch(remote_project, branch_to_try)
            addon_info.branch = branch_to_use
            if remote_project.visibility != "public":
                addon_info.protocole = "https"
                addon_info.format = git_addons.GitOdooAddons.FORMAT_GIT_CLONE["https"]
                addon_info.https_login = "gitlab-ci-token"
                addon_info.https_password = self.env.CI_DEPLOY_TOKEN or self.env.CI_JOB_TOKEN

            results.append(AddonsToInstall(addon_info, branch_to_try, "[green] " + branch_to_use))
        return results

    def _get_branch_name_of_path(self, addon_info: OdooAddonsDef) -> str:
        return subprocess.check_output(  # noqa: S603
            ["/usr/bin/git", "-C", addon_info.addons_path, "branch", "--show-current"],
        ).decode("utf-8")

    def branch_to_ty(
        self,
        addon: git_addons.GitOdooAddonsResult,
        project: gitlab.v4.objects.projects.Project,
    ) -> list[str]:
        """Return a list of branch names to try on a given project.
        The list is by default composed of:
        - The current branch name -> "CI_COMMIT_REF_NAME"
        - The target branch of the current merge request -> "CI_MERGE_REQUEST_TARGET_BRANCH_NAME"
        - The default branch of the current project
        - The branch for the addon, set with "ADDONS_GIT_<NAME>_BRANCH"
        - The current Odoo version (Last fallback)

        Args:
            addon: The git addons found in env to install.
            project: The curent GitlabProject on wich the runbot is executed (Value of $CI_PROJECT_PATH in env)

        Returns:
            The list of branch to try

        """
        # using `list of dict.fromkeys` to get a list of unique value without loosing the order of the list
        return [
            r
            for r in dict.fromkeys(
                [
                    self.env.CI_COMMIT_REF_NAME,
                    self.env.CI_MERGE_REQUEST_TARGET_BRANCH_NAME,
                    project.default_branch,
                    addon.branch,
                    self.env.ODOO_VERSION,
                ],
            )
            if r
        ]

    def try_find_suitable_branch(
        self,
        project: gitlab.v4.objects.projects.Project,
        branch_to_try_names: list[str],
    ) -> str:
        for branch_name in dict.fromkeys(branch_to_try_names):
            if not branch_name:
                continue
            try:
                return project.branches.get(branch_name).name
            except gitlab.GitlabGetError:
                _logger.warning("Can't fetch branch %s from Gitlab", branch_name)
        _logger.debug(
            "No suitable branche, fallback to default of project %s(%s)", project.name, project.default_branch
        )
        return project.default_branch
