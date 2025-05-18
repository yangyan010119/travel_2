"""
URL configuration for travelplan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from app01 import views

urlpatterns = [
	path('admin/', admin.site.urls), #admin 控制界面路由
	path('index/',views.index),
    path('', views.home),  # 设置首页路由

	path('register/', views.register,name='register'),
	path('login/', views.login,name='login'),
	path('travel_info/<int:travel_id>/', views.travel_info, name='travel_info'),
	path('add_travel_info/<int:user_id>/', views.add_travel_info, name='add_travel_info'),
	path('submit_feedback/<int:travel_info_id>/', views.submit_feedback, name='submit_feedback'),
	# 生成旅行计划
	# 用来显示旅行表单页面
	path('show_trip_form/', views.show_trip_form, name='show_trip_form'),  # 用户访问根路径时显示表单页面
	path('generate_trip/', views.generate_trip, name='generate_trip'),
	path('user/', views.user_page, name='user_page'),
	path('dashboard/', views.travel_dashboard, name='travel_dashboard'),
	path('get_scenic_spots/', views.get_scenic_spots, name='get_scenic_spots'),
]

