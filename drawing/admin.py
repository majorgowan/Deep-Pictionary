from django.contrib import admin

# Register your models here.
from .models import Drawing, Category

admin.site.register([Drawing, Category])
