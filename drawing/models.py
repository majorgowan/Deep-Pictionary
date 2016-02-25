from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Drawing(models.Model):
    bitmap = models.CharField(max_length=900)
    category = models.CharField(max_length=20)
    predicted = models.CharField(max_length=20)
    draw_date = models.DateTimeField('date of drawing')

    def __str__(self):
        return self.category + ' ' + str(self.draw_date)

class Category(models.Model):
    category_name = models.CharField(max_length=20)

    def __str__(self):
        return self.category_name

