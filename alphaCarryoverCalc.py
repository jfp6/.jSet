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
    num = float(words[1].strip(';\n'))
    return num

def getDfromString(string):
    words = string.split(' ')
    xlow = float(words[3].strip('('))
    ylow = float(words[4])
    zlow = float(words[5].strip(')'))
    xhigh = float(words[6].strip('('))
    yhigh = float(words[7])
    zhigh = float(words[8].strip(')\n'))
    diffV = np.array([xhigh-xlow,yhigh-ylow,zhigh-zlow])
    D = max(diffV)
    return D

def getArgs():
    parser.add_argument('--v', '--OpenFOAM Version',nargs='*',type=str,default=['ofo'])
    parser.add_argument('--w', '--Rolling Mean Window',nargs='*',type=int,default=[5000])
    parser.add_argument('--l', '--Case Label',nargs='*',type=str,default=['none'])
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
    label = args.l[0]
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
    return (v,w,case1Path,v1,case2Path,v2,case3Path,v3,case4Path,v4,yMin,yMax,label,saveFlag)

def getFiles():
    timeFiles = os.listdir('postProcessing/patchAverage/')
    timeFiles = [f for f in timeFiles if f[0].isdigit()]
    timeFiles.sort()
    return timeFiles


def getData(v,w):
    timeFiles = getFiles()
    print('version =',v)
    
    alphaV = [] #np.array([])
    timeV = [] #np.array([])

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

    # grab alphaInlet, UInlet
    with open('caseGlobalVariables','r') as f:
        for line in f:
            if findWholeWord('alphaInlet')(line):
                alphaInlet = getFloatFromString(line)
            if findWholeWord('UInlet')(line):
                UInlet = getFloatFromString(line)
            if findWholeWord('rhow')(line):
                rhoSlurry = getFloatFromString(line)
            if findWholeWord('rhos')(line):
                rhoSteam = getFloatFromString(line)

    # grab density
    # compute carryover
    alphaV = np.array(alphaV)
    carryover = alphaV/alphaInlet*100
    indexStart = timeV.index(2)
    print('Average % Carryover',np.average(carryover[indexStart:]))
    
    # create rolling mean
    df = pd.DataFrame()
    df['Time'] = timeV
    df['Carryover'] = carryover
    carryoverMean = df.Carryover.rolling(w).mean()

    # calculate % wetness
    os.system("surfaceCheck constant/triSurface/inlet.stl | grep 'Box' > boxI.txt")
    with open('boxI.txt','r') as f:
        for line in f:
            DInlet = getDfromString(line)
    areaInlet = DInlet**2*np.pi/4
    totVol = UInlet*areaInlet
    mSlurryOut = alphaV*totVol*rhoSlurry
    mSteamOut = (1-alphaV)*totVol*rhoSteam
    wetness = mSlurryOut/(mSlurryOut+mSteamOut)*100
    print('Average % Wetness',np.average(wetness[indexStart:]))


    return timeV,carryover,carryoverMean

def saveData(timeV,carryover,c):
    df = pd.DataFrame()
    df['Time'] = timeV
    df['Carryover'] = carryover
    if c == 0:
        saveName = 'alphaCarryover.csv'
    else:
        saveName = 'alphaCarryoverCase'+str(c)+'.csv'
    df.to_csv(saveName)



#------- main code ------------------
v,w,case1Path,v1,case2Path,v2,case3Path,v3,case4Path,v4,yMin,yMax,label,saveFlag = getArgs()

cwd = os.getcwd()
timeV,carryover,carryoverMean = getData(v,w)
caseCount = 1
if case1Path != 'none':
    print('running case',case1Path)
    caseCount += 1
    os.chdir(case1Path)
    time1V,carryover1,carryover1Mean = getData(v1,w)
elif case2Path != 'none':
    print('running case',case2Path)
    caseCount += 1
    os.chdir(case2Path)
    time2V,carryover2,carryover2Mean = getData(v2,w)
elif case3Path != 'none':
    print('running case',case3Path)
    caseCount += 1
    os.chdir(case3Path)
    time3V,carryover3,carryover3Mean = getData(v3,w)
elif case4Path != 'none':
    print('running case',case4Path)
    caseCount += 1
    os.chdir(case4Path)
    time4V,carryover4,carryover4Mean = getData(v4,w)

os.chdir(cwd)
if saveFlag:
    saveData(timeV,carryover,0)
    if caseCount > 1:
        saveData(time1V,carryover1,1)
    elif caseCount > 2:
        saveData(time2V,carryover2,2)
    elif caseCount > 3:
        saveData(time3V,carryover3,3)
    elif caseCount > 4:
        saveData(time4V,carryover4,4)



# ----------- plot -----------------------

if yMin == 'none':
    yMin = 0
    yMax = max(carryover)*1.1
if label == 'none':
    label = 'Case 0'

plt.figure(1,figsize=(8,6))
font = {'family' : 'sans-serif',
        'weight' : 'normal',
        'size'   : 14}
plt.rc('font',**font)
plt.plot(timeV,carryover,label=label)
plt.plot(timeV,carryoverMean,'-k',label='_nolegend_')
if caseCount > 1:
    plt.plot(time1V,carryover1)
    plt.plot(timeV,carryover1Mean,label='_nolegend_')
if caseCount > 2:
    plt.plot(time2V,carryover2)
    plt.plot(timeV,carryover2Mean,label='_nolegend_')
if caseCount > 3:
    plt.plot(time3V,carryover3)
    plt.plot(timeV,carryover3Mean,label='_nolegend_')
if caseCount > 4:
    plt.plot(time4V,carryover4)
    plt.plot(timeV,carryover4Mean,label='_nolegend_')

plt.ylim(yMin,yMax)
plt.grid()
plt.xlabel('Time (s)')
plt.ylabel('% Slurry Carryover')
plt.legend()
plt.show()
