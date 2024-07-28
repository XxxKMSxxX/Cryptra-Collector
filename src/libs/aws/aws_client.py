import os

import boto3

from src.libs.utils import LogManager


class AwsClient:
    def __init__(self, session_name: str):
        """
        Credentialsクラスのコンストラクタ

        Args:
            session_name (str): セッション名
        """
        self._load_env()
        self._session_name = session_name
        self._credentials = self.assume_role()

    def _load_env(self):
        """
        環境変数からAWSの設定を読み込む

        Raises:
            EnvironmentError: 環境変数の取得に失敗した場合
        """
        self._aws_role_arn = os.getenv("AWS_ROLE_ARN")
        self._aws_region = os.getenv("AWS_REGION")
        LogManager.add_masked_credentials(
            {"AWS_ROLE_ARN": self._aws_role_arn, "AWS_REGION": self._aws_region}
        )

        if not self._aws_role_arn or not self._aws_region:
            raise EnvironmentError(
                "環境変数 'AWS_ROLE_ARN' または 'AWS_REGION' が設定されていません"
            )

    def assume_role(self):
        """
        STSを使用して指定されたロールを引き受け、一時的なセキュリティ認証情報を取得する

        Returns:
            dict: 一時的なセキュリティ認証情報
        """
        sts_client = boto3.client("sts")
        assumed_role = sts_client.assume_role(
            RoleArn=self._aws_role_arn, RoleSessionName=self._session_name
        )
        return assumed_role["Credentials"]

    def get_boto3_client(self, service_name: str):
        """
        指定されたサービスのboto3クライアントを取得する

        Args:
            service_name (str): サービス名 (例: 's3', 'kinesis')

        Returns:
            boto3.client: 指定されたサービスのboto3クライアント
        """
        return boto3.client(
            service_name,
            region_name=self._aws_region,
            aws_access_key_id=self._credentials["AccessKeyId"],
            aws_secret_access_key=self._credentials["SecretAccessKey"],
            aws_session_token=self._credentials["SessionToken"],
        )
