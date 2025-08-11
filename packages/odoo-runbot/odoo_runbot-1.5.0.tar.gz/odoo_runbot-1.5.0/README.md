# Mangono runbot (Odoo tester)

This project all the source code relative to the process to test Odoo in the mangono way.

This project support Odoo version `12.0` to `18.0`.

The complete documentation is available [on atlas](https://atlas.docs.mangono.io/)

## Use it as a GitLab CI Components

```yaml
include:
  - component: $CI_SERVER_FQDN/gitlab-ci/odoo-quality/runbot@1
    inputs:
      odoo-version: "18.0"
```

See this component page [for more information](https://gitlab.mangono.io/explore/catalog/gitlab-ci/mangono-runbot)

## Run tests

You can simply run test with
```shell
hatch -e test test
```

If you want to run the runbot on a particular version you can

```shell
docker compose run --rm -it runbot18
```

# Build lib

```shell
hatch build
```


## Build Doc

You can build python code as doc with mkdoc, you only need to run
```shell
hatch -e doc run mkdocs build # or server
```
