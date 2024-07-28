from __future__ import annotations

from typing import Dict, List

from pybotters import WebSocketQueue

from src.libs.utils.logger import LogManager

from ..aws_client import AwsClient


class Kinesis(AwsClient):
    """
    Kinesisクラスは、AWS Kinesisストリームとのインターフェースを提供する。

    Attributes:
        _queue_in (WebSocketQueue): 入力データのキュー
        _client (boto3.client): Kinesisクライアント
    """

    def __init__(self, queue_in: WebSocketQueue, is_healthy: bool = False):
        """
        Kinesisクラスのコンストラクタ。

        Args:
            queue_in (WebSocketQueue): 入力キュー
        """
        super().__init__("kinesis")
        self._queue_in = queue_in
        self._client = self.get_boto3_client("kinesis")
        self._logger = LogManager.get_logger(__name__)
        self._is_healthy = is_healthy

    async def publish(self, stream_name: str, tags: Dict) -> None:
        """
        レコードをKinesisストリームに送信する。

        Args:
            stream_name (str): Kinesisストリームの名前
            tags (Dict): レコードに追加するタグ

        Returns:
            None
        """
        async for record in self._queue_in:
            record.update(tags)
            try:
                response = self.client.put_record(
                    StreamName=stream_name,
                    Data=record,
                    PartitionKey="default"
                )
                self._logger.info(f"Published to Kinesis: {response}")
                self._is_healthy = True
            except Exception as e:
                self._logger.error(f"Failed to publish to Kinesis: {e}")
                self._is_healthy = False

    def get_shard_iterator(
        self, stream_name: str, shard_id: str, iterator_type: str = "LATEST"
    ) -> str:
        """
        Shard Iteratorを取得する。

        Args:
            stream_name (str): Kinesisストリームの名前
            shard_id (str): シャードID
            iterator_type (str): イテレーターのタイプ ('LATEST', 'TRIM_HORIZON', etc.)

        Returns:
            str: Shard Iterator
        """
        response = self._client.get_shard_iterator(
            StreamName=stream_name, ShardId=shard_id, ShardIteratorType=iterator_type
        )
        return response["ShardIterator"]

    def get_records(self, shard_iterator: str, limit: int = 10) -> List[Dict]:
        """
        レコードを取得する。

        Args:
            shard_iterator (str): Shard Iterator
            limit (int): 取得するレコードの最大数

        Returns:
            List[Dict]: 取得したレコード
        """
        response = self._client.get_records(
            ShardIterator=shard_iterator, Limit=limit
        )
        return response["Records"]

    def subscribe(
        self,
        stream_name: str,
        shard_id: str,
        iterator_type: str = "LATEST",
        limit: int = 10,
    ) -> List[Dict]:
        """
        Kinesisストリームを購読し、データを取得する。

        Args:
            stream_name (str): Kinesisストリームの名前
            shard_id (str): シャードID
            iterator_type (str): イテレーターのタイプ ('LATEST', 'TRIM_HORIZON', etc.)
            limit (int): 取得するレコードの最大数

        Returns:
            List[Dict]: 取得したレコード
        """
        shard_iterator = self.get_shard_iterator(stream_name, shard_id, iterator_type)
        records = self.get_records(shard_iterator, limit)
        return records
