#!/bin/bash
cd /Users/Przemek/Desktop/lunch_script
source lunch_script/bin/activate
date
RET=1;until [[ $RET = 0 ]];do python lunch.py; RET="$?";sleep 900; date;done
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
