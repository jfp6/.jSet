
import os
import sys


dirPath = os.getcwd()
print(dirPath)
inTriSurface = False
if "triSurface" in dirPath:
    print('in triSurface')
    inTriSurface = True
else:
    dirPath = dirPath + '/constant/triSurface'
print(dirPath)

sys.path.insert( 0, dirPath)
dirPathCase = dirPath + ''
if not os.path.exists(dirPathCase):
    os.makedirs(dirPathCase)

for file in os.listdir(dirPath):
    if inTriSurface:
        fileFull = file
    else:
        fileFull = 'constant/triSurface/' + file

    if file.endswith(".stl"):
        print(fileFull)
        name = file[:-4]
        print(name)
        sourceFile = open(fileFull,'r')
        target = fileFull + "t" 
        targetFile = open(target,'w')
        first_row = True
        for row in sourceFile:
            if first_row:
                row = 'solid ' + name + '\n'
                first_row = False
            targetFile.write(row)
        sourceFile.close()
        targetFile.close()
        os.remove(fileFull)
        os.rename(target,target[:-1])

