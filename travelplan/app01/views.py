from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET

from .models import User
from django.shortcuts import render, get_object_or_404, redirect
from .models import TravelInfo
from .forms import TravelInfoForm
from django.http import JsonResponse
from .models import TravelInfo
from .utils import generate_travel_plan  # 假设你把上面函数放在 utils.py 中
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Feedback
from django.db.models import Q
from datetime import timedelta

def index(request):
	return HttpResponse("<h1>Hello world</h1>")
def home(request):
    return HttpResponse("欢迎来到 Django 首页！")

#注册功能实现
# 注册功能实现
def register(request):
    error_message = None

    if request.method == "POST":
        print("表单数据：", request.POST)
        username = request.POST.get("username")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        confirm_password = request.POST.get('confirm_password')

        """
        # 验证密码一致性
        if password != confirm_password:
            error_message = "两次密码输入不一致"
        """
        # 验证用户是否已存在(根据主键来)
        if User.objects.filter(username=username).exists():
            error_message = "Account already exists"
        # 保存到数据库
        else:
            User.objects.create(
                username=username,
			    password=password,  # 后面可以加密
			    email=email,
			    mobile=mobile
		    )
            # print("用户创建成功：", user)
            return redirect("/login/")  # 注册成功跳转到登录

    return render(request, "app01/register.html",{'error_message': error_message})

#登陆功能实现
def login(request):
    error_message = None

    if request.method == "POST":
        # 输入的账号必须唯一，username如果可重复则需要改成手机号或邮箱号登录
        username = request.POST.get("username")
        password = request.POST.get("password")

        # 先查询用户名是否存在
        try:
            user = User.objects.get(username=username)
            if user.password == password:
                # 设置session
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                return redirect('user_page')
            else:
                error_message = "Password ERROR"
        except User.DoesNotExist:
            error_message = "User not exist"
        """
        user = User.objects.filter(username=username, password=password).first()
        if user:
            return redirect('user_page')
        elif User.objects.filter(mobile=username).exists():
            error_message = "Invalid credentials. Please try again."
        """
    return render(request, "app01/login.html",{'error_message': error_message})

def user_page(request):
    # 检查登录状态
    if 'user_id' not in request.session:
        return redirect('login')

    try:
        # 获取用户信息
        user = User.objects.get(id=request.session['user_id'])
        context = {
            'username': user.username,
            'email': user.email,
            'mobile': user.mobile,
        }
        return render(request, 'app01/user.html', context)

    except User.DoesNotExist:
        # 用户不存在则清除session
        request.session.flush()
        return redirect('login')

def travel_dashboard(request):
    # 检查登录状态
    if 'user_id' not in request.session:
        return redirect('login')

    # 获取用户对象
    user = get_object_or_404(User, id=request.session['user_id'])

    # 处理表单提交逻辑（后续可以扩展）
    if request.method == 'POST':
        # 这里可以添加处理偏好设置表单的逻辑
        pass

    return render(request, 'app01/traveldashboard.html', {'user': user})

# 显示旅游信息
def travel_info(request, travel_id):
    travel = get_object_or_404(TravelInfo, id=travel_id)
    return render(request, 'app01/travel_info.html', {'travel': travel})

# 添加旅行计划，通过输入信息，调用API接口，生成计划
def add_travel_info(request, user_id):
    if request.method == 'POST':
        form = TravelInfoForm(request.POST)
        # -------------------------------------
        if form.is_valid():
            travel_info = form.save(commit=False)
            travel_info.user_id = user_id
            travel_info.save()

            # 测试查询相似旅行反馈,筛选出一些反馈好让chat生成计划时注意事项
            # -------------------------------------
            # 计算日期范围（1个月以内）
            one_month_before_start = travel_info.travel_start_date - timedelta(days=30)
            one_month_after_end = travel_info.travel_end_date + timedelta(days=30)
            # # 查找符合条件的 travelinfo 记录
            similar_travels = TravelInfo.objects.filter(
                Q(destination=travel_info.destination) &
                Q(travel_companion=travel_info.travel_companion) &
                Q(budget__range=(travel_info.budget - 1000, travel_info.budget + 1000)) &
                Q(travel_start_date__gte=one_month_before_start) &
                Q(travel_end_date__lte=one_month_after_end)
            )
            # 获取这些 travelinfo 对应的 feedback 中评分最低的前5条评论
            feedbacks = Feedback.objects.filter(travel_info__in=similar_travels).order_by('rating').values_list('comment', flat=True)[:5]
            print(feedbacks)
            # 使用 utils 中封装好的函数
            try:
                plan_text = generate_travel_plan(travel_info,feedbacks)
            except Exception as e:
                plan_text = f"生成计划时发生错误：{str(e)}"
            # 跳转至旅行计划安排界面
            return render(request, 'app01/travel_plan_result.html', {
                'travel_info': travel_info,
                'plan_text': plan_text,
            })

    else:
        form = TravelInfoForm()
    # 跳转至新添旅行信息界面，在该界面用户可以输入信息，点击生成计划按钮
    return render(request, 'app01/add_travel_info.html', {'form': form})

def get_travel_plan(request, travel_id):
    travel = TravelInfo.objects.get(id=travel_id)
    plan = generate_travel_plan(travel)
    return JsonResponse({'plan': plan})

