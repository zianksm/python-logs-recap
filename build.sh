#!/bin/bash

rm -rf app 
mkdir app
cp run.sh ./app
cp rekap.py ./app

tar -zcvf app.tar.gz ./app
rm -rf app 



