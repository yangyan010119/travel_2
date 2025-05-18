# rail_query.py

import requests
import json
import re

class HighSpeedRailQuery:
    def __init__(self, api2d_key: str):
        self.api_key = api2d_key
        self.api_url = "https://openai.api2d.net/v1/chat/completions"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def _clean_json(self, raw_text: str) -> str:
        """清理掉 markdown 的代码块包裹"""
        return re.sub(r"^```json|```$", "", raw_text.strip(), flags=re.IGNORECASE).strip()

    def get_train_info(self, departure_city: str, arrival_city: str, date: str) -> dict:
        """
        获取高铁车次信息，返回 JSON 格式
        """
        prompt = (
            f"请以 JSON 格式列出{date}从{departure_city}到{arrival_city}的高铁信息，包含字段："
            "车次 (train_no), 出发时间 (departure_time), 到达时间 (arrival_time), 历时 (duration), "
            "二等座票价 (second_class_price), 一等座票价 (first_class_price), 商务座票价 (business_class_price)。"
            "请返回一个 JSON 数组，字段使用英文 key，票价为数字（单位元），不要添加任何注释或 markdown 包裹。"
        )

        data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5
        }

        response = requests.post(self.api_url, headers=self.headers, json=data)
        print("response",response.text)
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            cleaned = self._clean_json(content)
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                return {"error": "返回内容不是有效的 JSON。", "raw_output": content}
        else:
            return {
                "error": f"请求失败：{response.status_code}",
                "details": response.text
            }

# ✅ 提供外部调用函数
def query_high_speed_rail(api_key: str, departure: str, arrival: str, date: str) -> dict:
    rail_query = HighSpeedRailQuery(api_key)
    return rail_query.get_train_info(departure, arrival, date)
