import requests

AMAP_API_KEY = "bf46eb2481a85735a6421b4044bc8804"

def get_city_center(city_name):
    """通过城市名称获取该城市中心点经纬度"""
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        "address": city_name,
        "key": AMAP_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] == "1" and data["geocodes"]:
        location = data["geocodes"][0]["location"]
        return location
    else:
        print("获取城市中心点失败")
        return None

def search_restaurants(location, city_name, filter_keywords=None):
    """搜索餐厅，并返回筛选后的餐厅列表（JSON 格式）"""
    url = "https://restapi.amap.com/v3/place/around"
    params = {
        "key": AMAP_API_KEY,
        "location": location,
        "keywords": "餐厅",
        "types": "050000",
        "radius": 5000,
        "offset": 20,
        "page": 1,
        "extensions": "all",
        "city": city_name
    }
    response = requests.get(url, params=params)
    data = response.json()

    restaurant_list = []
    if data["status"] == "1":
        pois = data.get("pois", [])
        for poi in pois:
            name = poi.get("name", "无名餐厅")
            address = poi.get("address", "")
            tel = poi.get("tel", "无电话")
            poi_type = poi.get("type", "未知类型")

            if filter_keywords:
                if not any(keyword in poi_type for keyword in filter_keywords):
                    continue  # 不符合类型筛选

            restaurant_list.append({
                "名称": name,
                "类型": poi_type,
                "地址": address,
                "电话": tel
            })

    return restaurant_list

def get_restaurants_for_city(city_name, filter_keywords=None):
    """主入口：通过城市名和关键词获取餐厅列表"""
    location = get_city_center(city_name)
    if location:
        return search_restaurants(location, city_name, filter_keywords)
    else:
        return []

# # 如果你想单独运行测试，可以取消以下注释
# if __name__ == "__main__":
#     city = input("请输入城市名称：")
#     keywords_input = input("请输入要筛选的类型关键词（如中餐、西餐、咖啡），多个用逗号分隔：")
#     filter_keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]
#     restaurants = get_restaurants_for_city(city, filter_keywords)
#     print(f"{city} 餐厅列表：")
#     for idx, rest in enumerate(restaurants, 1):
#         print(f"{idx}. {rest['名称']} | 类型：{rest['类型']} | 地址：{rest['地址']} | 电话：{rest['电话']}")
