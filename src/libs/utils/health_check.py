import uvicorn
from fastapi import FastAPI, Response


class HealthCheck:
    def __init__(self, is_healthy: bool = True):
        self.app = FastAPI()
        self._is_healthy = is_healthy
        self._setup_routes()

    def _setup_routes(self):
        @self.app.get("/health")
        async def health_check(response: Response):
            """
            ヘルスチェックエンドポイント

            Returns:
                dict: ステータスメッセージ
            """
            if self._is_healthy:
                response.status_code = 200
                return {"status": "ok"}
            else:
                response.status_code = 503
                return {"status": "unhealthy"}

    def set_health_status(self, is_healthy: bool):
        """
        ヘルスステータスを設定するメソッド

        Args:
            is_healthy (bool): ヘルスステータス
        """
        self._is_healthy = is_healthy

    async def start(self):
        """
        FastAPIサーバーを起動する非同期関数
        """
        config = uvicorn.Config(self.app, host="0.0.0.0", port=8080, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
