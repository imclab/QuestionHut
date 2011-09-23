from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserProfile(models.Model):
    user        =   models.OneToOneField(User)

class Tag(models.Model):
    title       =   models.CharField(max_length=200)

class Question(models.Model):
    author      =   models.ForeignKey(User)
    votes       =   models.IntegerField(default=0)
    views       =   models.IntegerField(default=0)
    title       =   models.CharField(max_length=200)
    content     =   models.TextField()
    created_at  =   models.DateTimeField(auto_now_add=True)
    tags        =   models.ManyToManyField(Tag)   
    
class Answer(models.Model):
    author      =   models.ForeignKey(User)
    content     =   models.TextField()
    votes       =   models.IntegerField(default=0)
    created_at  =   models.DateTimeField(auto_now_add=True)
    question    =   models.ForeignKey(Question, related_name='answers')
    