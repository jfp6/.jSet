#!/bin/bash

tail -n 10000 log | grep -e Time -e deltaT -e Date > timeCheck.txt

python3 ~/.jSet/timeCheck/timeCheck.py
