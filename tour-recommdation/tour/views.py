# coding:utf-8
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .algorithm import addr, ItemCF, UserCF
from tour.recomand import UserCf
from .models import *
import random
import json
from django.db.models import Avg
from tour.models import Tscore, Tview
from django.db.models.signals import pre_save, post_save

@login_required(login_url='/login')
def init(request):
    # 推荐处理，根据游客的评分进行推荐
    recProducts = []
    datas = {}
    for user in User.objects.all():
        score = Score.objects.filter(user_id=user.id)
        dict = {}
        for sco in score:
            dict[sco.view_id] = sco.rate
        datas[user.username] = dict
    print("datas是",datas)

    userCf = UserCf(data=datas)

    recommandList = userCf.recomand(request.user.username, 10)  # 推荐10条 推荐列表  request.session.get('username')
    print("最终推荐：",recommandList)
    gue=View.objects.none()
    for r in recommandList:
        tables = View.objects.none()
        s_tables = tables.none()
        print(r)

        pro =View.objects.get(id=r[0])
        #s_tables += tables.filter(id=r[0])
        #gue=gue + View.objects.filter(id=r[0])
        recProducts.append({'id': pro.id, 'name': pro.view_name})

    print('pro ',pro )
    #print('s_tables ', s_tables)
    print(recProducts)

    if request.method == 'GET':
        # 热门推荐 按评分排序

        hot = View.objects.order_by('view_rate')[::-1]

        # 随机推荐某一地区景点


        #rand = View.objects.order_by('?')[:10]
        #rand = View.objects.filter(city=u'北京').order_by('view_rate')[::-1]
        rand = View.objects.all()

        # 猜你喜欢
        guess = recProducts

        data = {
            'hot': hot,
            'rand': rand,
            'guess': guess
        }
        print('随机猜测rand:', rand)
        print('guess:' ,guess)

        return render(request, 'index.html', data)


@csrf_exempt
@login_required(login_url='/login')
def detail(request):
    if request.method == 'GET':
        view_id = request.GET.get('id', False)
        view = View.objects.filter(id=view_id).first()

        # 类似推荐
        sim = View.objects.filter(city=view.city)

        # 该景点的评论
        comments = Comment.objects.filter(view=view).order_by('comment_date')[::-1]

        # 评分统计
        score = Score.objects.filter(view=view)
        pn = len(score)
        rate = round(sum(int(s.rate) for s in score) * 1.0 / pn, 1) if pn else 0.0#一位数平均

        collection = Collection.objects.filter(view=view, user=request.user)

        data = {
            'view': view,
            'sim': sim,
            'pn': pn,
            'comments': comments,
            'rate': rate,
            'collection': collection
        }

        return render(request, 'detail.html', data)

    elif request.method == 'POST':
        comment = request.POST.get('text', False)
        view_id = request.POST.get('id', False)
        score = request.POST.get('score', False)
        collection = request.POST.get('collection', False)

        view = View.objects.get(id=view_id)

        msg = {
            'msg': '发生未知错误',
            'type': 'danger'
        }
        if comment:
            Comment.objects.create(user=request.user, view=view, comment=comment)
            msg['msg'] = '评论提交成功，页面即将刷新!'
            msg['type'] = 'success'

            return HttpResponse(json.dumps(msg), content_type='application/json')

        if score:
            score = int(score)
            s = Score.objects.filter(user=request.user, view=view)
            if s:
                s[0].rate = score
                s[0].save()
            else:
                Score.objects.create(user=request.user, view=view, rate=score)
            msg['msg'] = '感谢您的评分!'
            msg['type'] = 'success'
            return HttpResponse(json.dumps(msg), content_type='application/json')

        if collection:
            if collection == 'collection-true':
                Collection.objects.create(user=request.user, view=view)
                msg['msg'] = '收藏成功!'

            elif collection == 'collection-false':
                Collection.objects.filter(user=request.user, view=view).delete()
                msg['msg'] = '已取消收藏!'

            msg['type'] = 'success'
            return HttpResponse(json.dumps(msg), content_type='application/json')

        return HttpResponse(json.dumps(msg), content_type='application/json')


