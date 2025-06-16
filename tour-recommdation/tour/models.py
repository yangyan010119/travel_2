# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class View(models.Model):
    id = models.CharField(max_length=50, primary_key=True)  # city_pinyin + '_' + view_pinyin
    area = models.CharField(max_length=20)  # 景点地区
    province = models.CharField(max_length=20)  # 省份
    city = models.CharField(max_length=20)  # 城市
    view_name = models.CharField(max_length=25)  # 景点名称
    view_desc = models.TextField()  # 景点描述信息
    view_rate = models.CharField(max_length=5)  # 景点打分（去哪儿网系统评分）
    advise_time = models.CharField(max_length=20)  # 建议游玩时间

    def __unicode__(self):
        return  self.province + '-' + self.city + '-' +self.view_name


class ExtUser(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    number = models.IntegerField(primary_key=True)
    age = models.IntegerField(blank=True, null=True)
    sex = models.CharField(max_length=2, blank=True, null=True)
    address = models.CharField(max_length=30, blank=True, null=True)

    register_date = models.DateField(auto_now=True)

    def __unicode__(self):
        return self.user.username


class Comment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    view = models.ForeignKey(View,on_delete=models.CASCADE)
    comment = models.CharField(max_length=255, blank=True)
    comment_date = models.DateTimeField(blank=True, auto_now=True)

    def __unicode__(self):
        return self.user.username


class Score(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    view = models.ForeignKey(View,on_delete=models.CASCADE)
    rate = models.IntegerField(default=0)
    comment_date = models.DateTimeField(blank=True, auto_now=True)

    def __unicode__(self):
        return self.user.username


class Collection(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    view = models.ForeignKey(View,on_delete=models.CASCADE)
    collection_date = models.DateTimeField(blank=True, auto_now=True)

    def __unicode__(self):
        return self.user.username


##旅游计划推荐

class Tview(models.Model):
    tid = models.CharField(max_length=50, primary_key=True)
    tview_from = models.CharField(max_length=25)
    tview_journey = models.TextField()
    tview_rate = models.FloatField(default=0.0)
    tview_to = models.CharField(max_length=25)
    tview_day = models.CharField(max_length=25)
    def __unicode__(self):
        return  self.tview_from+'-'+ self.tview_to





class Tcomment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    view = models.ForeignKey(View,on_delete=models.CASCADE)
    comment = models.CharField(max_length=255, blank=True)
    comment_date = models.DateTimeField(blank=True, auto_now=True)

    def __unicode__(self):
        return self.user.username


class Tscore(models.Model):
    tuser = models.ForeignKey(User,on_delete=models.CASCADE)
    tview = models.ForeignKey(View,on_delete=models.CASCADE)
    trate = models.FloatField(default=0.0)
    tcomment_date = models.DateTimeField(blank=True, auto_now=True)

    def __unicode__(self):
        return self.tuser.username


class Tcollection(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    view = models.ForeignKey(View,on_delete=models.CASCADE)
    collection_date = models.DateTimeField(blank=True, auto_now=True)

    def __unicode__(self):
        return self.user.username