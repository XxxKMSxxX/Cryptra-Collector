from __future__ import annotations

from json import dumps
from typing import List, Dict
import boto3


class Kinesis:
    def __init__(self, aws_region):
        self._region = aws_region
        self._kinesis_client = boto3.client(
            'kinesis', region_name=self._region
        )

    def publish(self, stream_name: str, records: List[Dict]):
        entries = [{
            'Data': dumps(record),
            'PartitionKey': 'partition_key'
        } for record in records]

        response = self._kinesis_client.put_records(
            StreamName=stream_name,
            Records=entries
        )

        return response
