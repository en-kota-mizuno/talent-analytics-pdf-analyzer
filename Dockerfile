# Python 3.11を使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージの更新と必要なツールのインストール
RUN apt-get update && apt-get install -y \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# 依存パッケージをコピーしてインストール
COPY requirements.txt .
# SSL証明書の問題を回避（企業プロキシ環境の場合）
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# ポート8000を公開（FastAPI用）
EXPOSE 8000

# 環境変数のデフォルト設定（.envファイルで上書き可能）
ENV PYTHONUNBUFFERED=1

# FastAPIサーバーを起動
CMD ["uvicorn", "ta_interview_briefing.api:app", "--host", "0.0.0.0", "--port", "8000"]

