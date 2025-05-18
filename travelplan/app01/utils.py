# ✅ 新版本写法
# from openai import OpenAI
from django.conf import settings
import requests
# client = OpenAI(api_key=settings.OPENAI_API_KEY)
# 调用OPENAI接口实现旅游路径规划功能
def generate_travel_plan(info,feedback):
    prompt = (
        f"请帮我生成一份旅行计划：\n"
        f"目的地：{info.destination}\n"
        f"出发日期：{info.travel_start_date}\n"
        f"结束日期：{info.travel_end_date}\n"
        f"预算：{info.budget} 元\n"
        f"喜欢的景点类型：{info.favorite_scenic_type}\n"
        f"旅行同伴：{info.travel_companion or '无'}"
        f"同时注意生成计划时需要考虑：{feedback}\n"
    )
    print('prompt'+prompt)
    # 使用 API2D 代理地址
    api_url = "https://openai.api2d.net/v1/chat/completions"
    headers = {
        "Authorization": "Bearer fk232710-xSebTGIZWjLnmHjKEcoPUBnW73IueTYP",  # 替换成你在 API2D 获取的 API Key
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",  # 你可以使用 gpt-4 或者其他模型
        "messages": [
            {"role": "system", "content": "你是一位专业的旅行规划师，擅长为用户提供详细的行程安排。"},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(api_url, json=data, headers=headers)
    print(response.status_code, response.text)
    if response.status_code == 200:
        result = response.json()  # ✅ 把 JSON 转成字典
        return result['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code}, {response.text}"


# 添加审核模块工具
# import re
# import jieba
# from textblob import TextBlob
#
# SENSITIVE_WORDS = ['垃圾', '骗子', '骗钱', '无语', '傻', '傻逼', '滚']
# MIN_COMMENT_LENGTH = 5
#
# def simple_sentiment_analysis(text):
#     # 使用 TextBlob 英文分析或你可替换为中文模型
#     blob = TextBlob(text)
#     polarity = blob.sentiment.polarity
#     if polarity > 0.3:
#         return "positive"
#     elif polarity < -0.3:
#         return "negative"
#     return "neutral"

def evaluate_comment_quality(text):
    if not text:
        return 0.0
    length_score = min(len(text) / 50, 1.0)  # 50字以上为满分
    unique_words = len(set(jieba.lcut(text)))
    diversity_score = min(unique_words / 10, 1.0)
    return round((length_score + diversity_score) / 2, 2)

def auto_review_feedback(feedback):
    comment = feedback.comment or ''
    rating = feedback.rating

    # 1. 空或太短
    if len(comment.strip()) < MIN_COMMENT_LENGTH:
        feedback.reviewed = True
        feedback.approved = False
        feedback.review_reason = "内容过短"
        return feedback

    # 2. 敏感词过滤
    for word in SENSITIVE_WORDS:
        if re.search(word, comment, re.IGNORECASE):
            feedback.reviewed = True
            feedback.approved = False
            feedback.review_reason = f"包含敏感词: {word}"
            return feedback

    # 3. 情感分析
    sentiment = simple_sentiment_analysis(comment)
    feedback.sentiment = sentiment

    # 4. 评论质量分析
    quality_score = evaluate_comment_quality(comment)
    feedback.quality_score = quality_score

    # 5. 逻辑判定通过
    feedback.reviewed = True
    feedback.approved = True
    feedback.review_reason = "自动审核通过"
    return feedback


