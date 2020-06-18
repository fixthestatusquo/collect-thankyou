#!/bin/bash
set -u
set -e

if [ $# -gt 0 ]; then
    PKG=$(basename $PWD).zip
    FUN=$1; shift;
    aws lambda update-function-code --function-name $FUN --zip-file fileb://$PKG 
else
    echo $0 function_name
fi

echo "Remember to increase lambda timeout from default 3 sec! It's not too much."
echo "Review env.json and run ./configure.sh function_name"
