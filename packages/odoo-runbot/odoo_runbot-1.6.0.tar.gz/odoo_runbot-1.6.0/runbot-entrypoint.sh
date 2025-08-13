#!/usr/bin/env bash
cd $CI_PROJECT_DIR

export CI_JOB_ID=$RANDOM
WORKDIR=$CI_PROJECT_DIR/$PATH_TO_TEST
#rm -rf $WORKDIR/runbot_result/*
rm -rf $WORKDIR/runbot_result/.coverage*
set -e
set -x

echo "before_script"
pip install $CI_PROJECT_DIR
coverage --version
odoo-runbot --verbose --workdir=$WORKDIR diag

echo "script"
odoo-runbot --verbose --workdir=$WORKDIR init
odoo-runbot --verbose --workdir=$WORKDIR run "$@"
odoo-runbot --verbose --workdir=$WORKDIR report
