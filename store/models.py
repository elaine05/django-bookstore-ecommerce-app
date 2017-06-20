from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.

class Author(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s, %s" % (self.first_name, self.last_name)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author)
    description = models.TextField()
    publish_date = models.DateTimeField(default=timezone.now)
    price = models.DecimalField(decimal_places=2, max_digits=8)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Review(models.Model):
    book = models.ForeignKey(Book)
    user = models.ForeignKey(User)
    publish_date = models.DateField(default=timezone.now)
    text = models.TextField()
