#! /usr/bin/env python3
import re
import numpy as np

def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w)).search

def getLastFloatFromString(string,delimiter):
    words = string.split(delimiter)
    if words[0] == 'endTime':
        num = float(words[-1][:-2])
    elif words[0] == 'ExecutionTime':
        try:
            num = (float(words[2]),float(words[7]))
        except:
            num = (float(words[2]),float(words[2]))
    else:
        num = float(words[-1])
    return num



# --------------- code begins ------------------


with open('system/controlDict','r') as file:
    for i,line in enumerate(file):
        if line[:7] == 'endTime':
            try:
                endTime = getLastFloatFromString(line,' ')
            except:
                endTime = getLastFloatFromString(line,'\t')

deltaT = np.array([])
realTime = np.array([])

with open('timeCheck.txt','r') as file:
    for i,line in enumerate(file):
        if findWholeWord('deltaT')(line):
            deltaT = np.append(deltaT,getLastFloatFromString(line,'='))
        if findWholeWord('ExecutionTime')(line):
            num = getLastFloatFromString(line,' ')
            realTime = np.append(realTime,num[0])
            clockTime = num[1]
        if line[:4] == 'Time':
            try:
                currentTime = getLastFloatFromString(line,'=')
            except:
                print('Preliminary')
        if findWholeWord('Date')(line):
            deltaT = np.array([])
            realTime = np.array([])

# get average simulation time step size
deltaTavg = np.average(deltaT)

# get average realTime it takes for each timeStep
realDeltaT = np.diff(realTime)
realDeltaTavg = np.average(realDeltaT)

#print(realDeltaT)
#print(realDeltaTavg)
#print(clockDeltaT)
#print(clockDeltaTavg)

# calculate how long it will take
timeLeft = endTime - currentTime
simTime = np.array([timeLeft,1,10,100])

f = realTime[-1]/clockTime

runTime = simTime*realDeltaTavg/deltaTavg/3600/f

# print results
print('Currently at',currentTime,'EndTime is ',endTime)
print('deltaT is ' + str(round(deltaTavg,6)) + ' s in ' + str(round(realDeltaTavg,2)) + ' s') 
print('Time to finish simulation',round(runTime[0],1),'hours,',round(runTime[0]/24,1),'days')
print('Time to run 1 sec',round(runTime[1],1),'hours,',round(runTime[1]/24,1),'days')
print('Time to run 10 sec',round(runTime[2],1),'hours,',round(runTime[2]/24,1),'days')
print('Time to run 100 sec',round(runTime[3],1),'hours,',round(runTime[3]/24,1),'days')
