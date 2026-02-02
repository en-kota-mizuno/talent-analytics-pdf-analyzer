# Docker使用方法ガイド

このプロジェクトをDockerで実行する方法を説明します。

## 前提条件

- Dockerがインストールされていること
- Docker Composeがインストールされていること（通常、Docker Desktopに含まれています）

## 基本的な使い方

### 1. 環境変数の設定

`.env`ファイルを作成し、Azure OpenAIの設定を入力してください：

```bash
cp .env.example .env
# .envファイルを編集
```

`.env`ファイルの例：

```
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
# または
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

### 2. Docker Composeを使用して起動（推奨）

最も簡単な方法です：

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

### 3. Dockerコマンドを直接使用

```bash
# イメージをビルド
docker build -t talent-analytics-pdf-analyzer .

# コンテナを実行
docker run -d \
  --name talent-analytics-api \
  -p 8000:8000 \
  --env-file .env \
  talent-analytics-pdf-analyzer

# ログを確認
docker logs -f talent-analytics-api

# 停止
docker stop talent-analytics-api
docker rm talent-analytics-api
```

## 開発時の使い方

開発中にコードの変更を反映させたい場合：

```bash
# docker-compose.ymlのvolumes設定により、コード変更が自動反映されます
docker-compose up -d

# コードを変更した後、コンテナを再起動
docker-compose restart
```

## APIの使用例

### curlコマンド

```bash
curl -X POST "http://localhost:8000/generate_pdf" \
  -F "file=@sample_ta_report.pdf" \
  -F "candidate_name=水野 港太" \
  --output briefing.pdf
```

### Python（requestsライブラリ）

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
```

## トラブルシューティング

### ポートが既に使用されている場合

```bash
# ポート8000が使用されている場合は、docker-compose.ymlでポート番号を変更
# 例: "8001:8000" に変更すると、http://localhost:8001 でアクセスできます
```

### 環境変数が読み込まれない場合

```bash
# .envファイルが正しい場所にあるか確認
# docker-compose.ymlと同じディレクトリに配置してください
```

### コンテナのログを確認

```bash
# エラーが発生した場合
docker-compose logs api

# リアルタイムでログを確認
docker-compose logs -f api
```

## 本番環境での使用

本番環境では、以下の点に注意してください：

1. **セキュリティ**
   - `.env`ファイルに機密情報を含めない
   - 環境変数は適切に管理する（例：AWS Secrets Manager、Azure Key Vault）

2. **パフォーマンス**
   - リソース制限を設定する
   - ログローテーションを設定する

3. **監視**
   - ヘルスチェックエンドポイントを使用: `GET /health`
   - ログを適切に収集・監視する

