import requests
import json
from datetime import datetime, timedelta
from ..api.restarant import get_restaurants_for_city
from ..api.gaotie import query_high_speed_rail
from ..api.hotel_ai import query_hotels

# API Keys
API2D_API_KEY = "fk232710-06FfAYSSi0OAiwZFSYNonlskE262jhV3"
API2D_API_URL = "https://openai.api2d.net/v1/chat/completions"
GAODE_API_KEY = 'bf46eb2481a85735a6421b4044bc8804'


def normalize_json(result):
    """
    补全和标准化返回的 JSON 数据结构
    """
    required_keys = {
        "行程概览": {
            "出发地": "",
            "目的地": "",
            "总天数": 0,
            "开始日期": "",
            "结束日期": ""
        },
        "每日行程": [],
        "预算分配": {
            "交通": "",
            "住宿": "",
            "餐饮": "",
            "景点": "",
            "其他": ""
        },
        "旅行建议": []
    }

    def deep_merge(default, data):
        if isinstance(default, dict):
            for key in default:
                if key not in data:
                    data[key] = default[key]
                elif isinstance(default[key], dict):
                    data[key] = deep_merge(default[key], data.get(key, {}))
        return data

    return deep_merge(required_keys, result)


def generate_travel_plan(departure, destination, num_people, preferences, budget,
                         travel_date, duration_days, food_preferences, scenic_spots, hotel_type):
    headers = {
        "Authorization": f"Bearer {API2D_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        start_date = datetime.strptime(travel_date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=duration_days - 1)
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

    hotels_data = query_hotels(GAODE_API_KEY, destination, scenic_spots, hotel_type)
    hotels_json = json.dumps(hotels_data, ensure_ascii=False, indent=2)

    trains_data = query_high_speed_rail(API2D_API_KEY, departure, destination, travel_date)
    trains_json = json.dumps(trains_data, ensure_ascii=False, indent=2)

    restaurants_data = get_restaurants_for_city(destination, food_preferences)
    restaurants_json = json.dumps(restaurants_data, ensure_ascii=False, indent=2)

    prompt = f"""
你是一位旅行规划专家。请根据以下用户信息，结合提供的酒店、高铁和餐厅真实数据，生成一份**严格遵守格式**的JSON格式旅行计划。

仅返回 JSON 格式，结构如下（请严格遵循）：

{{
  "行程概览": {{
    "出发地": "...",
    "目的地": "...",
    "总天数": {duration_days},
    "开始日期": "{travel_date}",
    "结束日期": "{end_date.strftime('%Y-%m-%d')}"
  }},
  "每日行程": [
    {{
      "日期": "...",
      "行程安排": ["...", "..."],
      "用餐推荐": ["...", "..."],
      "交通方式": "...",
      "住宿": {{
          "酒店名称": "...",
          "地址": "...",
       }}
    }}
  ],
  "预算分配": {{
    "交通": "...",
    "住宿": "...",
    "餐饮": "...",
    "景点": "...",
    "其他": "..."
  }},
  "旅行建议": ["...", "..."]
}}

用户信息如下：
{json.dumps(user_info, ensure_ascii=False)}

酒店信息：
{hotels_json}

高铁信息：
{trains_json}

餐厅信息：
{restaurants_json}
    """

    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "你是一位专业的旅行助手，擅长按严格格式生成结构化旅行计划"},
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
        clean_str = content.strip()
        if clean_str.startswith("```json"):
            clean_str = clean_str[7:-3].strip()
        result = json.loads(clean_str)
        return normalize_json(result)
    except (KeyError, json.JSONDecodeError):
        print("返回内容不是合法 JSON：")
        print(response.text)
        return None
