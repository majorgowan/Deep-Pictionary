from django.urls import path

from . import views

app_name = 'drawing'
urlpatterns = [
    path('', views.chooseCategory, name='chooseCategory'),
    path('choose/', views.chooseCategory, name='chooseCategory'),
    path('drawingPad/', views.drawingPad, name='drawingPad'),
    path('redict/', views.predictCategory, name='predictCategory'),
    path('indicate/', views.indicateCategory, name='indicateCategory'),
    path('record/', views.recordCategory, name='recordCategory'),
    path('browse/', views.browse, name='browse'),
    path('statPlots/', views.statPlots, name='statPlots'),
    path('statTests/', views.statTests, name='statTests'),
    path('silly/', views.silly, name='silly'),
]


