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

def getTimeFromString(string,v):
    if v == 'ofp':
        words = string.split(' ')
        num = float(words[0])
    elif v == 'ofo':
        words = string.split('\t')
        num = float(words[0])
    return num

def getOmegaFromString(string):
    words = string.split(' ')
    for i,word in enumerate(words):
        try:
            num = float(word[:-1])
            break
        except:
            pass
    return num

def getTorqueFromString(string,v):
    if v == 'ofp':
        words = string.split('\t')
        total = words[1]
        values = total.split(' ')
        num = float(values[1])
    elif v == 'ofo':
        words = string.split('(')
        total = words[6]
        values = total.split(' ')
        num = float(values[1])
    return num

def getOmegaFromCase(path):
    files = os.listdir(path+'/constant')
    with open(path+'/constant/dynamicMeshDict','r') as file:
        for line in file:
            if findWholeWord('omega')(line):
                omega = getOmegaFromString(line)
                break
    try:
       return  omega
    except:
        print('***ERROR: omega not defined in dynamicMeshDict***')

def getArgs():
    parser.add_argument('--v', '--OpenFOAM Version',nargs='*',type=str,default=['ofo'])
    parser.add_argument('--e', '--efficiency',nargs='*',type=float,default=[0.8])
    parser.add_argument('--w', '--omega',nargs='*',type=float,default=[False])
    parser.add_argument('--case1', '--Case 1 Path',nargs='*',type=str,default=['none'])
    parser.add_argument('--v1', '--OpenFOAM Version for case 1',nargs='*',type=str,default=['ofo'])
    parser.add_argument('--e1', '--efficiency for case 1',nargs='*',type=float,default=[0.8])
    parser.add_argument('--w1', '--omega for case 1',nargs='*',type=float,default=[False])
    parser.add_argument('--case2', '--Case 2 Path',nargs='*',type=str,default=['none'])
    parser.add_argument('--v2', '--OpenFOAM Version for case 2',nargs='*',type=str,default=['ofo'])
    parser.add_argument('--e2', '--efficiency for case 2',nargs='*',type=float,default=[0.8])
    parser.add_argument('--w2', '--omega for case 2',nargs='*',type=float,default=[False])
    parser.add_argument('--case3', '--Case 3 Path',nargs='*',type=str,default=['none'])
    parser.add_argument('--v3', '--OpenFOAM Version for case 3',nargs='*',type=str,default=['ofo'])
    parser.add_argument('--e3', '--efficiency for case 3',nargs='*',type=float,default=[0.8])
    parser.add_argument('--w3', '--omega for case 3',nargs='*',type=float,default=[False])
    parser.add_argument('--case4', '--Case 4 Path',nargs='*',type=str,default=['none'])
    parser.add_argument('--v4', '--OpenFOAM Version for case 4',nargs='*',type=str,default=['ofo'])
    parser.add_argument('--e4', '--efficiency for case 4',nargs='*',type=float,default=[0.8])
    parser.add_argument('--w4', '--omega for case 4',nargs='*',type=float,default=[False])
    parser.add_argument('--r', '--Range for Plot',nargs='*',type=float,default=['none','none'])
    parser.add_argument('--s', '--Save Data',nargs='*',type=bool,default=[False])

    args = parser.parse_args()
    v = args.v[0]
    efficiency = args.e[0]
    omega = args.w[0]
    if omega == False:
        print('getting omega from case')
        omega = getOmegaFromCase(os.getcwd())
    case1Path = args.case1[0]
    v1 = args.v1[0]
    efficiency1 = args.e1[0]
    omega1 = args.w1[0]
    if omega1 == False and case1Path != 'none':
        print('getting omega1 from case1')
        omega1 = getOmegaFromCase(case1Path)
    case2Path = args.case2[0]
    v2 = args.v2[0]
    efficiency2 = args.e2[0]
    omega2 = args.w2[0]
    if omega2 == False and case2Path != 'none':
        print('getting omega2 from case2')
        omega2 = getOmegaFromCase(case2Path)
    case3Path = args.case3[0]
    v3 = args.v3[0]
    efficiency3 = args.e3[0]
    omega3 = args.w3[0]
    if omega3 == False and case3Path != 'none':
        print('getting omega3 from case3')
        omega3 = getOmegaFromCase(case3Path)
    case4Path = args.case4[0]
    v4 = args.v4[0]
    efficiency4 = args.e4[0]
    omega4 = args.w4[0]
    if omega4 == False and case4Path != 'none':
        print('getting omega4 from case4')
        omega4 = getOmegaFromCase(case4Path)

    yMin = args.r[0]
    yMax = args.r[1]
    
    saveFlag = args.s[0]
    return (v,efficiency,omega,case1Path,v1,efficiency1,omega1,case2Path,v2,efficiency2,omega2,
            case3Path,v3,efficiency3,omega3,case4Path,v4,efficiency4,omega4,yMin,yMax,saveFlag)