@csrf_exempt
def sign_in(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        pw = request.POST.get('pw', False)
        user = authenticate(username=username, password=pw)
        if user:
            login(request, user)
            return redirect('/')

    if request.method == 'GET':
        username = request.GET.get('username', False)
        pw = request.GET.get('pw', False)
        if not username or not pw:
            return render(request, 'login.html')
        user = authenticate(username=username, password=pw)
        msg = {
            'msg': '登录成功，页面正在跳转！',
            'type': 'success'
        }
        if not user:
            msg['msg'] = '账号或密码错误,请检查后重新登录!'
            msg['type'] = 'danger'
        return HttpResponse(json.dumps(msg), content_type='application/json')


@csrf_exempt
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        pw = request.POST.get('pw', False)
        email = request.POST.get('email', False)

        # 生成随机编号
        number = random.randint(1000000, 9999999)
        if not ExtUser.objects.filter(number=number):
            user = User.objects.create_user(username=username, password=pw, email=email)
            ExtUser.objects.create(user=user, number=number)
            user = authenticate(username=username, password=pw)
            login(request, user)
            return redirect('/')

    elif request.method == 'GET':
        username = request.GET.get('username', False)
        pw = request.GET.get('pw', False)
        rpw = request.GET.get('rpw', False)
        if not username or not pw:
            return render(request, 'register.html')
        msg = {
            'msg': '账号注册成功!',
            'type': 'success'
        }
        if not pw.isalnum():
            msg['msg'] = '密码只能由数字字母组成！'
            msg['type'] = 'danger'
        if pw != rpw:
            msg['msg'] = '两次输入的密码不一致！'
            msg['type'] = 'danger'
        if len(pw) < 6:
            msg['msg'] = '密码至少需要6个字符！'
            msg['type'] = 'danger'
        if User.objects.filter(username=username):
            msg['msg'] = '用户名已经存在！'
            msg['type'] = 'danger'

        return HttpResponse(json.dumps(msg), content_type='application/json')


def sign_out(request):
    logout(request)
    return redirect('/')


def search(request):
    if request.method == 'GET':
        word = request.GET.get('word', False)
        views = View.objects.filter(Q(province__contains=word) | Q(view_name__contains=word) | Q(city__contains=word))

        for v in views:
            score = Score.objects.filter(view=v)
            v.view_rate = sum(s.rate for s in score)*1.0/len(score) if score else 0

        return render(request, 'search.html', {'views': views})


@login_required(login_url='/login')
def collection(request):
    views = Collection.objects.filter(user=request.user)
    return render(request, 'collection.html', {'views': views})



@login_required(login_url='/login')
@csrf_exempt
def info(request):
    if request.method == 'GET':
        return render(request, 'info.html')
    elif request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        sex = request.POST.get('sex', False)
        age = request.POST.get('age', False)
        address = request.POST.get('address', False)

        user = request.user
        user.username = username
        if password:
            user.set_password(password)
        user.extuser.sex = sex
        user.extuser.age = age
        user.extuser.address = address
        user.extuser.save()
        user.save()

        return redirect('/login')

####计划推荐
#
@login_required(login_url='/login')
def tinit(request):
    # 推荐处理，根据游客的评分进行推荐
    recProducts = []
    datas = {}
    for user in User.objects.all():
        tscore = Tscore.objects.filter(tuser_id=user.id)
        dict = {}
        for tsco in tscore:
            dict[tsco.tview_id] = tsco.trate
        datas[user.username] = dict
    userCf = UserCf(data=datas)

    recommandList = userCf.recomand(request.user.username, 10)  # 推荐10条 推荐列表  request.session.get('username')
    gue=Tview.objects.none()
    for r in recommandList:
        tables = Tview.objects.none()
        s_tables = tables.none()
        print(r)

        pro =Tview.objects.get(tid=r[0])
        #s_tables += tables.filter(id=r[0])
        #gue=gue + View.objects.filter(id=r[0])
        recProducts.append({'tid': pro.tid, 'tview_from': pro.tview_from,'tview_to':pro.tview_to,'tview_day': pro.tview_day,'tview_rate':pro.tview_rate,'tview_journey':pro.tview_journey})


    if request.method == 'GET':
        # 热门推荐 按评分排序
        page = request.GET.get('page', 1)
        hot = Tview.objects.order_by('tview_rate')[::-1]
        hot_paginator = Paginator(hot, 10)
        hot = hot_paginator.get_page(page)
        # 随机推荐某一地区景点

        rand = Tview.objects.all()

        # 猜你喜欢
        guess = recProducts
        guess_paginator = Paginator(guess, 10)
        guess = guess_paginator.get_page(page)
        data = {
            'hot': hot,
            'rand': rand,
            'guess': guess
        }


        return render(request, 'index2.html', data)

@csrf_exempt
@login_required(login_url='/login')
def tdetail(request):
    if request.method == 'GET':
        tview_id = request.GET.get('id', False)
        tview = Tview.objects.filter(tid=tview_id).first()
        # 类似推荐
        sim = Tview.objects.filter(tview_to=tview.tview_to,tview_from=tview.tview_from).exclude(tid=tview_id)




        # 评分统计
        score = Tscore.objects.filter(tview_id=tview_id)
        tpn = len(score)
        trate = round(sum(s.trate for s in score) * 1.0 / tpn, 1) if tpn else 0.0#一位数平均


        data = {
            'tview': tview,
            'tsim': sim,
            'tpn': tpn,
            'trate': trate,
        }

        return render(request, 'detail2.html', data)

    elif request.method == 'POST':

        score = request.POST.get('score', False)
        tview_id = request.POST.get('tid', False)
        view = Tview.objects.get(tid=tview_id)

        msg = {
            'msg': '发生未知错误',
            'type': 'danger'
        }


        if score:
            score = float(score)
            s = Tscore.objects.filter(tuser_id=request.user.id, tview_id=tview_id)

            pre_save.connect(lambda sender, instance, **kwargs: print(f"PRE_SAVE: {instance.tview_rate}"),
                             sender=Tview)
            post_save.connect(lambda sender, instance, **kwargs: print(f"POST_SAVE: {instance.tview_rate}"),
                              sender=Tview)

            # 2. 强制更新并提交
            tw = Tview.objects.filter(tid=tview_id).first()

            if s:
                s[0].trate = score
                s[0].save()
                if tw:
                    score_f = Tscore.objects.filter(tview_id=tview_id)
                    tpn = len(score_f)
                    new_avg = round(sum(s.trate for s in score_f) * 1.0 / tpn, 1) if tpn else 0.0
                    tw.tview_rate = new_avg
                    tw.save(force_update=True)


            else:
                Tscore.objects.create(tuser_id=request.user.id, tview_id=tview_id, trate=score)
                if tw:
                    score_f = Tscore.objects.filter(tview_id=tview_id)
                    tpn = len(score_f)
                    new_avg = round(sum(s.trate for s in score_f) * 1.0 / tpn, 1) if tpn else 0.0
                    tw.tview_rate = new_avg
                    tw.save(force_update=True)
            msg['msg'] = '感谢您的评分!'
            msg['type'] = 'success'
            return HttpResponse(json.dumps(msg), content_type='application/json')



        return HttpResponse(json.dumps(msg), content_type='application/json')



