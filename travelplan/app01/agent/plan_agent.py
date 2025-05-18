import requests
import json
from datetime import datetime, timedelta
from ..api.restarant import get_restaurants_for_city
from ..api.gaotie import query_high_speed_rail
from ..api.hotel_ai import query_hotels
API2D_API_KEY = "fk232710-06FfAYSSi0OAiwZFSYNonlskE262jhV3"
API2D_API_URL = "https://openai.api2d.net/v1/chat/completions"
# 高德地图 API Key
API_KEY = 'bf46eb2481a85735a6421b4044bc8804'


def generate_travel_plan(departure, destination, num_people, preferences, budget, travel_date, duration_days,
                         food_preferences,scenic_spots,hotel_type):
    headers = {
        "Authorization": f"Bearer {API2D_API_KEY}",
        "Content-Type": "application/json"
    }

    # 生成日期列表
    try:
        start_date = datetime.strptime(travel_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("出发日期格式必须为 YYYY-MM-DD")

    user_info = {
        "出发地": departure,
        "目的地": destination,
        "人数": num_people,
        "喜好": preferences,
        "预算": budget,
        "出发日期": travel_date,
        "游玩天数": duration_days,
        "饮食喜好": food_preferences
    }

    # 将辅助数据转换为 JSON 字符串（为了 prompt 中可读）
    print("scenic_spots",scenic_spots)
    hotels_data = query_hotels(API_KEY,destination,scenic_spots,hotel_type)
    hotels_json = json.dumps(hotels_data, ensure_ascii=False, indent=2)
    print("hotels_json",hotels_json)
    trains_data = query_high_speed_rail(API2D_API_KEY,departure,destination,travel_date)
    trains_json = json.dumps(trains_data, ensure_ascii=False, indent=2)
    print("trains_json",trains_json)
    restaurants_data = get_restaurants_for_city(destination, food_preferences)
    restaurants_json = json.dumps(restaurants_data, ensure_ascii=False, indent=2)
    print("restaurants_json",restaurants_json)

    prompt = f"""
你是一位旅行规划专家。请根据以下用户信息，结合提供的酒店、高铁和餐厅真实数据，为用户生成一份实际可执行的旅行计划。返回格式为 JSON，格式必须是json字典类型，结构如下：

{{
  "行程概览": {{...}},
  "第1天": {{
    "日期": "...",
    "行程安排": ["...", "..."],
    "用餐推荐": ["...", "..."],
    "交通方式": "...",
    "住宿": "..."
  }},
  ...
  "预算分配": {{...}},
  "旅行建议": ["...", "..."]
}}

用户需求如下：
{json.dumps(user_info, ensure_ascii=False)}

以下是可选酒店信息（请根据地点和预算合理选择）：
{hotels_json}

以下是高铁车次信息（出发地与目的地之间）：
{trains_json}

以下是餐厅推荐信息（请根据用户喜好选择）：
{restaurants_json}
"""

    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "你是一位专业的旅行助手。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(API2D_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print("请求失败，状态码:", response.status_code)
        print("返回内容:", response.text)
        return None

    try:
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)
    except (KeyError, json.JSONDecodeError):
        print("返回内容不是合法 JSON：")
        print(response.text)
        return None

# 示例用法
# if __name__ == "__main__":
#     # 下面是 mock 的数据结构，可替换为你的实际 JSON 数据
#     travel_plan = generate_travel_plan(
#         departure="西安",
#         destination="北京",
#         num_people=2,
#         preferences=["历史", "美食", "文化"],
#         budget="4000元",
#         travel_date="2025-07-10",
#         duration_days=3,
#         food_preferences = "中餐",
#         scenic_spots=["天安门", "故宫", "长城"],
#         hotel_type = ["快捷"]
#
#
#     )
#
#     if travel_plan:
#         print("生成的旅行计划：")
#         print(json.dumps(travel_plan, ensure_ascii=False, indent=2))
