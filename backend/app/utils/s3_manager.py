import boto3
import asyncio
from concurrent.futures import ThreadPoolExecutor

class S3Client:
    def __init__(self, access_key: str, secret_key: str, endpoint_url: str, bucket_name: str):
        self.bucket_name = bucket_name
        session = boto3.session.Session()
        self.client = session.client(
            service_name='s3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.executor = ThreadPoolExecutor()

    async def upload_file(self, key: str, file_data: bytes) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self._upload_file_sync,
            key,
            file_data
        )

    def _upload_file_sync(self, key: str, file_data: bytes) -> None:
        self.client.put_object(Bucket=self.bucket_name, Key=key, Body=file_data)

    def _list_objects_sync(self):
        response = self.client.list_objects(Bucket=self.bucket_name)
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        return []

    async def list_objects(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._list_objects_sync)

    def _get_file_sync(self, key: str) -> bytes:
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=key)
            return response['Body'].read()
        except Exception as e:
            raise e

    async def get_file(self, key: str) -> bytes:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._get_file_sync, key)
