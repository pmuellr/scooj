#!/bin/sh
cd `dirname $0`

node test-driver.js

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
cp -R test tmp
cp ../scooj.js tmp

$MODJEWEL/module2transportd.py -o tmp --htmlFile testDriver.html --htmlMain "require('test-driver')" .
cp $MODJEWEL/modjewel-require.js tmp

echo
echo to run the tests, open tmp/testDriver.html in your browser