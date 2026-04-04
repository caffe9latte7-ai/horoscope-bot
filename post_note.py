import os
import json
import random
import smtplib
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google import genai

THEMES = [
    {
        "title": "Preplyで一円も稼げなかった話とitalkiに乗り換えた理由",
        "prompt": """
オンライン日本語教師のとうかさんの実体験をもとに記事を書いてください。

【実体験】
- 最初はPreplyに登録したが全く予約が入らなかった
- Preplyは体験レッスンが必ず0円で、継続契約に至らず一円も稼げなかった
- 講師数が増えてインプレッションでも選ばれる自信がなくなり退会
- italkiの募集にチャレンジして合格し、現在はメインプラットフォームとして活用中
"""
    },
    {
        "title": "italki、格安スタートから値上げして気づいたこと",
        "prompt": """
オンライン日本語教師のとうかさんの実体験をもとに記事を書いてください。

【実体験】
- 最初は30分5ドルという格安設定でスタート
- 安い価格帯だと生徒の層が様々で継続しない人も多かった
- 生徒がつき始めてから「しっかり学びたい人は値上げしても続けてくれる」と気づいた
- 現在は30分10ドルに値上げ。それでも安めだと感じている
"""
    },
    {
        "title": "italkiの単発レッスンはデメリットじゃなかった",
        "prompt": """
オンライン日本語教師のとうかさんの実体験をもとに記事を書いてください。

【実体験】
- 最初の予約はすぐ入ったが、継続する人は少なく単発が多かった
- 最初は不安に思ったが、単発レッスンの気楽さに気づいた
- 毎回「初めまして」から自己紹介・フリートークで完結するシンプルさが心地よい
- 今は単発もありと前向きに捉えている
"""
    },
    {
        "title": "人気講師のプロフィールを「盗んで」予約が増えた話",
        "prompt": """
オンライン日本語教師のとうかさんの実体験をもとに記事を書いてください。

【実体験】
- italkiで人気のある講師のプロフィールを研究した
- 完全なコピーではなく、文体・構成・読みやすさなどいいところを参考にした
- プロフィール改善後、予約が入りやすくなった
- 初心者講師へのアドバイスとして「人気講師から学ぶ」ことを勧めたい
"""
    },
    {
        "title": "Cafetalkとitalkiはここどこどこが違う【使い分け術】",
        "prompt": """
オンライン日本語教師のとうかさんの実体験をもとに記事を書いてください。

【実体験】
- italkiの生徒数が少し減ったタイミングでCafetalkを始めた
- Cafetalkは母体が日本企業でサポートが日本語・チャット対応で早い
- Cafetalkは「いますぐレッスン」機能で単発生徒が多い傾向
- 割引クーポンや講師コラムなど日本っぽいプロモーション手段が豊富
- italkiとCafetalkでうまく使い分けができている
"""
    },
]

ARTICLE_PROMPT_TEMPLATE = """
あなたはオンライン日本語教師「とうか」として記事を書いてください。

{theme_prompt}

【文体・スタイルの条件】
- フレンドリーで親しみやすい「です・ます」調
- 同じオンライン日本語教師や、これから始めたい人に語りかける感じ
- 失敗談や悩みも正直に書く（完璧な先生より等身大の先生）
- 具体的なエピソードを交えて共感を呼ぶ内容
- 最後に読者への問いかけや励ましで締める

【構成】
- 冒頭：共感を呼ぶ「あるある」や問いかけ
- 本文：実体験をもとにした具体的なエピソード
- まとめ：読者へのメッセージ

【その他の条件】
- 1000字程度
- タイトルは含めない（別途設定します）
- ハッシュタグは末尾に3〜4個（#オンライン日本語教師 #italki #日本語教師 など）
- 説明文や前置きは不要、本文のみ出力
"""

def generate_article(theme):
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    prompt = ARTICLE_PROMPT_TEMPLATE.format(theme_prompt=theme["prompt"])
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text.strip()

def send_email(title, content):
    sender = os.getenv("GMAIL_ADDRESS")
    password = os.getenv("GMAIL_APP_PASSWORD")
    receiver = os.getenv("GMAIL_ADDRESS")

    today = date.today().strftime("%Y/%m/%d")
    subject = f"【note記事】{today}：{title}"

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(content, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

    print(f"メール送信完了：{subject}")

def main():
    theme = random.choice(THEMES)
    print(f"テーマ：{theme['title']}")

    print("記事を生成中...")
    article = generate_article(theme)
    print(f"生成完了！\n{article[:100]}...\n")

    print("メールを送信中...")
    send_email(theme["title"], article)
    print("完了！")

if __name__ == "__main__":
    main()