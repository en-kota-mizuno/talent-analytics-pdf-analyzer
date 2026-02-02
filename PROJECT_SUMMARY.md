# プロジェクト概要と整理

## 📋 プロジェクトの目的

**Talent Analytics PDF Analyzer** は、Talent Analytics（性格・価値観診断）の受検結果レポートPDFを自動解析し、面接官向けのブリーフィングPDFを生成するツールです。

### 何ができるか

1. **PDFをアップロード** → Talent Analyticsの受検結果PDFを読み込む
2. **AIが解析** → Azure OpenAIがPDFの内容を分析し、面接に必要な情報を抽出
3. **PDFを生成** → 面接官向けのブリーフィングPDFを自動生成

## 🏗️ プロジェクトの構成

```
talent-analytics-pdf-analyzer/
├── ta_interview_briefing/          # メインのパッケージ
│   ├── __init__.py                 # パッケージの初期化
│   ├── models.py                   # データの型定義
│   ├── azure_client.py             # Azure OpenAIとの連携
│   ├── pdf_builder.py              # PDF生成
│   ├── main.py                     # コマンドライン実行
│   └── api.py                      # Web API（FastAPI）
│
├── requirements.txt                # 必要なPythonパッケージ一覧
├── .env                            # 実際の環境変数（自分で作成）
│
├── Dockerfile                      # Dockerイメージの定義
├── docker-compose.yml              # Docker Composeの設定
│
├── run_api.py                      # APIサーバー起動スクリプト
├── test_env.py                     # 環境変数確認スクリプト
├── test_azure_openai.py            # Azure OpenAI接続テスト
│
└── README.md                       # プロジェクトの説明書
```

## 🔧 主要なファイルの役割

### 1. `ta_interview_briefing/azure_client.py`
**役割**: Azure OpenAIを使ってPDFを解析する

**主な機能**:
- PDFファイルからテキストを抽出
- Azure OpenAI APIに送信して解析
- 以下の情報を取得:
  - `summary`: 候補者の総合的な特徴
  - `risk_points`: 見定めポイント（リスク）
  - `attract_points`: アトラクトポイント（強み）
  - `notes_for_interviewer`: 面接の進め方メモ

### 2. `ta_interview_briefing/pdf_builder.py`
**役割**: 解析結果からPDFを生成する

**主な機能**:
- ReportLabを使ってPDFを作成
- 日本語フォントを自動設定
- 以下のセクションを表示:
  - タイトル
  - 候補者名
  - 総合特徴
  - 見定めポイント
  - アトラクトポイント
  - 面接の進め方メモ

### 3. `ta_interview_briefing/main.py`
**役割**: コマンドラインから実行する

**使い方**:
```bash
python3 -m ta_interview_briefing.main sample.pdf -n "候補者名"
```

### 4. `ta_interview_briefing/api.py`
**役割**: Web APIとして提供する

**使い方**:
- サーバーを起動: `python3 run_api.py`
- ブラウザで `http://localhost:8000/docs` にアクセス
- PDFをアップロードしてブリーフィングPDFを生成

## 🚀 使い方（3つの方法）

### 方法1: コマンドラインから実行

```bash
python3 -m ta_interview_briefing.main "PDFファイルのパス" -n "候補者名"
```

**例**:
```bash
python3 -m ta_interview_briefing.main \
  "/Users/kota_mizuno/Downloads/2240272_水野港太_2025TA9月全社受検.pdf" \
  -n "水野 港太"
```

### 方法2: Pythonコードから直接呼び出す

```python
from ta_interview_briefing.azure_client import analyze_ta_pdf_with_azure
from ta_interview_briefing.pdf_builder import generate_interview_pdf_from_azure

# PDFを解析
analysis = analyze_ta_pdf_with_azure("sample.pdf")

# PDFを生成
generate_interview_pdf_from_azure("output.pdf", "水野 港太", analysis)
```

### 方法3: Web APIとして使用（Docker推奨）

```bash
# Docker Composeで起動
docker-compose up -d

# ブラウザでアクセス
# http://localhost:8000/docs
```

## ⚙️ 設定が必要なもの

### 1. 環境変数（`.env`ファイル）

以下の情報を設定する必要があります：

```
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

**取得方法**:
- Azure Portalにログイン
- Azure OpenAIリソースを作成
- エンドポイントURLとAPIキーを取得

### 2. Pythonパッケージのインストール

```bash
pip install -r requirements.txt
```

## 🔄 処理の流れ

```
1. PDFファイルを読み込む
   ↓
2. PDFからテキストを抽出（PyPDF2）
   ↓
3. Azure OpenAIに送信
   ↓
4. AIが解析してJSON形式で返す
   {
     "summary": "...",
     "risk_points": [...],
     "attract_points": [...],
     "notes_for_interviewer": [...]
   }
   ↓
