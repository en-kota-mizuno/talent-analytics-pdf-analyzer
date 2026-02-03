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

**注意**: テストを実行する場合は、`requirements.txt`に含まれるpytest関連のパッケージもインストールされます。

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

環境変数が正しく設定されているか確認するには、以下のコマンドでテストを実行してください：

```bash
# 環境変数が必要なテストを実行（.envファイルが設定されている場合）
pytest -m requires_env

# または、環境変数を直接確認
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('AZURE_OPENAI_ENDPOINT:', os.getenv('AZURE_OPENAI_ENDPOINT'))"
```

### 4. テストの実行

pytestを使用してテストを実行できます：

```bash
# すべてのテストを実行
pytest

# カバレッジレポート付きで実行
pytest --cov=ta_interview_briefing --cov-report=html

# 特定のテストファイルのみ実行
pytest tests/test_models.py

# マーカーでフィルタリング（例：単体テストのみ）
pytest -m unit

# 環境変数が必要なテストをスキップ
pytest -m "not requires_env"
```

テスト結果のカバレッジレポートは `htmlcov/index.html` で確認できます。

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
- `POST /analyze`: PDFをアップロードして解析結果をJSONで取得
  - `file`: PDFファイル（multipart/form-data、必須）
  - 戻り値: 解析結果（summary, risk_points, attract_points, notes_for_interviewer）
- `POST /generate_pdf`: PDFをアップロードしてブリーフィングPDFを生成
  - `file`: PDFファイル（multipart/form-data、必須）
  - `candidate_name`: 候補者名（オプション、デフォルト: "候補者"）

#### API使用例

**解析結果をJSONで取得（`/analyze`エンドポイント）：**

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@sample_ta_report.pdf" \
  | jq
```

```python
import requests

url = "http://localhost:8000/analyze"
files = {"file": open("sample_ta_report.pdf", "rb")}

response = requests.post(url, files=files)
if response.status_code == 200:
    analysis = response.json()
    print("解析結果:", analysis)
else:
    print(f"エラー: {response.status_code} - {response.text}")
```

**ブリーフィングPDFを生成（`/generate_pdf`エンドポイント）：**

```bash
curl -X POST "http://localhost:8000/generate_pdf" \
  -F "file=@sample_ta_report.pdf" \
  -F "candidate_name=水野 港太" \
  --output briefing.pdf
```

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
├── ta_interview_briefing/          # メインパッケージ
│   ├── __init__.py                 # パッケージ初期化
│   ├── models.py                   # データモデル定義
│   ├── azure_client.py             # Azure OpenAIを使ったPDF解析
│   ├── pdf_builder.py              # ReportLabを使ったPDF生成
│   ├── main.py                     # CLI実行用エントリーポイント
│   └── api.py                      # FastAPIアプリケーション
├── run_api.py                      # FastAPIサーバー起動スクリプト
├── requirements.txt                # 依存パッケージ
├── .env.example                    # 環境変数テンプレート
├── Dockerfile                      # Dockerイメージ定義
├── docker-compose.yml              # Docker Compose設定
├── .dockerignore                   # Dockerビルド除外ファイル
├── .gitignore                      # Git除外ファイル
├── .cursorrules                    # Cursorエディタ用のプロジェクトルール
├── tests/                          # テストディレクトリ
│   ├── __init__.py                 # テストパッケージ初期化
│   ├── conftest.py                  # pytest共通設定とフィクスチャ
│   ├── test_models.py              # データモデルのテスト
│   ├── test_azure_client.py         # Azure OpenAIクライアントのテスト
│   ├── test_pdf_builder.py          # PDF生成のテスト
│   ├── test_api.py                 # FastAPIエンドポイントのテスト
│   ├── test_main.py                # CLI（main.py）のテスト
│   └── README.md                   # テストディレクトリの説明
├── pytest.ini                      # pytest設定ファイル
├── .github/                         # GitHub Actions設定
│   └── workflows/
│       └── ci.yml                  # CI/CDワークフロー
├── README.md                       # このファイル
├── PDF_EXTRACTION_NOTES.md        # PDF抽出に関する注意事項
├── DOCKER_USAGE.md                 # Docker使用方法ガイド
└── DOCKER_BENEFITS.md              # Docker使用の利点
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

## 開発ガイドライン

### Cursor Rules
このプロジェクトには`.cursorrules`ファイルが含まれており、Cursorエディタで開発する際のプロジェクト固有のルールが定義されています。

**重要なルール:**
- **README.mdの更新**: コードや機能を変更した際は、必ずREADME.mdを更新してください
- テスト駆動開発を推奨（テストカバレッジ89%を維持）
- コミットメッセージはプレフィックス付きで日本語で記述
- 環境変数は`.env`ファイルを使用（Gitに含めない）

詳細は`.cursorrules`ファイルを参照してください。

## プロダクション化に向けて

このプロジェクトをプロダクトに組み込む際の主な改修項目：

- **セキュリティ強化**: 認証・認可、入力検証、APIキーの適切な管理
- **ログ・監視の実装**: 構造化ログ、エラートラッキング、パフォーマンス監視
- **エラーハンドリングの強化**: より詳細なエラーメッセージ、リトライ機能
- **パフォーマンス最適化**: キャッシュの導入、非同期処理の検討
- **データベース連携**: 解析結果の永続化、履歴管理
- **テストの拡充**: 統合テスト、E2Eテストの追加（現在のカバレッジ: 89%）

