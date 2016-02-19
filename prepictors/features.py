def strToListList(pixelString, rows=0):
    import math
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

def flipLR(pixelArray):
    # return a left-right mirror of original image
    from copy import deepcopy
    # make a deep copy of original array
    newArray = deepcopy(pixelArray)
    # reverse each inner list
    for row in newArray:
        row.reverse()
    return(newArray)

def flipUD(pixelArray):
    # return a top-bottom mirror of original image
    from copy import deepcopy
    # make a deep copy of original array
    newArray = deepcopy(pixelArray)
    # reverse outer list
    newArray.reverse()
    return(newArray)

def rotate(pixelArray,n=90):
    # based on Artem Rudenko example
    from copy import deepcopy
    # return a copy of original image counter-clockwise-rotated by n degrees
    if n % 90 != 0:
        print('rotate error: rotation must be multiple of 90 degrees')
        return -1
    nrot = (n / 90) % 4
    # make a deep copy of original array
    newArray = deepcopy(pixelArray)
    for rot in range(nrot):
        newArray = zip(*newArray)[::-1]
    return(newArray)

def cellCount(pixelArray,ncell=[2,2]):
    import numpy as np
    arr = np.array(pixelArray)
    # check if ncell components divide array evenly
    shap = np.shape(arr)
    if sum(shap[i] % ncell[i] for i in (0,1)) > 0:
        print('cellCount error: split does not divide array evenly')
        return -1
    xsize = shap[0]/ncell[0]
    ysize = shap[1]/ncell[1]
    counts = []
    for i in range(ncell[0]):
        rowCounts = []
        for j in range(ncell[1]):
            rowCounts.append(sum(sum(arr[i*xsize:(i+1)*xsize,j*ysize:(j+1)*ysize])))
        counts.append(rowCounts)
    return counts

def asymmLR(pixelArray):
    import numpy as np
    return sum(sum(abs(np.array(pixelArray) - np.array(flipLR(pixelArray)))))

def asymmUD(pixelArray):
    import numpy as np
    return sum(sum(abs(np.array(pixelArray) - np.array(flipUD(pixelArray)))))

def asymmROT(pixelArray):
    import numpy as np
    return sum(sum(abs(np.array(pixelArray) - np.array(rotate(pixelArray,180)))))

