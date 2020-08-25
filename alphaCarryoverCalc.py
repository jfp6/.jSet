# -*- coding: utf-8 -*-

import os, sys
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import argparse
parser = argparse.ArgumentParser()
cwd = os.getcwd()
import dill


def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w)).search

def getValuesFromString(string,v):
    if v == 'ofp':
        print('add code to work with ofp')
        #words = string.split(' ')
        #num = float(words[0])
    elif v == 'ofo':
        words = string.split('\t')
        time = float(words[0])
        alpha = float(words[1])
    return time,alpha

def getFloatFromString(string):
    words = string.split(' ')
    num = float(words[1][:-1])
    return num

def getArgs():
    parser.add_argument('--v', '--OpenFOAM Version',nargs='*',type=str,default=['ofo'])
    parser.add_argument('--w', '--Rolling Mean Window',nargs='*',type=int,default=[5000])
    parser.add_argument('--case1', '--Case 1 Path',nargs='*',type=str,default=['none'])
    parser.add_argument('--v1', '--OpenFOAM Version for case 1',nargs='*',type=str,default=['ofo'])
    parser.add_argument('--case2', '--Case 2 Path',nargs='*',type=str,default=['none'])
    parser.add_argument('--v2', '--OpenFOAM Version for case 2',nargs='*',type=str,default=['ofo'])
    parser.add_argument('--case3', '--Case 3 Path',nargs='*',type=str,default=['none'])
    parser.add_argument('--v3', '--OpenFOAM Version for case 3',nargs='*',type=str,default=['ofo'])
    parser.add_argument('--case4', '--Case 4 Path',nargs='*',type=str,default=['none'])
    parser.add_argument('--v4', '--OpenFOAM Version for case 4',nargs='*',type=str,default=['ofo'])
    parser.add_argument('--r', '--Range for Plot',nargs='*',type=float,default=['none','none'])
    parser.add_argument('--s', '--Save Data',nargs='*',type=bool,default=[False])

    args = parser.parse_args()
    v = args.v[0]
    w = args.w[0]
    case1Path = args.case1[0]
    v1 = args.v1[0]
    case2Path = args.case2[0]
    v2 = args.v2[0]
    case3Path = args.case3[0]
    v3 = args.v3[0]
    case4Path = args.case4[0]
    v4 = args.v4[0]

    yMin = args.r[0]
    yMax = args.r[1]
    
    saveFlag = args.s[0]
    return (v,w,case1Path,v1,case2Path,v2,case3Path,v3,case4Path,v4,yMin,yMax,saveFlag)

def getFiles():
    timeFiles = os.listdir('postProcessing/patchAverage/')
    timeFiles = [f for f in timeFiles if f[0].isdigit()]
    timeFiles.sort()
    #print(forceFiles)
    #print(timeFiles)
    return timeFiles


def getData(v,w):
    timeFiles = getFiles()
    print('version =',v)
    
    alphaV = []
    timeV = []

    for j,time in enumerate(timeFiles):
        files = os.listdir('postProcessing/patchAverage/'+time)
        momentFile = max(files,key=len)
        print(momentFile)
        try:
            stopTime = float(timeFiles[j+1])
        except:
            stopTime = 1000 
        with open('postProcessing/patchAverage/'+time+'/'+momentFile,'r') as f:
            for i,line in enumerate(f):
                if i>3:
                    time,alpha = getValuesFromString(line,v)
                    if time < stopTime:
                        timeV.append(time)
                        alphaV.append(alpha)

    # grab alphaInlet
    with open('caseGlobalVariables','r') as f:
        for line in f:
            if findWholeWord('alphaInlet')(line):
                alphaInlet = getFloatFromString(line)

    # compute carryover
    alphaV = np.array(alphaV)/alphaInlet*100
    indexStart = timeV.index(2)
    print(np.average(alphaV[indexStart:]))
    
    # create rolling mean
    df = pd.DataFrame()
    df['Time'] = timeV
    df['Alpha'] = alphaV
    alphaMean = df.Alpha.rolling(w).mean()

    return timeV,alphaV,alphaMean

def saveData(timeV,power,c):
    df = pd.DataFrame()
    df['Time'] = timeV
    df['Alpha'] = alphaV
    if c == 0:
        saveName = 'alphaCarryover.csv'
    else:
        saveName = 'alphaCarryoverCase'+str(c)+'.csv'
    df.to_csv(saveName)



#------- main code ------------------
v,w,case1Path,v1,case2Path,v2,case3Path,v3,case4Path,v4,yMin,yMax,saveFlag = getArgs()

cwd = os.getcwd()
timeV,alphaV,alphaMean = getData(v,w)
caseCount = 1
if case1Path != 'none':
    print('running case',case1Path)
    caseCount += 1
    os.chdir(case1Path)
    time1V,alpha1,alpha1Mean = getData(v1,w)
elif case2Path != 'none':
    print('running case',case2Path)
    caseCount += 1
    os.chdir(case2Path)
    time2V,alpha2,alpha2Mean = getData(v2,w)
elif case3Path != 'none':
    print('running case',case3Path)
    caseCount += 1
    os.chdir(case3Path)
    time3V,alpha3,alpha3Mean = getData(v3,w)
elif case4Path != 'none':
    print('running case',case4Path)
    caseCount += 1
    os.chdir(case4Path)
    time4V,alpha4,alpha4Mean = getData(v4,w)

os.chdir(cwd)
if saveFlag:
    saveData(timeV,power,0)
    if caseCount > 1:
        saveData(time1V,power1,1)
    elif caseCount > 2:
        saveData(time2V,power2,2)
    elif caseCount > 3:
        saveData(time3V,power3,3)
    elif caseCount > 4:
        saveData(time4V,power4,4)



# ----------- plot -----------------------

if yMin == 'none':
    yMin = 0
    yMax = max(alphaV)*1.1

plt.figure(1,figsize=(8,6))
font = {'family' : 'sans-serif',
        'weight' : 'normal',
        'size'   : 14}
plt.rc('font',**font)
plt.plot(timeV,alphaV,label='Case 0')
plt.plot(timeV,alphaMean,'-k')
if caseCount > 1:
    plt.plot(time1V,alpha1,label='Case 1')
    plt.plot(timeV,alpha1Mean)
if caseCount > 2:
    plt.plot(time2V,alpha2,label='Case 2')
    plt.plot(timeV,alpha2Mean)
if caseCount > 3:
    plt.plot(time3V,alpha3,label='Case 3')
    plt.plot(timeV,alpha3Mean)
if caseCount > 4:
    plt.plot(time4V,alpha4,label='Case 4')
    plt.plot(timeV,alpha4Mean)

plt.ylim(yMin,yMax)
plt.grid()
plt.xlabel('Simulation Time (s)')
plt.ylabel('alpha')
plt.legend()
plt.show()

