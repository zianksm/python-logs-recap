#!/bin/bash

rm -rf auto-rekap 
mkdir auto-rekap
cp run.sh ./auto-rekap
cp rekap.py ./auto-rekap

tar -zcvf auto-rekap.tar.gz auto-rekap
rm -rf auto-rekap 



