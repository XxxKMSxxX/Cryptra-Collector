from __future__ import annotations

from json import dumps
from typing import Dict
import boto3


class Kinesis:
    def __init__(self, aws_region):
        self._aws_region = aws_region
        self._kinesis_client = boto3.client(
            'kinesis', region_name=self._aws_region
        )

    def publish(self, stream_name: str, record: Dict):
        return self._kinesis_client.put_record(
            StreamName=stream_name,
            Records={
                'Data': dumps(record),
                'PartitionKey': 'partition_key'
            }
        )
