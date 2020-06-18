#!/bin/bash
set -u
set -e

if [ $# -gt 0 ]; then
    PKG=$(basename $PWD).zip
    FUN=$1; shift;
    aws lambda update-function-code --function-name $FUN --zip-file fileb://$PKG 
    aws lambda update-function-configuration --function-name $FUN "--environment=Variables={FROM_NAME=Campax Team,FROM_EMAIL=dump@cahoots.pl,LOG_LEVEL=DEBUG}"
else
    echo $0 function_name
fi


echo "Remember to increase lambda timeout from default 3 sec!"
# echo "https://lumigo.io/blog/sqs-and-lambda-the-missing-guide-on-failure-modes/"
