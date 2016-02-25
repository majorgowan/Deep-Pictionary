from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

from .models import Category, Drawing
from prepictors import features, sampling
import prepictors.knn.knn as knn

# Create your views here.
def index(request):
    return HttpResponse("Hello, world.  Get ready to draw!!")

def chooseCategory(request):
    from random import shuffle
    category_list = list(Category.objects.values_list('category_name',flat=True))
    shuffle(category_list)

    context = {
            'category_list': category_list,
            }
    return render(request, 'drawing/chooseCategory.html', context)

def predictCategory(request):
    image_string = request.POST['imageDataHidden']

    prediction, confidence = predict_knn(image_string,[2,2], K=4,\
            featureList=['asymmLR','asymmUD','asymmROT','cellCount'], equally=True)

    print('I think it is a ' + prediction + '!!!')
    print('(confidence %d)' % int(100*confidence))
    context = {
            'prediction': prediction,
            'confidence': int(100*confidence),
            'image_string': image_string,
            }
    return render(request, 'drawing/predictCategory.html', context)

def indicateCategory(request):
    category_list = list(Category.objects.values_list('category_name',flat=True))
    image_string = request.POST['imageDataHidden']
    predicted_choice = request.POST['predicted']

    context = {
            'prediction': predicted_choice,
            'category_list': category_list,
            'image_string': image_string,
            }
    return render(request, 'drawing/indicateCategory.html', context)

def recordCategory(request):
    from random import shuffle
    selected_choice = request.POST['submit']
    if selected_choice == 'Yes!!!':
        iwasright = True
        selected_choice = request.POST['selected']
        predicted_choice = selected_choice
    else:
        iwasright = False
        predicted_choice = request.POST['predicted']
    # print(selected_choice)
    image_string = request.POST['imageDataHidden']
    draw_date = timezone.now()
    # if drawing is new, update database
    all_the_category = Drawing.objects.filter(category=selected_choice).values_list('bitmap',flat=True)
    if image_string not in all_the_category:
        d = Drawing(bitmap=image_string, category=selected_choice, \
                    predicted=predicted_choice, draw_date=draw_date)
        d.save()
    else:
        print('already have that one, mate!')
    # collect 9 other drawings of the same category 
    last_9 = list(Drawing.objects.filter(category=selected_choice).order_by('-draw_date').values_list('bitmap',flat=True))
    shuffle(last_9)
    last_9 = last_9[1:10]
    # pass info to browser for final flourish
    context = {
            'selected_choice': selected_choice,
            'iwasright': iwasright,
            'image_string': image_string,
            'last_9': last_9,
            }
    return render(request, 'drawing/recordCategory.html', context)

def drawingPad(request):
    return render(request, 'drawing/drawingPad.html')

# browse other drawings
def browse(request):

    bitmapStringList = list(Drawing.objects.values_list('bitmap',flat=True))
    categoryList = list(Drawing.objects.values_list('category',flat=True))
    predictedList = list(Drawing.objects.values_list('predicted',flat=True))

    zipadee = zip(bitmapStringList, categoryList, predictedList)
    zipadee.reverse()

    context = {
            'zipadee': zipadee,
            }
    return render(request, 'drawing/browse.html', context)

# statistics
def statPlots(request):
    ncell = [5,5]
    category_list = list(Category.objects.values_list('category_name',flat=True))

    # plot the statistics for the different categories
    cellCounts = []
    asymmLRs = []
    asymmUDs = []
    asymmROTs = []
    for cat in category_list:
        bitmapStringList = list(Drawing.objects.filter(category=cat).values_list('bitmap',flat=True))
        bitmapList = [features.strToListList(a) for a in bitmapStringList]
        cellCount = [features.cellCount(a,ncell,relative=True) for a in bitmapList]
        cellCounts.append(cellCount)
        
        feat = [features.applyStat(a,'asymmLR') for a in cellCount]
        asymmLRs.append(feat)
        feat = [features.applyStat(a,'asymmUD') for a in cellCount]
        asymmUDs.append(feat)
        feat = [features.applyStat(a,'asymmROT') for a in cellCount]
        asymmROTs.append(feat)

    colours = ['#000099','#ff0000','#009933','#000000']

    zipadee = zip(category_list, cellCounts, asymmLRs, asymmUDs, asymmROTs, colours)

    mins = []
    mins.append(min([x for y in asymmLRs for x in y]))
    mins.append(min([x for y in asymmUDs for x in y]))
    mins.append(min([x for y in asymmROTs for x in y]))

    maxs = []
    maxs.append(max([x for y in asymmLRs for x in y]))
    maxs.append(max([x for y in asymmUDs for x in y]))
    maxs.append(max([x for y in asymmROTs for x in y]))

    context = {
            'zipadee': zipadee,
            'mins': mins, 'maxs': maxs,
            }
    return render(request, 'drawing/statPlots.html', context)

