import requests

# 高德地图 API Key
API_KEY = 'bf46eb2481a85735a6421b4044bc8804'


def get_location_from_name(place_name):
    """获取景点的经纬度"""
    url = f"https://restapi.amap.com/v3/geocode/geo?key={API_KEY}&address={place_name}"
    response = requests.get(url)
    data = response.json()

    if data['status'] == '1' and data['geocodes']:
        location = data['geocodes'][0]['location']
        return location.split(',')
    else:
        print("无法获取该景点的经纬度")
        return None


def get_hotels_nearby(location, hotel_keyword):
    """获取附近指定类型的酒店信息"""
    longitude, latitude = location
    url = (
        f"https://restapi.amap.com/v3/place/around"
        f"?key={API_KEY}"
        f"&location={longitude},{latitude}"
        f"&types=住宿服务"
        f"&keywords={hotel_keyword}"
        f"&radius=5000"
        f"&offset=20"
        f"&page=1"
        f"&output=json"
    )

    response = requests.get(url)
    data = response.json()

    if data['status'] == '1' and data['pois']:
        return data['pois']
    else:
        print("没有找到符合条件的酒店")
        return []


def sort_hotels_by_distance(hotels, location):
    """按距离对酒店进行排序"""

    def calculate_distance(hotel):
        hotel_location = hotel.get('location', '')
        if not hotel_location:
            return float('inf')
        hotel_longitude, hotel_latitude = map(float, hotel_location.split(','))
        return (float(location[0]) - hotel_longitude) ** 2 + (float(location[1]) - hotel_latitude) ** 2

    return sorted(hotels, key=calculate_distance)


def display_hotels(hotels):
    """输出酒店信息"""
    if hotels:
        print("\n找到的酒店列表：")
        for hotel in hotels:
            name = hotel['name']
            address = hotel.get('address', '无地址')
            distance = hotel.get('distance', '未知')
            hotel_type = hotel.get('type', '未知类型')
            print(f"酒店名称: {name} | 类型: {hotel_type} | 地址: {address} | 距离: {distance}米")
    else:
        print("没有找到酒店")


# 主程序
if __name__ == "__main__":
    place_name = input("请输入景点名称（如：天安门）：")
    hotel_keyword = input("请输入想要查找的酒店类型（如：宾馆、快捷、豪华、民宿）：")
    location = get_location_from_name(place_name)

    if location:
        print(f"\n获取到 {place_name} 的经纬度：{location}")
        hotels = get_hotels_nearby(location, hotel_keyword)
        sorted_hotels = sort_hotels_by_distance(hotels, location)
        display_hotels(sorted_hotels)
