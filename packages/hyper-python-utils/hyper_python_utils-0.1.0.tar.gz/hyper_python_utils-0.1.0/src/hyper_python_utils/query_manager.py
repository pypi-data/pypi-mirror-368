import boto3
import time
import io
import re
import polars as pl
from typing import Literal


class AthenaQueryError(Exception):
    pass


class QueryManager:
    def __init__(self, bucket: str, results_prefix: str = 'athena/query_results/'):
        self._bucket = bucket
        self._results_prefix = results_prefix
        self._s3_output = f's3://{bucket}/{results_prefix}'
        self.athena = boto3.client('athena', region_name='ap-northeast-2')
        self.s3 = boto3.client('s3', region_name='ap-northeast-2')

    def run_query(self, query: str, database: str) -> str:
        response = self.athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': database},
            ResultConfiguration={'OutputLocation': self._s3_output}
        )
        return response['QueryExecutionId']

    def wait_for_completion(self, query_id: str, interval: int = 5, timeout: int = 300) -> str:
        start_time = time.time()
        while True:
            response = self.athena.get_query_execution(QueryExecutionId=query_id)
            status = response['QueryExecution']['Status']['State']
            if status == 'SUCCEEDED':
                print("[Athena] Query succeeded")
                break
            elif status in ['FAILED', 'CANCELLED']:
                reason = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
                raise AthenaQueryError(f"Query {status}: {reason}")
            elif (time.time() - start_time) > timeout:
                raise TimeoutError("Query timed out")
            print(f"[Athena] Query status: {status}..")
            time.sleep(interval)
        return response['QueryExecution']['ResultConfiguration']['OutputLocation']

    def execute_unload(self, query: str, database: str) -> list[str]:
        query_id = self.run_query(query, database)
        self.wait_for_completion(query_id)

    def delete_query_results_by_prefix(self, s3_prefix_url: str):
        match = re.match(r's3://([^/]+)/(.+)', s3_prefix_url.rstrip('/'))
        if not match:
            raise ValueError("Invalid S3 URL format")

        bucket, prefix = match.groups()

        paginator = self.s3.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

        deleted_any = False
        for page in page_iterator:
            for obj in page.get("Contents", []):
                key = obj["Key"]
                self.s3.delete_object(Bucket=bucket, Key=key)
                deleted_any = True

        if not deleted_any:
            print(f"[S3] No files found under prefix: {s3_prefix_url}")