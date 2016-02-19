def distance(p1, p2, method='Euclid_sq'):
    import math
    if len(p1) != len(p2):
        print('distance error: vectors of different lengths')
        return -1
    if method=='Euclid_sq':
        # Euclidean distance squared (sqrt doesn't change ordering)
        return sum((p1[i]-p2[i])**2 for i in range(len(p1)))
    if method=='Euclid':
        return math.sqrt(sum((p1[i]-p2[i])**2 for i in range(len(p1))))
    elif method=='Manhattan':
        return sum(abs(p1[i]-p2[i]) for i in range(len(p1)))
    else:
        print('distance error: unknown method')
        return -1

def distToAll(trainList, testVec, method='Euclid_sq'):
    # compute distances from test point to each point in training set
    return [distance(testVec,trainVec,method) for trainVec in trainList] 

def nearestClass(distToAll,trainClass,K=5):
    # return classes of nearest K points in training set to the test point
    import numpy as np
    ind = np.argsort(distToAll)[:K]
    return [trainClass[i] for i in ind]

def majorityNeighbour(nearestClass):
    import numpy as np
    categories, ind = np.unique(nearestClass, return_inverse=True)
    return categories[np.argmax(np.bincount(ind))]

