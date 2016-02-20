from django.conf.urls import url

from . import views

app_name = 'drawing'
urlpatterns = [
        url(r'^$', views.index, name='index'),
        url(r'^choose$', views.chooseCategory, name='chooseCategory'),
        url(r'^drawingPad$', views.drawingPad, name='drawingPad'),
        url(r'^predict$', views.predictCategory, name='predictCategory'),
        url(r'^indicate$', views.indicateCategory, name='indicateCategory'),
        url(r'^record$', views.recordCategory, name='recordCategory'),
        url(r'^statPlots$', views.statPlots, name='statPlots'),
        ]
