FROM python:3.11-slim

# 作業ディレクトリ作成
WORKDIR /app

# 必要ファイルコピー
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリコードをコピー
COPY ./app .

# .env を使用可能にする（uvicorn 起動時）
ENV PYTHONPATH=/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
