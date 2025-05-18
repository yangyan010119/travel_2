import requests

# 高德地图 API Key
API_KEY = 'bf46eb2481a85735a6421b4044bc8804'


class HotelQuery:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_location_from_name(self, destination,place_name):
        """获取景点的经纬度"""
        url = f"https://restapi.amap.com/v3/geocode/geo?key={self.api_key}&address={destination+place_name}"
        print("url",url)
        response = requests.get(url)
        data = response.json()
        print("data",data)
        if data['status'] == '1' and data['geocodes']:
            location = data['geocodes'][0]['location']
            return location.split(',')
        else:
            print(f"无法获取景点 {place_name} 的经纬度")
            return None

    def get_hotels_nearby(self, location, hotel_keyword, place_name):
        """获取附近指定类型的酒店信息"""
        longitude, latitude = location
        url = (
            f"https://restapi.amap.com/v3/place/around"
            f"?key={self.api_key}"
            f"&location={longitude},{latitude}"
            f"&types=住宿服务"
            f"&keywords={hotel_keyword}"
            f"&radius=5000"
            f"&offset=20"
            f"&page=1"
            f"&output=json"
        )
        print("url",url)
        response = requests.get(url)
        data = response.json()

        if data['status'] == '1' and data['pois']:
            return data['pois']
        else:
            print(f"没有找到景点 {place_name} 附近的酒店")
            return []

    def sort_hotels_by_distance(self, hotels, location):
        """按距离对酒店进行排序"""
        def calculate_distance(hotel):
            hotel_location = hotel.get('location', '')
            if not hotel_location:
                return float('inf')
            hotel_longitude, hotel_latitude = map(float, hotel_location.split(','))
            return (float(location[0]) - hotel_longitude) ** 2 + (float(location[1]) - hotel_latitude) ** 2

        return sorted(hotels, key=calculate_distance)

    def display_hotels(self, hotels):
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

    def query_hotels_for_scenic_spots(self, destination,scenic_spots, hotel_keyword):
        """查询多个景点的酒店信息"""
        results = {}
        for place_name in scenic_spots:
            location = self.get_location_from_name(destination,place_name)
            if location:
                print(f"\n获取到 {place_name} 的经纬度：{location}")
                hotels = self.get_hotels_nearby(location, hotel_keyword, place_name)  # 传递 place_name 作为参数
                sorted_hotels = self.sort_hotels_by_distance(hotels, location)
                results[place_name] = sorted_hotels[:5] if sorted_hotels else []  # 确保有酒店数据才切片
        return results

def query_hotels(api_key: str,destination, scenic_spots_raw: list, hotel_keyword: str):
    # 将列表中的单个字符串按逗号切分成真正的景点列表
    if len(scenic_spots_raw) == 1 and isinstance(scenic_spots_raw[0], str):
        scenic_spots = [spot.strip() for spot in scenic_spots_raw[0].split(",")]
    else:
        scenic_spots = scenic_spots_raw

    print("scenic_spots", scenic_spots)

    hotel_query = HotelQuery(api_key)
    return hotel_query.query_hotels_for_scenic_spots(destination,scenic_spots, hotel_keyword)

