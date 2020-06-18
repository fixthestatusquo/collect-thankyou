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
pipenv lock -r  > requirements.txt
pip3 install --upgrade --target deps/ -r requirements.txt
( cd deps; zip -r9 ../$PKG .)
fi

( cd src; zip ../$PKG *.py)


