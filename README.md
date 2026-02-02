# Talent Analytics PDF Analyzer

Talent Analytics（性格・価値観診断）の受検結果レポートPDFを解析し、面接官向けのブリーフィングPDFを自動生成するPoCプロジェクトです。

## 機能

- Talent Analytics PDFをAzure OpenAIで解析
- 面接官向けのブリーフィング情報を抽出（総合的な特徴、強み、リスク、面接の進め方メモ）
- ReportLabを使用したPDF生成

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成し、Azure OpenAIの設定を入力してください：

```bash
cp .env.example .env
```

`.env`ファイルを編集：

```
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

### 3. 環境変数の確認（オプション）

環境変数が正しく設定されているか確認：

```bash
python test_env.py
```

## 使用方法

### Pythonコードから直接呼び出す場合

```python
from ta_interview_briefing.azure_client import analyze_ta_pdf_with_azure
from ta_interview_briefing.pdf_builder import generate_interview_pdf_from_azure

# 1. PDFを解析
analysis = analyze_ta_pdf_with_azure("sample_ta.pdf")

# 2. ブリーフィングPDFを生成
generate_interview_pdf_from_azure("output.pdf", "水野 港太", analysis)
```

### コマンドライン実行

```bash
python -m ta_interview_briefing.main <pdf_path> [-o output_path] [-n candidate_name]
```

例：

```bash
# 基本的な使用方法
python -m ta_interview_briefing.main sample_ta_report.pdf

# 出力パスと候補者名を指定
python -m ta_interview_briefing.main sample_ta_report.pdf -o output/briefing.pdf -n "水野 港太"
```

### FastAPIサーバーとして実行

```bash
python run_api.py
```

または：

```bash
uvicorn ta_interview_briefing.api:app --reload --host 0.0.0.0 --port 8000
```

サーバー起動後、以下のエンドポイントが利用可能です：

- `GET /`: API情報を取得
- `GET /health`: ヘルスチェック
- `POST /generate_pdf`: PDFをアップロードしてブリーフィングPDFを生成
  - `file`: PDFファイル（multipart/form-data、必須）
  - `candidate_name`: 候補者名（オプション、デフォルト: "候補者"）

#### API使用例

**curlコマンド：**

```bash
curl -X POST "http://localhost:8000/generate_pdf" \
  -F "file=@sample_ta_report.pdf" \
  -F "candidate_name=水野 港太" \
  --output briefing.pdf
```

**Python（requestsライブラリ）：**

```python
import requests

url = "http://localhost:8000/generate_pdf"
files = {"file": open("sample_ta_report.pdf", "rb")}
data = {"candidate_name": "水野 港太"}

response = requests.post(url, files=files, data=data)
if response.status_code == 200:
    with open("briefing.pdf", "wb") as f:
        f.write(response.content)
    print("PDFを生成しました: briefing.pdf")
else:
    print(f"エラー: {response.status_code} - {response.text}")
```

**Swagger UI（ブラウザ）：**

サーバー起動後、以下のURLにアクセスしてAPIドキュメントとテストUIを確認できます：

```
http://localhost:8000/docs
```

## プロジェクト構成

```
talent-analytics-pdf-analyzer/
├── ta_interview_briefing/
│   ├── __init__.py          # パッケージ初期化
│   ├── models.py            # データモデル定義
│   ├── azure_client.py      # Azure OpenAIを使ったPDF解析
│   ├── pdf_builder.py       # ReportLabを使ったPDF生成
│   ├── main.py              # CLI実行用エントリーポイント
│   └── api.py               # FastAPIアプリケーション
├── run_api.py               # FastAPIサーバー起動スクリプト
├── requirements.txt         # 依存パッケージ
├── .env.example             # 環境変数テンプレート
├── Dockerfile               # Dockerイメージ定義
├── docker-compose.yml       # Docker Compose設定
├── .dockerignore            # Dockerビルド除外ファイル
└── README.md                # このファイル
```

## 主要関数

### `analyze_ta_pdf_with_azure(pdf_path: str) -> dict`

Talent Analytics PDFをAzure OpenAIで解析し、以下の構造の辞書を返します：

```python
{
    "summary": "候補者の総合的な特徴の要約",
    "risk_points": ["見定めポイント（リスク）1", ...],
    "attract_points": ["アトラクトポイント（強み）1", ...],
    "notes_for_interviewer": ["面接官向けの進め方メモ1", ...]
}
```

### `generate_interview_pdf_from_azure(output_path: str, candidate_name: str, analysis: dict) -> None`

解析結果から面接官向けブリーフィングPDFを生成します。

## 環境変数

`.env`ファイルに以下の環境変数を設定してください：

```
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
# または
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# 日本語フォントパス（オプション）
# IPAexGothicフォントを使用する場合
JAPANESE_FONT_PATH=/path/to/ipag.ttf
```

`.env.example`をコピーして`.env`ファイルを作成：

```bash
cp .env.example .env
# .envファイルを編集して上記の値を設定
```

**注意**: 
- `AZURE_OPENAI_DEPLOYMENT` と `AZURE_OPENAI_DEPLOYMENT_NAME` のどちらでも対応しています。
- 日本語フォントが正しく表示されない場合は、`JAPANESE_FONT_PATH` 環境変数にIPAexGothicフォントのパスを設定してください。
  - IPAexGothicフォントのダウンロード: https://ipafont.ipa.go.jp/

## Dockerでの実行

### 前提条件

- Dockerがインストールされていること
- Docker Composeがインストールされていること（通常、Docker Desktopに含まれています）

### 基本的な使い方

1. **環境変数の設定**

`.env`ファイルを作成し、Azure OpenAIの設定を入力：

```bash
cp .env.example .env
# .envファイルを編集してAzure OpenAIの設定を入力
```

2. **Docker Composeを使用して起動（推奨）**

```bash
# コンテナをビルドして起動
docker-compose up -d

# ログを確認
docker-compose logs -f

# 停止
docker-compose down
```

起動後、以下のURLでAPIにアクセスできます：
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

3. **Dockerコマンドを直接使用**

```bash
# イメージをビルド
docker build -t talent-analytics-pdf-analyzer .

# コンテナを実行
docker run -d \
  --name talent-analytics-api \
  -p 8000:8000 \
  --env-file .env \
  talent-analytics-pdf-analyzer
```

詳細な使い方は `DOCKER_USAGE.md` を参照してください。

## 注意事項

- Azure OpenAI APIの利用には適切な認証情報が必要です
- PDFのテキスト抽出ができない場合（画像のみのPDFなど）はエラーになります
- 長文の場合は1ページに収まらない可能性があります（PoCレベル）
- Dockerを使用する場合は、`.env`ファイルを適切に設定してください

## プロダクション化に向けて

このプロジェクトをプロダクトに組み込む際の改修項目については、`PRODUCTION_CHECKLIST.md` を参照してください。

主な改修項目：
- セキュリティ強化（認証・認可、入力検証）
- ログ・監視の実装
- エラーハンドリングの強化
- パフォーマンス最適化
- データベース連携
- テストの実装

