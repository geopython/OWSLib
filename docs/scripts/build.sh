#!/bin/sh
# =============================================================================
# Copyright (c) 2010 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@hotmail.com>
#
# Contact email: tomkralidis@hotmail.com
# =============================================================================

LANGUAGES="en"
BASEDIR=/home/tkralidi/foss4g/OWSLib/trunk/docs/
TARGET=/usr/local/wwwsites/apache/devgeo.cciw.ca/htdocs/owslib-docs/trunk

cd $BASEDIR && make clean && make html && rm -fr $TARGET/*

for i in $LANGUAGES;
do
    cp -rp build/html/$i $TARGET 
done