def statTests(request):
    import math

    ncells = [[2,2],[3,3],[5,5],[6,6]]
    #ncells = [[2,2],[3,3]]
    category_list = list(Category.objects.values_list('category_name',flat=True))
    Ks = range(3,7)
    #Ks = range(3,5)

    # test algorithm on training set
    middle_zips = []
    for ncell in ncells:
        print('accuracy test over training set:')
        scores = []
        inner_zips = []
        for KK in Ks:
            predictions, categories, confidences, score = \
                    accuracyTest_knn(ncell, K=KK, \
                    featureList=['asymmLR','asymmUD','asymmROT','cellCount'], \
                    equally=True)
            # accuracy by category:
            correct = []
            total = []
            mean_conf = []
            for category in category_list:
                corr = sum(predictions[ii] == cat for ii,cat in enumerate(categories) if cat==category)
                incorr = sum(predictions[ii] != cat for ii,cat in enumerate(categories) if cat==category)
                mc = sum(confidences[ii] for ii,cat in enumerate(categories) if cat==category)
                mc = math.floor(1000*mc/(corr + incorr))/10
                correct.append(corr)
                total.append(corr+incorr)
                mean_conf.append(mc)
            inner_zips.append(zip(category_list,correct,total,mean_conf))
            scores.append(math.floor(1000*score)/10)
            print('K: %d, accuracy: %f' % (KK,score))
        middle_zips.append(zip(Ks,scores,inner_zips))

    zipadee = zip(ncells, middle_zips)

    context = {
            'zipadee': zipadee,
            }
    return render(request, 'drawing/statTests.html', context)

###########################################
# methods for prediction
def predict_knn(test_bitmap_string, ncell, K=5, \
        featureList=['asymmLR','asymmUD','asymmROT'], equally=False):
    # ncell [m,n]: break images into m x n blocks
    # featureList: list of strings
    #
    # load all bitmaps
    bitmaps = list(Drawing.objects.values_list('bitmap',flat=True))
    # load corresponding list of categories
    categories = list(Drawing.objects.values_list('category',flat=True))
    #
    if equally:
        # sample equal number of each category
        indices = sampling.sampleEqually(categories)
        bitmaps = [bitmaps[ii] for ii in indices]
        categories = [categories[ii] for ii in indices]
    #
    # convert bitmap strings to lists of lists
    trainLoL = [features.strToListList(a) for a in bitmaps]
    testLoL = features.strToListList(test_bitmap_string)
    #
    # centre images
    trainLoL = [features.centreArray(a) for a in trainLoL]
    testLoL = features.centreArray(testLoL)
    # compute cell-block counts
    blockTrain = [features.cellCount(a,ncell,relative=True) for a in trainLoL]
    blockTest = features.cellCount(testLoL,ncell,relative=True)
    # compute requested features and construct feature LoL for knn
    featureLoL = []
    feature_test = []
    for statName in featureList:
        if statName != 'cellCount':
            feat = [features.applyStat(a,statName) for a in blockTrain]
            featureLoL.append(feat)
            feat_test = features.applyStat(blockTest,statName)
            feature_test.append(feat_test)
        else:
            for cx in range(ncell[0]):
                for cy in range(ncell[1]):
                    feat = [a[cx][cy] for a in blockTrain]
                    featureLoL.append(feat)
                    feat_test = blockTest[cx][cy]
                    feature_test.append(feat_test)

    # transpose feature LoL:
    featureLoL = map(list,zip(*featureLoL))
    
    dist_to_all = knn.distToAll(featureLoL, feature_test, 'Euclid_sq')
    # print(zip(categories,dist_to_all))
    neighbours = knn.nearestClass(dist_to_all,categories,K)
    print(neighbours)
    prediction = knn.majorityNeighbour(neighbours)
    # confidence
    confidence = float(sum(neighbour==prediction for neighbour in neighbours))/len(neighbours)
    return prediction, confidence

