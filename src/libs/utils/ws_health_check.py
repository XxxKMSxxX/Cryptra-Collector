from flask import Flask, jsonify, Response
from threading import Thread


class WSHealthCheck:
    def __init__(self) -> None:
        """WSHealthCheckクラスの初期化"""
        self.app: Flask = Flask(__name__)
        self.first_message_received: bool = False
        self.app.add_url_rule('/health', 'health_check', self.health_check)

    def health_check(self) -> Response:
        """ヘルスチェック用のエンドポイント

        Returns:
            Response: ヘルスチェック結果
        """
        if self.first_message_received:
            return jsonify(status="OK")
        else:
            return jsonify(status="Waiting for first message")

    def start_flask_app(self) -> None:
        """Flaskアプリを開始する"""
        self.app.run(host='0.0.0.0', port=8080)

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
