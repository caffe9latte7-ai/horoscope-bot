import os
from datetime import datetime, date, timezone, timedelta
from dotenv import load_dotenv
from kerykeion import AstrologicalSubject
from google import genai
import tweepy

# .envファイルからAPIキーを読み込む
load_dotenv()


def get_astrology_data():
    """kerykeionで今日の惑星位置を計算する"""

    JST = timezone(timedelta(hours=9))
　　 now = datetime.now(JST)

    # 今日の日時・東京の位置情報をもとに天体配置を計算する
    subject = AstrologicalSubject(
        name="Today",
        year=now.year,
        month=now.month,
        day=now.day,
        hour=now.hour,
        minute=now.minute,
        lng=139.6503,    # 東京の経度
        lat=35.6762,     # 東京の緯度
        tz_str="Asia/Tokyo",
    )

    # 主要な7つの天体の位置をまとめる
    planets = [
        ("太陽",   subject.sun),
        ("月",     subject.moon),
        ("水星",   subject.mercury),
        ("金星",   subject.venus),
        ("火星",   subject.mars),
        ("木星",   subject.jupiter),
        ("土星",   subject.saturn),
    ]

    lines = []
    for name, planet in planets:
        lines.append(f"{name}：{planet['sign']}座 {planet['position']:.1f}度")

    return "\n".join(lines)


def generate_horoscope(astrology_data):
    """Gemini APIを使って牡羊座向けの一言を生成する"""

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    JST = timezone(timedelta(hours=9))
    today = datetime.now(JST).date()

    prompt = (
        f"今日は{today.strftime('%Y年%m月%d日')}です。\n\n"
        f"今日の惑星配置：\n{astrology_data}\n\n"
        "上記の惑星配置をもとに、牡羊座（3/21〜4/19）の人向けに"
        "西洋占星術に基づいた今日の一言を日本語で作ってください。\n\n"
        "条件：\n"
        "- 元気になれる、前向きな内容\n"
        "- 日付や「牡羊座」などのラベルは冒頭に書かない（別途追加します）\n"
        "- 先頭の日付ラベルを除いて100字以内\n"
        "- 本文の後に改行を1つ入れてから「ラッキーアクションは・・・」で終わらせる\n"
        "- ラッキーアクションの内容は絶対に書かない（リプライで別途公開します）\n"
        "- ハッシュタグを末尾に2〜3個つける（例：#牡羊座 #今日の運勢 #占星術）\n"
        "- 上記の形式のみ出力する（説明文や前置きは不要）"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    prefix = f"【{today.strftime('%Y年%m月%d日')}の牡羊座】\n"
    return prefix + response.text.strip()


def generate_lucky_action(astrology_data):
    """Gemini APIを使って面白おかしいラッキーアクションを生成する"""

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    prompt = (
        f"今日の惑星配置：\n{astrology_data}\n\n"
        "牡羊座向けの今日のラッキーアクションを1つ考えてください。\n\n"
        "条件：\n"
        "- 「イカを食べる」「見知らぬ人に笑いかける」のような、ちょっと面白おかしい行動\n"
        "- 日常でできる具体的なこと\n"
        "- 30字以内の短い一文のみ出力する（説明文や前置きは不要）"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text.strip()


def get_x_client():
    """X APIのクライアントを作成する（投稿・リプライで共用）"""
    return tweepy.Client(
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_SECRET"),
    )


def post_to_x(text):
    """X APIを使ってメイン投稿する"""
    client = get_x_client()
    response = client.create_tweet(text=text)
    return response


def reply_to_x(text, reply_to_id):
    """X APIを使って指定ツイートにリプライする"""
    client = get_x_client()
    response = client.create_tweet(text=text, in_reply_to_tweet_id=reply_to_id)
    return response


def main():
    print("今日の惑星配置を計算中...")
    astrology_data = get_astrology_data()
    print(f"惑星配置：\n{astrology_data}\n")

    print("牡羊座の一言を生成中...")
    horoscope = generate_horoscope(astrology_data)
    print(f"生成されたメッセージ：\n{horoscope}\n")

    print("ラッキーアクションを生成中...")
    lucky_action = generate_lucky_action(astrology_data)
    print(f"ラッキーアクション：{lucky_action}\n")

    print("Xに投稿中...")
    main_post = post_to_x(horoscope)
    tweet_id = main_post.data["id"]
    print(f"メイン投稿完了！ツイートID: {tweet_id}")

    print("ラッキーアクションをリプライ中...")
    reply_to_x(lucky_action, reply_to_id=tweet_id)
    print("リプライ完了！")


if __name__ == "__main__":
    main()