# 计划生成好后，用户提交反馈
# @csrf_exempt
# def submit_feedback(request, travel_info_id):
#     if request.method == "POST":
#         # 提交评星和建议反馈
#         rating = request.POST.get("rating")
#         comment = request.POST.get("comment")
#         Feedback.objects.create(
#             travel_info_id=travel_info_id,
#             rating=int(rating) if rating else None,
#             comment=comment
#         )
#         return HttpResponse("感谢你的反馈！")
#     # 返回旅行计划结果界面
#     return redirect("travel_plan_result")

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404
from .models import Feedback, TravelInfo
from .utils import auto_review_feedback

def submit_feedback(request, travel_info_id):
    if request.method != "POST":
        return redirect("travel_plan_result")

    # 确认 travel_info 存在
    travel_info = get_object_or_404(TravelInfo, pk=travel_info_id)

    rating = request.POST.get("rating")
    comment = request.POST.get("comment", "").strip()

    # 简单校验：评论不能为空
    if not comment:
        return HttpResponseBadRequest("评论内容不能为空。")

    # 先创建，但不马上 save() 到数据库
    feedback = Feedback(
        travel_info=travel_info,
        rating=int(rating) if rating else None,
        comment=comment
    )

    # 自动审核（在内部会设置 feedback.reviewed 和 feedback.approved）
    feedback = auto_review_feedback(feedback)

    # 只有审核通过的才保存
    if feedback.approved:
        feedback.save()
        return HttpResponse("感谢你的反馈！")
    else:
        # 如果需要，也可以记录未通过的原因：feedback.review_reason
        # feedback.save()  # 如果你想保留未通过的记录，可以打开这一行
        return HttpResponse("抱歉，你的评论未通过审核。")

# ----------------------------------------------------------------
# 根据城市名，生成景点列表
import requests
from django.http import JsonResponse

API2D_KEY = "fk232710-06FfAYSSi0OAiwZFSYNonlskE262jhV3"  # 替换成你的 API2D 密钥
API2D_URL = "https://openai.api2d.net/v1/chat/completions"

import requests
from django.http import JsonResponse

API2D_KEY = "fk232710-06FfAYSSi0OAiwZFSYNonlskE262jhV3"  # 替换成你的 API2D 密钥
API2D_URL = "https://openai.api2d.net/v1/chat/completions"

def get_scenic_spots(request):
    destination = request.GET.get('destination', '')
    print("destination:", destination)
    if not destination:
        return JsonResponse({'error': 'No destination provided'}, status=400)

    prompt = f"请列出中国{destination}最有代表性的10个旅游景点名称（仅名称），用逗号分隔返回。"

    headers = {
        "Authorization": f"Bearer {API2D_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        # 调用 API2D
        response = requests.post(API2D_URL, headers=headers, json=data)
        print("HTTP Status:", response.status_code)
        print("Response Text:", response.text)

        # 如果状态码为 401，直接返回
        if response.status_code == 401:
            return JsonResponse({'error': 'API key unauthorized or invalid'}, status=401)

        response.raise_for_status()
        reply = response.json()

        # 检查返回的内容格式
        if 'choices' not in reply or len(reply['choices']) == 0:
            return JsonResponse({'error': 'Unexpected API response format'}, status=500)

        content = reply['choices'][0]['message']['content']
        spots = [spot.strip() for spot in content.split(',') if spot.strip()]
        print("Parsed spots:", spots)

        return JsonResponse({'spots': spots})
    except Exception as e:
        print("Error during API call:", str(e))
        return JsonResponse({'error': f"Internal server error: {str(e)}"}, status=500)

#--------------------------------------------------------------------
# 旅行信息提交表单
def show_trip_form(request):
    return render(request, 'app01/generate_trip.html')

# 调用旅行计划生成，输入旅行要求，输出旅行计划
from django.shortcuts import render
from django.http import JsonResponse
from .agent.plan_agent import generate_travel_plan  # 假设你的函数在travel_service.py文件中
@require_GET
def generate_trip(request):
    # 获取请求中的参数
    departure = request.GET.get('departure', '西安')
    destination = request.GET.get('destination', '北京')
    num_people = int(request.GET.get('num_people', 2))
    preferences = request.GET.getlist('preferences', ['历史', '美食', '文化'])
    budget = request.GET.get('budget', '4000元')
    travel_date = request.GET.get('travel_date', '2025-07-10')
    duration_days = int(request.GET.get('duration_days', 3))
    food_preferences = request.GET.get('food_preferences', '中餐')
    scenic_spots = request.GET.getlist('scenic_spots', ['天安门', '故宫', '长城'])
    hotel_type = request.GET.getlist('hotel_type', ['快捷'])

    # 调用generate_travel_plan函数
    travel_plan = generate_travel_plan(
        departure=departure,
        destination=destination,
        num_people=num_people,
        preferences=preferences,
        budget=budget,
        travel_date=travel_date,
        duration_days=duration_days,
        food_preferences=food_preferences,
        scenic_spots=scenic_spots,
        hotel_type=hotel_type
    )
    # 返回 JSON 响应，明确指定编码

    is_dict = isinstance(travel_plan, dict)
    response = JsonResponse(travel_plan, safe=is_dict, json_dumps_params={"ensure_ascii": False})

    response["Content-Type"] = "application/json; charset=utf-8"
    return response



def get_display_feedback(travel_info_id):
    return Feedback.objects.filter(
        travel_info_id=travel_info_id,
        reviewed=True,
        approved=True,
        quality_score__gte=0.5  # 可设置门槛
    ).order_by('-quality_score', '-created_at')

