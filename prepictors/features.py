import math
import numpy as np
from copy import deepcopy

def strToListList(pixelString, rows=0):
    n = len(pixelString)
    if rows==0:
        nx = math.sqrt(n)
        if nx != int(nx):
            print('strToArray error: string length not a perfect square')
            return -1
        else:
            nx = int(nx)
            ny = nx
    else:
        ny = float(n)/rows
        if ny != int(ny):
            print('strToArray error: number of rows does not divide string length')
            return -1
        else:
            ny = int(ny)
            nx = rows
    pixelArray = []
    for j in range(ny):
        pixelArray.append([int(x) for x in pixelString[j*nx:(j+1)*nx]])
    return pixelArray

def shiftPixelArray(pixelArray, shift):
    shiftedArray = deepcopy(pixelArray)
    us, ls = shift
    if ls != 0:
        shiftedArray = [a[ls:] + a[:ls] for a in shiftedArray]
    if us != 0:
        shiftedArray = shiftedArray[us:] + shiftedArray[:us]
    return shiftedArray

def centreArray(pixelArray):
    def first_one(a):
        for i,b in enumerate(a):
            if b>0:
                return i
        return len(a)
    def last_one(a):
        for i,b in enumerate(reversed(a)):
            if b>0:
                return i
        return len(a)
    # find left-most, right-most, top-most and bottom-most 1's
    maxes = [max(a) for a in pixelArray]
    top = first_one(maxes)
    bottom = last_one(maxes)
    left = min([first_one(a) for a in pixelArray])
    right = min([last_one(a) for a in pixelArray])
    #print('top %d, bottom %d, left %d, right %d' % (top, bottom, left, right)) 
    # shift pixelArray accordingly to centre image
    upshift = int((top-bottom)/2)
    leftshift = int((left-right)/2)
    #print('upshift: ' + str(upshift))
    #print('leftshift: ' + str(leftshift))
    return shiftPixelArray(pixelArray, shift=(upshift,leftshift))

## Extract symmetry characteristics
def flipLR(pixelArray):
    # return a left-right mirror of original image
    # make a deep copy of original array
    newArray = deepcopy(pixelArray)
    # reverse each inner list
    for row in newArray:
        row.reverse()
    return newArray

def flipUD(pixelArray):
    # return a top-bottom mirror of original image
    # make a deep copy of original array
    newArray = deepcopy(pixelArray)
    # reverse outer list
    newArray.reverse()
    return newArray

def rotate(pixelArray,n=90):
    # based on Artem Rudenko example
    # return a copy of original image counter-clockwise-rotated by n degrees
    if n % 90 != 0:
        print('rotate error: rotation must be multiple of 90 degrees')
        return -1
    nrot = int(n / 90) % 4
    # make a deep copy of original array
    newArray = deepcopy(pixelArray)
    for rot in range(nrot):
        newArray = list(zip(*newArray))[::-1]
    return newArray

def cellCount(pixelArray,ncell=[2,2],relative=False):
    arr = np.array(pixelArray)
    if relative:
        total_ones = sum(sum(arr))
        arr = np.multiply(float(1.0/total_ones),arr)
    # check if ncell components divide array evenly
    shap = np.shape(arr)
    if sum(shap[i] % ncell[i] for i in (0,1)) > 0:
        print('cellCount error: split does not divide array evenly')
        return -1
    xsize = int(shap[0]/ncell[0])
    ysize = int(shap[1]/ncell[1])
    counts = []
    for i in range(ncell[0]):
        rowCounts = []
        for j in range(ncell[1]):
            rowCounts.append(sum(sum(arr[i*xsize:(i+1)*xsize,j*ysize:(j+1)*ysize])))
        counts.append(rowCounts)
    return counts

def asymmLR(pixelArray):
    return sum(sum(abs(np.array(pixelArray) - np.array(flipLR(pixelArray)))))

def asymmUD(pixelArray):
    return sum(sum(abs(np.array(pixelArray) - np.array(flipUD(pixelArray)))))

def asymmROT(pixelArray):
    return sum(sum(abs(np.array(pixelArray) - np.array(rotate(pixelArray, 180)))))

def applyStat(pixelArray,statName):
    methodToCall = globals()[statName]
    return methodToCall(pixelArray)
