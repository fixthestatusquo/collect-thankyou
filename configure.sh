#!/bin/bash
set -u
set -e

ENVFILE=${2:-env.json}

if [ -e "$ENVFILE" ]; then
    VARIABLES="`cat ${ENVFILE}`"
else
    VARIABLES="{}"
fi

if [ $# -gt 0 ]; then
    PKG=$(basename $PWD).zip
    FUN=$1; shift;
    aws lambda update-function-configuration --function-name $FUN "--environment={ \"Variables\": $VARIABLES}"
else
    echo $0 function_name
fi

