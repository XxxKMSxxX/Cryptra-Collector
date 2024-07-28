from threading import Thread
from typing import Any

from flask import Flask, jsonify


class WSHealthCheck:
    def __init__(self) -> None:
        """WSHealthCheckクラスの初期化"""
        self.app: Flask = Flask(__name__)
        self.first_message_received: bool = False
        self.app.add_url_rule(
            "/health", "health_check", self.health_check, methods=["GET"]
        )

    def health_check(self) -> Any:
        """ヘルスチェック用のエンドポイント

        Returns:
            Any: ヘルスチェック結果
        """
        if self.first_message_received:
            return jsonify(status="OK"), 200
        else:
            return jsonify(status="Waiting for first message"), 503

    def start_flask_app(self) -> None:
        """Flaskアプリを開始する"""
        self.app.run(host="0.0.0.0", port=8080)

    def set_first_message_received(self, value: bool) -> None:
        """最初のメッセージが受信されたことを設定する

        Args:
            value (bool): 最初のメッセージが受信されたかどうか
        """
        self.first_message_received = value

    def run(self) -> Thread:
        """ヘルスチェックのスレッドを起動する

        Returns:
            Thread: 実行中のスレッド
        """
        flask_thread: Thread = Thread(target=self.start_flask_app)
        flask_thread.start()
        return flask_thread
