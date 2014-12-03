#!/bin/bash

# this script publishes Sphinx outputs to github pages
THIS_DIR=`pwd`

make clean && make html
git clone git@github.com:geopython/OWSLib.git /tmp/OWSLib-$$
cd /tmp/OWSLib-$$
git checkout gh-pages
/bin/cp -rp $THIS_DIR/build/html/en/* .
git add .
git commit -am "update live docs [ci skip]"
git push origin gh-pages

cd $THIS_DIR
rm -fr /tmp/OWSLib-$$