# test algorithm on training set
def accuracyTest_knn(ncell, K=5, featureList=['asymmLR','asymmUD','aymmROT'],equally=False):
    # ncell [m,n]: break images into m x n blocks
    # featureList: list of strings
    #
    # load list of categories
    category_list = list(Category.objects.values_list('category_name',flat=True))
    # load all bitmaps
    bitmaps = list(Drawing.objects.values_list('bitmap',flat=True))
    # load corresponding list of categories
    categories = list(Drawing.objects.values_list('category',flat=True))
    #
    if equally:
        # sample equal number of each category
        indices = sampling.sampleEqually(categories)
        bitmaps = [bitmaps[ii] for ii in indices]
        categories = [categories[ii] for ii in indices]

    # convert bitmap strings to lists of lists
    trainLoL = [features.strToListList(a) for a in bitmaps]
    # centre images
    trainLoL = [features.centreArray(a) for a in trainLoL]
    # compute cell-block counts
    blockTrain = [features.cellCount(a,ncell,relative=True) for a in trainLoL]
    # compute requested features and construct feature LoL for knn
    featureLoL = []
    for statName in featureList:
        if statName != 'cellCount':
            feat = [features.applyStat(a,statName) for a in blockTrain]
            featureLoL.append(feat)
        else:
            for cx in range(ncell[0]):
                for cy in range(ncell[1]):
                    feat = [a[cx][cy] for a in blockTrain]
                    featureLoL.append(feat)

    # transpose feature LoL:
    featureLoL = map(list,zip(*featureLoL))
    
    # perform leave-one-out test:
    predictions, confidences, score = knn.accuracyTest(featureLoL, categories, K=K, method='Euclid_sq')
    #print('K=%d: accuracy: %f' % (K,score))
    return predictions, categories, confidences, score

# fill in predictions for old drawings
def retroPredict_knn(ncell, K=5, \
        featureList=['asymmLR','asymmUD','aymmROT'],equally=False):
    # ncell [m,n]: break images into m x n blocks
    # featureList: list of strings
    #
    # load all bitmaps with missing prediction field
    test_bitmaps = list(Drawing.objects.filter(predicted='Default').values_list('bitmap',flat=True))
    # load list of category names
    category_list = list(Category.objects.values_list('category_name',flat=True))

    for test_bitmap_string in test_bitmaps:
        # load all bitmaps leaving out test_string
        bitmaps = list(Drawing.objects.exclude(bitmap=test_bitmap_string).values_list('bitmap',flat=True))
        # load corresponding list of categories leaving out test_string
        categories = list(Drawing.objects.exclude(bitmap=test_bitmap_string).values_list('category',flat=True))
        #
        if equally:
            # sample equal number of each category
            indices = sampling.sampleEqually(categories)
            bitmaps = [bitmaps[ii] for ii in indices]
            categories = [categories[ii] for ii in indices]
        #
        # convert bitmap strings to lists of lists
        trainLoL = [features.strToListList(a) for a in bitmaps]
        testLoL = features.strToListList(test_bitmap_string)
        #
        # centre images
        trainLoL = [features.centreArray(a) for a in trainLoL]
        testLoL = features.centreArray(testLoL)
        # compute cell-block counts
        blockTrain = [features.cellCount(a,ncell,relative=True) for a in trainLoL]
        blockTest = features.cellCount(testLoL,ncell,relative=True)
        # compute requested features and construct feature LoL for knn
        featureLoL = []
        feature_test = []
        for statName in featureList:
            if statName != 'cellCount':
                feat = [features.applyStat(a,statName) for a in blockTrain]
                featureLoL.append(feat)
                feat_test = features.applyStat(blockTest,statName)
                feature_test.append(feat_test)
            else:
                for cx in range(ncell[0]):
                    for cy in range(ncell[1]):
                        feat = [a[cx][cy] for a in blockTrain]
                        featureLoL.append(feat)
                        feat_test = blockTest[cx][cy]
                        feature_test.append(feat_test)

        # transpose feature LoL:
        featureLoL = map(list,zip(*featureLoL))
        
        dist_to_all = knn.distToAll(featureLoL, feature_test, 'Euclid_sq')
        # print(zip(categories,dist_to_all))
        neighbours = knn.nearestClass(dist_to_all,categories,K)
        print(neighbours)
        prediction = knn.majorityNeighbour(neighbours)

        # update database with prediction
        d = Drawing.objects.get(bitmap=test_bitmap_string)
        d.predicted = prediction
        d.save()