5. ReportLabでPDFを生成
   ↓
6. ブリーフィングPDFが完成
```

## 📦 使用している技術

### 主要なライブラリ

- **openai**: Azure OpenAI APIとの通信
- **reportlab**: PDF生成
- **PyPDF2**: PDFからテキスト抽出
- **fastapi**: Web APIフレームワーク
- **pydantic**: データの型定義とバリデーション

### 外部サービス

- **Azure OpenAI Service**: PDFの内容を解析するAI

## 🐳 Dockerについて

### なぜDockerを使うのか

1. **環境の統一**: 誰が使っても同じ環境で動作
2. **セットアップの簡素化**: 1コマンドで起動
3. **日本語フォントの自動インストール**: 環境ごとの差異を解消
4. **デプロイの容易さ**: 本番環境でも同じ方法で起動

### Dockerの基本的なコマンド

```bash
# 起動
docker-compose up -d

# 停止
docker-compose down

# ログ確認
docker-compose logs -f

# 状態確認
docker-compose ps
```

## 🎯 実際の使用例

### シナリオ: 面接前に候補者の情報を確認したい

1. **PDFを準備**: Talent Analyticsの受検結果PDFを用意
2. **実行**: 
   ```bash
   python3 -m ta_interview_briefing.main candidate.pdf -n "山田太郎"
   ```
3. **結果**: `candidate_interview_briefing.pdf` が生成される
4. **確認**: PDFを開いて、面接のポイントを確認

### シナリオ: 複数の候補者を一括処理したい

1. **APIサーバーを起動**: `docker-compose up -d`
2. **ブラウザでアクセス**: `http://localhost:8000/docs`
3. **PDFをアップロード**: 各候補者のPDFを順番にアップロード
4. **PDFをダウンロード**: 生成されたブリーフィングPDFを保存

## 🔍 トラブルシューティング

### よくある問題と解決方法

#### 1. 日本語が文字化けする
- **原因**: 日本語フォントが設定されていない
- **解決**: CIDFont（HeiseiKakuGo-W5）が自動的に使用されます
- Dockerを使用している場合は、Notoフォントが自動インストールされます

#### 2. Azure OpenAI APIでエラーが出る
- **原因**: 環境変数が正しく設定されていない
- **解決**: `test_env.py` で環境変数を確認
- **確認**: `test_azure_openai.py` で接続テスト

#### 3. PDFが生成されない
- **原因**: PDFファイルが画像のみの場合、テキスト抽出できない
- **解決**: テキストが含まれたPDFを使用してください

## 📝 今後の拡張可能性

### できること

1. **複数のPDFを一括処理**
2. **API経由で他のシステムと連携**
3. **カスタムテンプレートの追加**
4. **多言語対応**

### 改善の余地

1. **エラーハンドリングの強化**
2. **ログ機能の追加**
3. **パフォーマンスの最適化**
4. **UIの追加（Webインターフェース）**

## 🎓 技術的なポイント（理解しておくと良いこと）

### 1. パッケージ構造
- `ta_interview_briefing/` はPythonのパッケージ
- 各ファイルが役割を持って分かれている
- `__init__.py` で外部に公開する機能を定義

### 2. 環境変数
- `.env` ファイルに機密情報を保存
- コードに直接書かない（セキュリティのため）
- `.env.example` はテンプレート

### 3. Docker
- コンテナ = アプリケーションを動かす箱
- イメージ = コンテナの設計図
- `docker-compose` = 複数のコンテナを管理

### 4. API
- FastAPI = Web APIを作るフレームワーク
- エンドポイント = APIの機能（例: `/generate_pdf`）
- Swagger UI = APIの使い方を確認できる画面

## 📚 参考資料

- **Azure OpenAI**: https://azure.microsoft.com/ja-jp/products/ai-services/openai-service
- **ReportLab**: https://www.reportlab.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Docker**: https://www.docker.com/

## ✅ チェックリスト

プロジェクトを使い始める前に：

- [ ] `.env` ファイルを作成してAzure OpenAIの設定を入力
- [ ] `pip install -r requirements.txt` でパッケージをインストール
- [ ] `python3 test_env.py` で環境変数を確認
- [ ] `python3 test_azure_openai.py` でAzure OpenAI接続を確認
- [ ] サンプルPDFで動作確認

## 🎉 まとめ

このプロジェクトは、**AIを使ってPDFを解析し、面接官向けの情報を自動生成する**ツールです。

- **入力**: Talent Analytics PDF
- **処理**: Azure OpenAIで解析
- **出力**: 面接官向けブリーフィングPDF

コマンドライン、Pythonコード、Web APIの3つの方法で使用できます。

