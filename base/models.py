from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
User=get_user_model()
from django.utils import timezone
class theme(models.Model):
    name=models.CharField(max_length=255)
    description=models.TextField()
    color=models.JSONField(null=True,blank=True)
    category=models.ForeignKey('category',on_delete=models.SET_NULL,null=True)
    href=models.CharField(max_length=255,unique=True)
    price=models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return self.name
class category(models.Model):
    title=models.CharField(max_length=255)
    href=models.CharField(max_length=255,unique=True)
    description=models.TextField(null=True,blank=True)
    main_category=models.ForeignKey('self',on_delete=models.SET_NULL,null=True,default=None,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return self.title
    
class comment(models.Model):
    body = models.TextField()
    theme=models.ForeignKey(theme,on_delete=models.CASCADE,related_name="comments")
    creator = models.ForeignKey(User,on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    answer=models.IntegerField(choices=((0,0),(1,1)),default=0)
    isAnswer=models.BooleanField(default=False)
    best_comment=models.BooleanField(default=False)
    SCORE_CHOICES=[
        (1,"one"),
        (2,"two"),
        (3,"three"),
        (4,"four"),
        (5,"five"),
    ]
    score=models.SmallIntegerField(choices=SCORE_CHOICES)
    mainCommentID=models.ForeignKey('self',null=True,blank=True,on_delete=models.CASCADE,related_name="replies")
    def __str__(self) -> str:
        return str(self.creator)


    

    

    
    