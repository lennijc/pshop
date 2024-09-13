from django.contrib import admin
from . models import category,theme,comment,Article,contact,reservation,Question
# Register your models here.

admin.site.register(category)
admin.site.register(theme)
admin.site.register(comment)
admin.site.register(Article)
admin.site.register(contact)
admin.site.register(reservation)
admin.site.register(Question)
