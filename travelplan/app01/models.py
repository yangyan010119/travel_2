from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
#用户表
class User(models.Model):
    id = models.AutoField('序号', primary_key=True)
    username = models.CharField('用户名', max_length=32)
    password = models.CharField('密码', max_length=32)
    email = models.EmailField('邮箱')
    mobile = models.CharField(max_length=11)
#用户旅行信息表
class TravelInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='travel_info')  # 外键，关联用户表
    destination = models.CharField(max_length=255)  # 目的地
    travel_start_date = models.DateField()  # 旅行开始日期
    travel_end_date = models.DateField()  # 旅行结束日期
    favorite_scenic_type = models.CharField(max_length=255)  # 喜欢的旅行景点类型
    travel_companion = models.CharField(max_length=255, blank=True, null=True)  # 旅行同伴，可以是逗号分隔的名字
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # 预算，默认值为 0
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    updated_at = models.DateTimeField(auto_now=True)  # 更新时间

    def __str__(self):
        return f"Travel to {self.destination} by {self.user.username}"

from django.db import models
class Feedback(models.Model):
    travel_info = models.ForeignKey('TravelInfo', on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    reviewed = models.BooleanField(default=False)
    approved = models.BooleanField(default=True)
    review_reason = models.CharField(max_length=255, null=True, blank=True)
    sentiment = models.CharField(max_length=20, null=True, blank=True)  # positive/neutral/negative
    quality_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"反馈: {self.travel_info.destination} - {self.rating or '未评分'}星"
