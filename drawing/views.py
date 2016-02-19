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

    prediction, confidence = predict_knn(image_string,[2,2], \
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
    selected_choice = request.POST['submit']
    if selected_choice == 'Yes!!!':
        iwasright = True
        selected_choice = request.POST['selected']
    else:
        iwasright = False
    print(selected_choice)
    image_string = request.POST['imageDataHidden']
    draw_date = timezone.now()
    # if drawing is new, update database
    all_the_category = Drawing.objects.filter(category=selected_choice).values_list('bitmap',flat=True)
    if image_string not in all_the_category:
        d = Drawing(bitmap=image_string, category=selected_choice, draw_date=draw_date)
        d.save()
    else:
        print('already have that one, mate!')
    # collect last 9 of the same category 
    last_9 = list(Drawing.objects.filter(category=selected_choice).order_by('-draw_date')[1:10].values_list('bitmap',flat=True))
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

# methods for prediction
def predict_knn(test_bitmap_string, ncell, featureList=['asymmLR','asymmUD','asymmROT']):
    # ncell [m,n]: break images into m x n blocks
    # featureList: list of strings
    #
    # load all bitmaps
    bitmaps = list(Drawing.objects.values_list('bitmap',flat=True))
    # convert bitmap strings to lists of lists
    trainLoL = [features.strToListList(a) for a in bitmaps]
    testLoL = features.strToListList(test_bitmap_string)
    # compute cell-block counts
    blockTrain = [features.cellCount(a,ncell) for a in trainLoL]
    blockTest = features.cellCount(testLoL)
    # compute requested features and construct feature LoL for knn
    featureLoL = []
    feature_test = []
    if 'asymmLR' in featureList:
        feat = [features.asymmLR(a) for a in blockTrain]
        featureLoL.append(feat)
        feat_test = features.asymmLR(blockTest)
        feature_test.append(feat_test)
    if 'asymmUD' in featureList:
        feat = [features.asymmUD(a) for a in blockTrain]
        featureLoL.append(feat)
        feat_test = features.asymmUD(blockTest)
        feature_test.append(feat_test)
    if 'asymmROT' in featureList:
        feat = [features.asymmROT(a) for a in blockTrain]
        featureLoL.append(feat)
        feat_test = features.asymmROT(blockTest)
        feature_test.append(feat_test)
    if 'cellCount' in featureList:
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
    #print(zip(categories,dist_to_all))
    neighbours = knn.nearestClass(dist_to_all,categories,K=5)
    print(neighbours)
    prediction = knn.majorityNeighbour(neighbours)
    # confidence
    confidence = float(sum(neighbour==prediction for neighbour in neighbours))/len(neighbours)
    return prediction, confidence
