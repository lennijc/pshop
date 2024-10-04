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
    cover=models.ImageField(null=True,default=None,blank=True)
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
    
class Article(models.Model):
    title=models.CharField(max_length=255)
    description=models.TextField()
    body=models.TextField()
    cover=models.ImageField(upload_to="article_pics",null=True,default=None,blank=True)
    href=models.CharField(max_length=255,unique=True)
    category=models.ForeignKey(category,on_delete=models.PROTECT)
    creator=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    publish=models.BooleanField(default=False)
    def __str__(self) -> str:
        return self.title
    
class contact(models.Model):
    name=models.CharField(max_length=255)
    email= models.EmailField()
    phone=models.CharField(max_length=11,null=True)
    body=models.TextField()        
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    answer=models.BooleanField(default=False)
    def __str__(self):
        return self.name

class reservation(models.Model):
    color=models.JSONField(null=True,blank=True)
    theme=models.ForeignKey(theme,on_delete=models.SET_NULL,null=True)
    customer=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    date=models.DateField(null=True,blank=True)
    location=models.JSONField(null=True,blank=True)
    address=models.TextField(null=True,blank=True)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('unsuccessful', 'Unsuccessful'),
    )
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default=STATUS_CHOICES[0][0],
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    def __str__(self):
        return (str(self.date) if self.date is not None else "date:none") + " " + (str(self.address) if self.address is not None else "Address:none")
    
class Question(models.Model):
    question=models.TextField()
    answer=models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return str(self.question + self.answer)[:80]
    
class Banned_user(models.Model):
    phone = models.CharField(max_length=12, unique=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.phone