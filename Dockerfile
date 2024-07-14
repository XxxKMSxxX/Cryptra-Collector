# ビルドステージ
FROM python:3.12-slim-bookworm AS build

# 作業ディレクトリを設定
WORKDIR /build

# システムパッケージのインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 全てコピー
COPY . .

# 依存関係のインストール
RUN pip install --upgrade pip && \
    pip install .

# 実行ステージ
FROM python:3.12-slim-bookworm

# 作業ディレクトリを設定
WORKDIR /app

# ビルドステージからインストール済みのパッケージをコピー
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

COPY src/ ./src

# ポートを公開
EXPOSE 8080

# コンテナ起動時のデフォルトコマンドを設定
CMD ["sh", "-c", "python -Bum collector ${EXCHANGE} ${CONTRACT} ${SYMBOL} ${AWS_REGION}"]
