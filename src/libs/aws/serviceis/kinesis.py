from __future__ import annotations

from json import dumps
from typing import Dict, List
from authorization.aws_authorization import Authorization
import boto3

class Kinesis(Authorization):
    def __init__(self, session_name: str):
        """
        Kinesisクラスのコンストラクタ

        Args:
            session_name (str): セッション名
        """
        super().__init__(session_name)
        self._kinesis_client = self.get_boto3_client('kinesis')

    def publish(self, stream_name: str, record: Dict) -> dict:
        """
        レコードをKinesisストリームに送信する

        Args:
            stream_name (str): Kinesisストリームの名前
            record (Dict): 送信するレコード

        Returns:
            dict: Kinesisに送信した結果
        """
        return self._kinesis_client.put_record(
            StreamName=stream_name,
            Data=dumps(record),
            PartitionKey='partition_key'
        )

    def get_shard_iterator(self, stream_name: str, shard_id: str, iterator_type: str = 'LATEST') -> str:
        """
        Shard Iteratorを取得する

        Args:
            stream_name (str): Kinesisストリームの名前
            shard_id (str): シャードID
            iterator_type (str): イテレーターのタイプ ('LATEST', 'TRIM_HORIZON', etc.)

        Returns:
            str: Shard Iterator
        """
        response = self._kinesis_client.get_shard_iterator(
            StreamName=stream_name,
            ShardId=shard_id,
            ShardIteratorType=iterator_type
        )
        return response['ShardIterator']

    def get_records(self, shard_iterator: str, limit: int = 10) -> List[Dict]:
        """
        レコードを取得する

        Args:
            shard_iterator (str): Shard Iterator
            limit (int): 取得するレコードの最大数

        Returns:
            List[Dict]: 取得したレコード
        """
        response = self._kinesis_client.get_records(
            ShardIterator=shard_iterator,
            Limit=limit
        )
        return response['Records']

    def subscribe(
        self, stream_name: str,
        shard_id: str,
        iterator_type: str = 'LATEST',
        limit: int = 10
    ) -> List[Dict]:
        """
        Kinesisストリームを購読し、データを取得する

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
