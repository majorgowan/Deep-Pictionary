def partition(categories):
    # partition list of categorical data into homogeneous subsets
    #
    # get list of category names
    cat_names = list(set(categories))
    # construct list of indices for each category
    subsets = []
    for category in cat_names:
        subs = [ii for ii,samp in enumerate(categories) \
                if categories[ii]==category]
        subsets.append(subs)
    return cat_names, subsets

def sampleEqually(categories, nsamp=None):
    # given a list of categorical data, return set of indices
    # so that each category is equally represented
    # 
    # number of samples of each category either nsamp or the
    # number of samples in the smallest category
    #
    # returns list of indices
    #
    import random
    #
    cat_names, subsets = partition(categories)
    #
    nsamples = min(len(subset) for subset in subsets)
    if nsamp is not None:
        nsamples = min(nsamp,nsamples)
    #
    sampledList = []
    for subset in subsets:
        sampledList += random.sample(subset,nsamples)
    return sorted(sampledList)

def sampleSplit(categories, splitFraction):
    # given a list of categorical data, sample a
    # fraction of it such that representation of each
    # category in sampled list is equal to same
    # in full list
    #
    # returns list of indices
    #
    import random
    #
    cat_names, subsets = partition(categories)
    #
    lengths = [int(splitFraction*len(subset)) for subset in subsets]
    #
    sampledList = []
    for iset, subset in enumerate(subsets):
        sampledList += random.sample(subset,lengths[iset])
    return sorted(sampledList)


    
