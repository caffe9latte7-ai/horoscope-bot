import os
import random
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from google import genai
import tweepy

load_dotenv()

JST = timezone(timedelta(hours=9))

MORNING_THEMES = [
    "老後のお金について漠然と不安を感じている50代シングルマザーの気持ち",
    "一人で老後を迎えることへの不安と覚悟",
    "将来どうなるんだろうという気持ちと向き合う日常",
    "子どもが独立した後の孤独感と自由の間で揺れる気持ち",
    "年金だけで生活できるのか心配している50代の本音",
    "シングルマザーとして頑張ってきた自分への労い",
    "老後の住まいについて考え始めた50代の気持ち",
]

EVENING_THEMES = [
    "節約生活の中で見つけた小さな幸せや工夫",
    "買ってよかったもの・やめてよかったことの気づき",
    "生活を見直して変わった価値観や習慣",
    "50代からの健康管理で始めたこと",
    "資産形成を意識し始めたきっかけと行動",
    "人生後半をどう生きるかという気づきや決意",
    "過去を振り返って気づいた自分らしい生き方",
    "子どもとの関係で感じたこと・距離感の変化",
    "終活を意識し始めて気持ちが楽になったこと",
]

PROMPT_TEMPLATE = """
あなたは50代のシングルマザーとして、日々の暮らしや人生についてXに投稿しています。

テーマ：{theme}

以下の条件で投稿文を1つ書いてください：
- 匿名アカウントで発信している等身大の50代女性の言葉
- 丁寧で親しみやすいけれど、時々本音の毒も吐く
- キラキラワード・若作りな言葉・上から目線は絶対に使わない
- 同世代の女性が「わかる！」と思える語り口
- リアルで正直な気持ち（重すぎず・軽すぎず）
- 140字以内
- ハッシュタグを2〜3個末尾につける（例：#50代 #シングルマザー #老後）
- 本文のみ出力（説明文や前置き不要）
"""

def generate_post(themes):
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    theme = random.choice(themes)
    prompt = PROMPT_TEMPLATE.format(theme=theme)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text.strip()

def post_to_x(text):
    client = tweepy.Client(
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_SECRET"),
    )
    response = client.create_tweet(text=text)
    return response

def main():
    now = datetime.now(JST)
    hour = now.hour

    if 5 <= hour < 12:
        print("朝の投稿を生成中...")
        themes = MORNING_THEMES
    else:
        print("夕方の投稿を生成中...")
        themes = EVENING_THEMES

    post = generate_post(themes)
    print(f"生成された投稿：\n{post}\n")

    print("Xに投稿中...")
    result = post_to_x(post)
    print(f"投稿完了！ツイートID: {result.data['id']}")

if __name__ == "__main__":
    main()