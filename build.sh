#!/bin/bash
set -u
set -e

if [ "$#" -gt 0 -a "${1:-}" = "-u" ]; then
    mode=up
else
    mode=all
fi

PKG=$(basename $PWD).zip

if [ $mode = all ]; then
    rm $PKG

    if [ -e Pipfile ]; then
        pipenv lock -r  > requirements.txt
        pip3 install --upgrade --target deps/ -r requirements.txt
        ( cd deps; zip -r9 ../$PKG .)
    fi

    if [ -e package.json ]; then
        yarn install
        zip -r9 $PKG node_modules
    fi
fi

( cd src; zip -r ../$PKG . )

echo "Ok, the lambda code is in $PKG. now run ./deploy.sh function_name"


