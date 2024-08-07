from django.db import models

# Create your models here.

class theme(models.Model):
    name=models.CharField(max_length=255)
    description=models.TextField()
    color=models.JSONField(null=True,blank=True)
    category=models.ForeignKey('category',on_delete=models.SET_NULL,null=True)
    def __str__(self) -> str:
        return self.name
    
class category(models.Model):
    title=models.CharField(max_length=255)
    description=models.TextField(null=True,blank=True)
    main_category=models.ForeignKey('self',on_delete=models.SET_NULL,null=True,default=None,blank=True)
    def __str__(self) -> str:
        return self.title
    

    

    
    