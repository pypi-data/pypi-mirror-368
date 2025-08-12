import boto3
import time
import io
import re
import polars as pl
from typing import Literal


class AthenaQueryError(Exception):
    pass


class EmptyResultError(Exception):
    pass


class QueryManager:
    def __init__(self, bucket: str, result_prefix: str = 'athena/query_results/', auto_cleanup: bool = True):
        self._bucket = bucket
        self._result_prefix = result_prefix
        self._s3_output = f's3://{bucket}/{result_prefix}'
        self._auto_cleanup = auto_cleanup
        self.athena = boto3.client('athena', region_name='ap-northeast-2')
        self.s3 = boto3.client('s3', region_name='ap-northeast-2')

    def execute(self, query: str, database: str) -> str:
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

    def get_result(self, query_id: str, auto_cleanup: bool = None) -> pl.DataFrame:
        response = self.athena.get_query_execution(QueryExecutionId=query_id)
        result_location = response['QueryExecution']['ResultConfiguration']['OutputLocation']
        
        # Extract bucket and key from S3 URL
        match = re.match(r's3://([^/]+)/(.+)', result_location)
        if not match:
            raise ValueError(f"Invalid S3 result location: {result_location}")
        
        bucket, key = match.groups()
        
        # Download CSV result from S3
        try:
            obj = self.s3.get_object(Bucket=bucket, Key=key)
            csv_content = obj['Body'].read().decode('utf-8')
            
            # Read CSV with polars
            df = pl.read_csv(io.StringIO(csv_content))
            
            # Check if DataFrame is empty
            if df.height == 0:
                raise EmptyResultError("Query returned no results")
            
            # Auto cleanup if enabled
            cleanup_enabled = auto_cleanup if auto_cleanup is not None else self._auto_cleanup
            if cleanup_enabled:
                try:
                    self.s3.delete_object(Bucket=bucket, Key=key)
                    # Also delete metadata file if exists
                    metadata_key = key + '.metadata'
                    try:
                        self.s3.delete_object(Bucket=bucket, Key=metadata_key)
                    except:
                        pass  # Metadata file might not exist
                    print(f"[S3] Cleaned up query result: {result_location}")
                except Exception as cleanup_error:
                    print(f"[S3] Warning: Failed to cleanup query result: {cleanup_error}")
            
            return df
        except Exception as e:
            raise AthenaQueryError(f"Failed to read query result: {str(e)}")

    def query(self, query: str, database: str, auto_cleanup: bool = None) -> pl.DataFrame:
        query_id = self.execute(query, database)
        self.wait_for_completion(query_id)
        return self.get_result(query_id, auto_cleanup=auto_cleanup)

    def unload(self, query: str, database: str) -> list[str]:
        query_id = self.execute(query, database)
        result_location = self.wait_for_completion(query_id)
        
        # Extract the base path for unloaded files
        match = re.match(r's3://([^/]+)/(.+)', result_location)
        if not match:
            raise ValueError(f"Invalid S3 result location: {result_location}")
        
        bucket, key_prefix = match.groups()
        
        # List all files that were created by the UNLOAD operation
        # UNLOAD creates files with names like: query_id/part-00000.parquet, query_id/part-00001.parquet, etc.
        base_prefix = key_prefix.rsplit('/', 1)[0] + '/'
        
        paginator = self.s3.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket, Prefix=base_prefix)
        
        unloaded_files = []
        for page in page_iterator:
            for obj in page.get('Contents', []):
                key = obj['Key']
                # Skip the metadata file created by Athena
                if not key.endswith('.metadata'):
                    unloaded_files.append(f's3://{bucket}/{key}')
        
        return unloaded_files

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