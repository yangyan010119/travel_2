# -*- coding: utf-8 -*-


from django.contrib import admin
from .models import *
class ViewAdmin(admin.ModelAdmin):
    list_display = ['city', 'view_name']
class ExtUserAdmin(admin.ModelAdmin):
    list_display = ['user']
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'view']
class ScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'view']
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'view']
# Register your models here.
admin.site.register(View,ViewAdmin)
admin.site.register(ExtUser,ExtUserAdmin)
admin.site.register(Comment,CommentAdmin)
admin.site.register(Score,ScoreAdmin)
admin.site.register(Collection,CollectionAdmin)