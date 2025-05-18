import requests

# 你的 Aviationstack API Key
API_KEY = "83d64663e1ebbff550610eb96e797f30"

# 常见城市与机场 IATA 映射（可自行扩展）
city_to_iata = {
    "北京": "PEK",
    "beijing": "PEK",
    "上海": "SHA",
    "shanghai": "SHA",
    "广州": "CAN",
    "guangzhou": "CAN",
    "深圳": "SZX",
    "shenzhen": "SZX",
    "西安": "XIY",
    "xian": "XIY",
    "成都": "CTU",
    "chengdu": "CTU",
    "伦敦": "LHR",
    "london": "LHR",
    "纽约": "JFK",
    "new york": "JFK",
    "东京": "HND",
    "tokyo": "HND",
    "巴黎": "CDG",
    "paris": "CDG"
}

def city_to_airport_code(city_name):
    city = city_name.strip().lower()
    return city_to_iata.get(city, None)

def get_flights_by_city(dep_city, arr_city, flight_date):
    dep_iata = city_to_airport_code(dep_city)
    arr_iata = city_to_airport_code(arr_city)

    if not dep_iata or not arr_iata:
        print(f"无法识别城市名称：{dep_city} 或 {arr_city}")
        return

    print(f"出发地 {dep_city} -> IATA: {dep_iata}")
    print(f"目的地 {arr_city} -> IATA: {arr_iata}")
    print(f"查询日期：{flight_date}")
    print("=" * 40)

    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": API_KEY,
        "dep_iata": dep_iata,
        "arr_iata": arr_iata,
        "flight_date": flight_date  # 加入日期参数
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("请求失败：", response.status_code)
        print(response.text)
        return

    flights = response.json().get("data", [])
    if not flights:
        print("未找到航班数据")
        return

    for flight in flights[:10]:  # 最多输出10条
        airline = flight["airline"]["name"]
        flight_iata = flight["flight"]["iata"]
        departure_time = flight["departure"]["scheduled"]
        arrival_time = flight["arrival"]["scheduled"]
        print(f"航班号：{flight_iata} | 航空公司：{airline}")
        print(f"起飞时间：{departure_time}")
        print(f"到达时间：{arrival_time}")
        print("-" * 40)

# 示例调用（替换城市名和日期）
get_flights_by_city("西安", "北京", "2025-05-20")
