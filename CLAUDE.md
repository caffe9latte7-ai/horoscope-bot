# 牡羊座ホロスコープ X 自動投稿プロジェクト

## プロジェクト概要

西洋占星術をもとに、牡羊座向けの毎日の元気になれる一言をClaude APIで生成し、X（旧Twitter）に自動投稿するPythonプロジェクト。

## 技術スタック

- **言語**: Python 3.x
- **占星術データ計算**: kerykeion（無料Pythonライブラリ）
- **メッセージ生成**: Google Gemini API（無料枠：1日1500回まで）
- **投稿先**: X API v2（tweepy ライブラリ）
- **スケジュール実行**: cron または Claude Code のスケジュール機能
- **APIキー管理**: `.env` ファイル（python-dotenv）

## ファイル構成

```
/Users/takakoasai/Workspace/
├── CLAUDE.md               # このファイル
├── post_horoscope.py       # メイン投稿スクリプト
├── .env                    # APIキー（Gitに含めない）
└── requirements.txt        # 必要なPythonライブラリ一覧
```

## 必要な環境変数（.env）

```
GOOGLE_API_KEY=your_google_api_key
X_API_KEY=your_x_api_key
X_API_SECRET=your_x_api_secret
X_ACCESS_TOKEN=your_x_access_token
X_ACCESS_SECRET=your_x_access_secret
```

## Claudeへの作業指示

### コードの説明スタイル
- コードの説明は**平易な日本語**で行う
- 専門用語を使うときは、かんたんな言葉で補足する
- 何をしているコードなのかを一言で添える

### エラー対応
- エラーが出たときは必ず **「原因」と「対処法」をセットで説明する**
- 例：「このエラーは〇〇が原因です。対処法は〇〇してください。」

### ファイル作成のルール
- **ファイルを作る前に、何を作るか必ず確認する**
- 確認なしにファイルを作成・上書きしない

### セキュリティ
- APIキーはコードに直接書かず、必ず `.env` ファイルから読み込む
- `.env` は `.gitignore` に追加して、Gitに含めない
