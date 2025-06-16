# coding:utf-8
import sys
sys.path.append("I:\pycharmproject\TourRecSys")
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
#from tour.Spiders.MySQlHelper import MySQLHelper
import requests

import time
import re
import os

from tour.Spiders.MySQlHelper import MySQLHelper


class Spider:
    def __init__(self):
        self.headers = {
            'Host': 'travel.qunar.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0'}
        #self.engine = MySQLHelper.create_engine('root:root@39.108.141.110:3306/tour')
        self.engine = MySQLHelper.create_engine('root:admin@127.0.0.1:3306/tour')

    def send_request(self, url):
        response = requests.get(url, headers=self.headers)
        response.encoding = 'utf-8'
        html = response.content

        return BeautifulSoup(html, 'lxml')

    def download_img(self, path_prefix, urls):
        for idx, url in enumerate(urls):
            if idx > 3:
                break  # 最多只存储4张图片

            img_path = 'Spiders/imgs/' + path_prefix + '_{idx}.png'.format(idx=idx + 1)
            if os.path.exists(img_path):
                continue
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0'}
            res = requests.get(url, headers=headers)
            Image.open(BytesIO(res.content)).save(img_path)
            time.sleep(1)

    def save(self, data):
        try:
            MySQLHelper.insert_many('tour_view', data, self.engine, conflict='ignore')
        except Exception as e:
            print(e)
            time.sleep(20)
            self.engine = MySQLHelper.create_engine('root:admin@127.0.0.1:3306/tour')
            self.save(data)


    def catch_by_city(self):

        area_str = '华南华中'
        province = '河南'
        city = '洛阳'
        city_url = 'https://travel.qunar.com/p-cs299788-luoyang'
        city_pinyin, views = self.get_view(city_url)

        count = 0
        for view_name, view_url in list(views.items()):

            count += 1
            if count > 8:
                break  # 景点不超过8个

            pinyin, view_desc, img_url, view_rate, advise_time = self.view_info(view_url)

            if not img_url:
                continue

            view_id = city_pinyin + '_' + pinyin

            data = {}
            data['id'] = view_id
            data['area'] = area_str
            data['province'] = province
            data['city'] = city
            data['view_name'] = view_name
            data['view_desc'] = view_desc
            data['view_rate'] = view_rate
            data['advise_time'] = advise_time

            # 插入数据
            self.save([data])

            # 下载图片
            self.download_img(view_id, img_url)
            print(province, view_id, view_name)
            time.sleep(2)
            print('*' * 20)

    def get_view(self, url):
        obj = self.send_request(url)

        city_pinyin = url.split('-')[-1]  # 城市拼音

        data = {}
        for row in obj.find('dl', class_='line clrfix').find_all('dd'):
            view = row.a.get_text()  # 景点  view
            view_url = row.a.attrs['href']  # 景点信息链接
            data[view] = view_url

        return city_pinyin, data

    def view_info(self, url):
        obj = self.send_request(url)

        pinyin = url.split('-')[-1]  # 景点拼音
        if not obj.find('div', id='detail_box'):
            return pinyin, [], [], [], []

        text_lst = obj.find('div', id='detail_box').find('div', class_='b_detail_summary').text.split()
        view_desc = max(text_lst, key=len)  # 景点描述信息 获取句子最长单词

        if obj.find('div', id='idTransformView'):
            img_url = [img.attrs['src'] for img in obj.find('div', id='idTransformView').find_all('img')]  # 景点部分图片 img
        else:
            img_url = []

        view_rate = obj.find('span', class_='cur_score').get_text()  # 景点评分

        if obj.find('div', class_='time'):
            advise_time = obj.find('div', class_='time').get_text()
        else:
            advise_time = ''

        return pinyin, view_desc, img_url, view_rate, advise_time


if __name__ == '__main__':
    Spider().catch_by_city()
