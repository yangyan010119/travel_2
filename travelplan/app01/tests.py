from django.test import TestCase

# Create your tests here.
import requests
# 测试OPEN-AI ，API
headers = {
    "Authorization": "Bearer fk232710-xSebTGIZWjLnmHjKEcoPUBnW73IueTYP",
    "Content-Type": "application/json"
}
data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "user", "content": "你好，帮我写一首关于春天的诗"}
    ]
}
url = "https://openai.api2d.net/v1/chat/completions"
res = requests.post(url, json=data, headers=headers)
print(res.status_code)
print(res.text)




