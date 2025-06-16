# coding:utf-8
"""TourRecSys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import re_path
from django.contrib import admin
from tour import views

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),

    # 首页
    re_path(r'^init', views.init),
    re_path(r'^$', views.init),

    # 详情
    re_path(r'^detail', views.detail),

    # login & register & logout登录、注册、退出登录
    re_path(r'^login', views.sign_in),
    re_path(r'^register', views.register),
    re_path(r'^logout', views.sign_out),

    # 搜索
    re_path(r'^search', views.search),

    # 收藏
    re_path(r'^collection', views.collection),

    # personal info个人信息
    re_path(r'^info', views.info),
    re_path(r'^tinit', views.tinit),
    re_path(r'^tdetail', views.tdetail),
]
