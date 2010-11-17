#!/bin/sh
cd `dirname $0`

if [ -z $MODJEWEL ]; then
    echo "The MODJEWEL environment variable is not set."
    exit
fi

if [ ! -d $MODJEWEL ]; then
    echo "The MODJEWEL environment variable is not set to a directory."
    exit
fi

if [ ! -x $MODJEWEL/module2transportd.py ]; then
    echo "The MODJEWEL environment variable is not set to the right directory."
    exit
fi

if [ -d tmp ]; then
    rm -rf tmp
fi

mkdir tmp

$MODJEWEL/module2transportd.py -o tmp .

OLD=test/sample-browser-template.html
NEW=tmp/sample-browser.html
sed "s!__MODJEWEL__!../$MODJEWEL!" <$OLD >$NEW

echo
echo to run the tests, open $NEW in your browser