def getFiles():
    forceFiles = []
    files = os.listdir('postProcessing')
    for f in files:
        if f.startswith('force'):
            forceFiles.append(f)
    forceFiles.sort()
    timeFiles = os.listdir('postProcessing/'+forceFiles[0])
    timeFiles = [f for f in timeFiles if f[0].isdigit()]
    timeFiles.sort()
    #print(forceFiles)
    #print(timeFiles)
    return forceFiles,timeFiles


def getData(v,efficiency,omega):
    forceFiles,timeFiles = getFiles()
    print('Version ',v)
    print('efficiency =',efficiency)
    print('omega =',omega)

    torqueV = []
    for i in range(len(forceFiles)):
        torqueV.append([])
    timeV = []

    for k,force in enumerate(forceFiles):
        for j,time in enumerate(timeFiles):
            files = os.listdir('postProcessing/'+force+'/'+time)
            momentFile = max(files,key=len)
            try:
                stopTime = float(timeFiles[j+1])
            except:
                stopTime = 1000 
            with open('postProcessing/'+force+'/'+time+'/'+momentFile) as f:
                for i,line in enumerate(f):
                    if i>3:
                        time = getTimeFromString(line,v)
                        if time < stopTime:
                            if k == 0:
                                timeV.append(time)
                            torqueV[k].append(getTorqueFromString(line,v))


    power = []
    for i in range(len(torqueV)):
        torque = np.asarray(torqueV[i])
        power.append([])
        power[i] = torque*np.abs(omega)/1000/efficiency
    return timeV,power

def saveData(timeV,power,c):
    df = pd.DataFrame()
    df['Time'] = timeV
    for i in range(len(power)):
        df['Power'+str(i)] = power[i]
    if c == 0:
        saveName = 'power.csv'
    else:
        saveName = 'powerCase'+str(c)+'.csv'
    df.to_csv(saveName)



#------- main code ------------------
v,efficiency,omega,case1Path,v1,efficiency1,omega1,case2Path,v2,efficiency2,omega2,case3Path,v3,efficiency3,omega3,case4Path,v4,efficiency4,omega4,yMin,yMax,saveFlag = getArgs()

cwd = os.getcwd()
timeV,power = getData(v,efficiency,omega)
caseCount = 1
if case1Path != 'none':
    print('running multiple cases')
    caseCount += 1
    os.chdir(case1Path)
    time1V,power1 = getData(v1,efficiency1,omega1)
if case2Path != 'none':
    caseCount += 1
    os.chdir(case2Path)
    time2V,power2 = getData(v2,efficiency2,omega2)
if case3Path != 'none':
    caseCount += 1
    os.chdir(case3Path)
    time3V,power3 = getData(v3,efficiency3,omega3)
if case4Path != 'none':
    caseCount += 1
    os.chdir(case4Path)
    time4V,power4 = getData(v4,efficiency4,omega4)

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
    yMax = power[0][-1]*1.5

plt.figure(1,figsize=(8,6))
font = {'family' : 'sans-serif',
        'weight' : 'normal',
        'size'   : 14}
plt.rc('font',**font)
for i in range(len(power)):
    plt.plot(timeV,power[i],label='Impeller'+str(i))
if caseCount > 1:
    for i in range(len(power1)):
        plt.plot(time1V,power1[i],label='Case 1 Impeller'+str(i))
if caseCount > 2:
    for i in range(len(power2)):
        plt.plot(time2V,power2[i],label='Case 2 Impeller'+str(i))
if caseCount > 3:
    for i in range(len(power3)):
        plt.plot(time3V,power3[i],label='Case 3 Impeller'+str(i))
if caseCount > 4:
    for i in range(len(power4)):
        plt.plot(time4V,power4[i],label='Case 4 Impeller'+str(i))

plt.ylim(yMin,yMax)
plt.grid()
plt.xlabel('Simulation Time (s)')
plt.ylabel('Power (kW)')
plt.legend()
plt.show()

