# -*- coding: utf-8 -*-

import os, sys
import subprocess as sp
from multiprocessing import Process
import numpy as np
import argparse
parser = argparse.ArgumentParser()
cwd = os.getcwd()


def getArgs():
    parser.add_argument('--n', '--Number of Processors',nargs='*',type=float)
    parser.add_argument('--r', '--Range for Plot',nargs='*',type=str,default=[':',':'])

    args = parser.parse_args()
    n = int(args.n[0])
    startTime = args.r[0]
    endTime = args.r[1]
    return n,startTime,endTime

#------- main code ------------------
n,startTime,endTime = getArgs()

pTimes = sp.check_output(['foamListTimes','-processor'])
pTimes = pTimes.decode()
pTimes = pTimes.split("\n")
rTimes = sp.check_output(['foamListTimes'])
rTimes = rTimes.decode()
rTimes = rTimes.split("\n")

# apply range
if startTime == ':':
    indexStart = 0
    indexEnd = -1
else:
    indexStart = pTimes.index(startTime)
    indexEnd = pTimes.index(endTime)+1
    endTime = ':'+endTime
selectTimes = pTimes[indexStart:indexEnd]

# remove times that have already been reconstructed
allTimes = [i for i in selectTimes if i not in rTimes]

# determine number of timeSteps per processor
count = int(len(allTimes)/n)

print('Reconstruct From',allTimes[0],'to',allTimes[-1])

# create list of timeSteps for each processor
times = []
for i in range(n):
    times.append([])
    for j in range(count):
        j = j+(i*count)
        times[i].append(allTimes[j])

if times[-1][-1] != allTimes[-1]:
    times[-1][-1] = times[-1][-1]+endTime
# start reconstruction

def reconstruct(t,i):
    #sp.run(['reconstructPar','-time',','.join(map(str,t))],capture_output=True)
    filename = 'rLog'+str(i)
    with open(filename,'w') as f:
        print('processor',str(i),'reconstructing',t[0],'to',t[-1])
        sp.run(['reconstructPar','-time',','.join(map(str,t))],stdout=f)

processes = []
for i in range(len(times)):
    p = Process(target=reconstruct,args=([times[i],i]))
    p.daemon = True
    p.start()
    processes.append(p)

for p in processes:
    p.join()
