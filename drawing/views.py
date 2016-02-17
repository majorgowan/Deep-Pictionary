from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

from .models import Category, Drawing

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

def indicateCategory(request):
    category_list = list(Category.objects.values_list('category_name',flat=True))
    image_string = request.POST['imageDataHidden']
    print(image_string)

    context = {
            'category_list': category_list,
            'image_string': image_string,
            }
    return render(request, 'drawing/indicateCategory.html', context)

def recordCategory(request):
    selected_choice = request.POST['submit']
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
            'image_string': image_string,
            'last_9': last_9,
            }
    return render(request, 'drawing/recordCategory.html', context)

def drawingPad(request):
    return render(request, 'drawing/drawingPad.html')

