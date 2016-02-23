from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

from .models import Category, Drawing
from prepictors import features
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

    prediction, confidence = predict_knn(image_string,[5,5], K=9,\
            featureList=['asymmLR','asymmUD','asymmROT','cellCount'])

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

    context = {
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
    else:
        iwasright = False
    # print(selected_choice)
    image_string = request.POST['imageDataHidden']
    draw_date = timezone.now()
    # if drawing is new, update database
    all_the_category = Drawing.objects.filter(category=selected_choice).values_list('bitmap',flat=True)
    if image_string not in all_the_category:
        d = Drawing(bitmap=image_string, category=selected_choice, draw_date=draw_date)
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

# statistics
def statPlots(request):
    ncell = [5,5]
    category_list = list(Category.objects.values_list('category_name',flat=True))

    '''
    # test algorithm on training set
    print('accuracy test over training set:')
    for KK in range(3,6):
        predictions, categories, confidences, score = \
                accuracyTest_knn(ncell, K=KK, featureList=['asymmLR','asymmUD','asymmROT','cellCount'])
        # accuracy by category:
        for category in category_list:
            correct = sum(predictions[ii] == cat for ii,cat in enumerate(categories) if cat==category)
            incorrect = sum(predictions[ii] != cat for ii,cat in enumerate(categories) if cat==category)
            mean_conf = sum(confidences[ii] for ii,cat in enumerate(categories) if cat==category)
            mean_conf /= (correct + incorrect) 
            print('category: %s . . . %d out of %d -- acc %f, mean_conf %f' \
                    % (category,correct,incorrect+correct,float(correct)/(correct+incorrect),mean_conf))
        print('K: %d, accuracy: %f' % (KK,score))
    '''

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

###########################################
# methods for prediction
def predict_knn(test_bitmap_string, ncell, K=5, featureList=['asymmLR','asymmUD','asymmROT']):
    # ncell [m,n]: break images into m x n blocks
    # featureList: list of strings
    #
    # load all bitmaps
    bitmaps = list(Drawing.objects.values_list('bitmap',flat=True))
    # convert bitmap strings to lists of lists
    trainLoL = [features.strToListList(a) for a in bitmaps]
    testLoL = features.strToListList(test_bitmap_string)
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
    
    # load list of categories from Drawing table
    categories = list(Drawing.objects.values_list('category',flat=True))

    dist_to_all = knn.distToAll(featureLoL, feature_test, 'Euclid_sq')
    # print(zip(categories,dist_to_all))
    neighbours = knn.nearestClass(dist_to_all,categories,K)
    print(neighbours)
    prediction = knn.majorityNeighbour(neighbours)
    # confidence
    confidence = float(sum(neighbour==prediction for neighbour in neighbours))/len(neighbours)
    return prediction, confidence

# test algorithm on training set
def accuracyTest_knn(ncell, K=5, featureList=['asymmLR','asymmUD','aymmROT']):
    # ncell [m,n]: break images into m x n blocks
    # featureList: list of strings
    #
    # load list of categories
    category_list = list(Category.objects.values_list('category_name',flat=True))
    # load all bitmaps
    bitmaps = list(Drawing.objects.values_list('bitmap',flat=True))
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
    
    # load list of categories from Drawing table
    categories = list(Drawing.objects.values_list('category',flat=True))

    # perform leave-one-out test:
    predictions, confidences, score = knn.accuracyTest(featureLoL, categories, K=K, method='Euclid_sq')
    #print('K=%d: accuracy: %f' % (K,score))
    return predictions, categories, confidences, score

