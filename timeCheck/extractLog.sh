#!/bin/bash

tail -n 10000 log | grep -e Time -e deltaT -e Date > timeCheck.txt

python ~/.jSet/timeCheck/timeCheck.py
