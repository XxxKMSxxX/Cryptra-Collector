import asyncio

import uvicorn
from fastapi import FastAPI, Response


class HealthCheck:
    condition = asyncio.Condition()
    is_healthy = True

    def __init__(self):
        self.app = FastAPI()
        self._setup_routes()

    def _setup_routes(self):
        @self.app.get("/health")
        async def health_check(response: Response):
            """
            ヘルスチェックエンドポイント

            Returns:
                dict: ステータスメッセージ
            """
            async with HealthCheck.condition:
                if HealthCheck.is_healthy:
                    response.status_code = 200
                    return {"status": "ok"}
                else:
                    response.status_code = 503
                    return {"status": "unhealthy"}

    @classmethod
    async def set_health_status(cls, is_healthy: bool):
        """
        ヘルスステータスを設定するメソッド

        Args:
            is_healthy (bool): ヘルスステータス
        """
        async with cls.condition:
            if cls.is_healthy != is_healthy:
                cls.is_healthy = is_healthy
                cls.condition.notify_all()

    async def start(self):
        """
        FastAPIサーバーを起動する非同期関数
        """
        config = uvicorn.Config(self.app, host="0.0.0.0", port=80, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
