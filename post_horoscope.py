import os
import random
import smtplib
import json
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from google import genai

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

過去の投稿（重複を避けてください）：
{past_posts}

以下の条件で投稿文を1つ書いてください：
- 匿名アカウントで発信している等身大の50代女性の言葉
- 丁寧で親しみやすいけれど、時々本音の毒も吐く
- キラキラワード・若作りな言葉・上から目線は絶対に使わない
- 同世代の女性が「わかる！」と思える語り口
- リアルで正直な気持ち（重すぎず・軽すぎず）
- 読みやすいように適切な場所で改行を入れる
- 140字以内（改行含む）
- ハッシュタグを2〜3個末尾につける（例：#50代 #シングルマザー #老後）
- 本文のみ出力（説明文や前置き不要）
"""

PAST_POSTS_FILE = "past_posts.json"

def load_past_posts():
    if os.path.exists(PAST_POSTS_FILE):
        with open(PAST_POSTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_past_post(post):
    posts = load_past_posts()
    posts.append({
        "date": datetime.now(JST).strftime("%Y-%m-%d %H:%M"),
        "content": post
    })
    posts = posts[-30:]
    with open(PAST_POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

def generate_post(themes):
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    theme = random.choice(themes)

    past_posts = load_past_posts()
    if past_posts:
        past_text = "\n".join([f"- {p['content'][:50]}..." for p in past_posts[-10:]])
    else:
        past_text = "なし"

    prompt = PROMPT_TEMPLATE.format(theme=theme, past_posts=past_text)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text.strip()

def send_email(post, time_of_day):
    sender = os.getenv("GMAIL_ADDRESS")
    password = os.getenv("GMAIL_APP_PASSWORD")
    receiver = os.getenv("GMAIL_ADDRESS")

    today = datetime.now(JST).strftime("%Y/%m/%d")
    subject = f"【X投稿案】{today} {time_of_day}"

    body = f"""以下の投稿案をご確認ください。
気に入ったらXに貼り付けて投稿してください。

━━━━━━━━━━━━━━━━
{post}
━━━━━━━━━━━━━━━━

※投稿したら past_posts.json に内容を追加してください。
"""

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

    print(f"メール送信完了：{subject}")

def main():
    now = datetime.now(JST)
    hour = now.hour

    if 5 <= hour < 12:
        print("朝の投稿を生成中...")
        themes = MORNING_THEMES
        time_of_day = "朝の投稿"
    else:
        print("夕方の投稿を生成中...")
        themes = EVENING_THEMES
        time_of_day = "夕方の投稿"

    post = generate_post(themes)
    print(f"生成された投稿：\n{post}\n")

    send_email(post, time_of_day)
    save_past_post(post)
    print("完了！")

if __name__ == "__main__":
    main()