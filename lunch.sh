#!/bin/bash
cd /Users/Przemek/Desktop/lunch_script
source lunch_script/bin/activate
RET=1;until [[ $RET = 0 ]];do python lunch.py; RET="$?";sleep 15m;done
