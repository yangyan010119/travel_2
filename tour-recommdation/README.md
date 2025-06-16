# Tour System

#### 介绍
本旅游推荐系统通过抓取去哪网旅游景点数据，并将数据存储至mysql数据库之中,然后通过机器学习的方式对景点数据（包含景点介绍、评论文本）进行分析聚类，形成数据模型，最后通过一个web网站的形式，向用户推荐其感兴趣的旅游景点。

#### 软件架构
1. python3.10 — 基础开发语言
2. django — 网站框架
3. 网络爬虫 — 获取景点数据
4. mysql — 存储数据
5. 机器学习（贝叶斯模型）


#### 安装教程

1.  安装python3.10
2.  安装pip
> sudo apt-get install python pip
> 
> sudo pip install --upgrade pip
3.  安装mysql > 注意mysql的默认密码设置为admin,免得更改源代码
> sudo apt-get install mysql-server
> 
> sudo apt-get install mysql-client
4. 安装其他依赖
> sudo pip install django requests uniout bs4 image pandas lxml

#### 使用说明

1. 首先生成数据库
> CREATE DATABASE `tour` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
2. 生成数据表
> python manager.py migrate
3. 运行爬虫获取网络数据
> python tour/Spider/spider.py
4. 运行网站
> python manage.py runserver
> 
> 访问网站: 127.0.0.1:8000

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


#### 特技

1.  使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2.  Gitee 官方博客 [blog.gitee.com](https://blog.gitee.com)
3.  你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解 Gitee 上的优秀开源项目
4.  [GVP](https://gitee.com/gvp) 全称是 Gitee 最有价值开源项目，是综合评定出的优秀开源项目
5.  Gitee 官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6.  Gitee 封面人物是一档用来展示 Gitee 会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)
