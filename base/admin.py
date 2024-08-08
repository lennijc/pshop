from django.contrib import admin
from . models import category,theme,comment
# Register your models here.

admin.site.register(category)
admin.site.register(theme)
admin.site.register(comment)