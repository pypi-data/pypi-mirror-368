import boto3
import polars as pl
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from typing import List


class FileHandler:
    def __init__(self, bucket: str, region: str = 'ap-northeast-2'):
        self.bucket = bucket
        self.s3 = boto3.client('s3', region_name=region)

    def get_object(self, key: str) -> pl.DataFrame:
        response = self.s3.get_object(Bucket=self.bucket, Key=key)
        file_obj = BytesIO(response['Body'].read())

        if key.endswith('.csv'):
            return pl.read_csv(file_obj)
        elif key.endswith('.parquet'):
            return pl.read_parquet(file_obj)
        else:
            raise ValueError(f"지원되지 않는 파일 형식입니다: {key}")

    def upload_file(self, file_path: str, destination_key: str, file_format: str = 'csv'):
        if file_format not in ['csv', 'parquet']:
            raise ValueError("지원되지 않는 파일 형식입니다: csv 또는 parquet만 지원합니다.")

        if file_format == 'csv':
            df = pl.read_csv(file_path)
        else:
            df = pl.read_parquet(file_path)

        self.upload_dataframe(df, destination_key, file_format)

    def upload_dataframe(self, df: pl.DataFrame, destination_key: str, file_format: str = 'csv'):
        buffer = BytesIO()
        if file_format == 'csv':
            df.write_csv(buffer)
        elif file_format == 'parquet':
            df.write_parquet(buffer)
        else:
            raise ValueError("지원되지 않는 파일 형식입니다: csv 또는 parquet만 지원합니다.")

        buffer.seek(0)
        self.s3.upload_fileobj(buffer, self.bucket, destination_key)
        print(f"[S3] 데이터프레임 업로드 성공: s3://{self.bucket}/{destination_key}")

    def upload_dataframe_partitioned_by_range(self, df: pl.DataFrame, destination_prefix: str, partition_size: int = 100000):
        # 인덱스 컬럼 추가
        df = df.with_columns(pl.arange(0, df.height).alias("index"))

        # 인덱스를 기준으로 범위 파티셔닝
        for start in range(0, df.height, partition_size):
            end = min(start + partition_size, df.height)
            partition_df = df.slice(start, partition_size)

            buffer = BytesIO()
            partition_df.write_parquet(buffer, compression="snappy")
            buffer.seek(0)

            # S3 경로 설정 (파티션 구조)
            partition_path = f"{destination_prefix}/index={start}-{end}/data.snappy.parquet"

            # S3로 업로드
            self.s3.upload_fileobj(buffer, self.bucket, partition_path)
            print(f"[S3] 파티션 업로드 성공: s3://{self.bucket}/{partition_path}")

    def upload_dataframe_partitioned_by_update_date(self, df: pl.DataFrame, destination_prefix: str):
        if "update_date" not in df.columns:
            raise ValueError("'update_date' 컬럼이 존재하지 않습니다.")

        # update_date 컬럼 기준으로 그룹화
        unique_dates = df.select("update_date").unique().to_series().to_list()

        for date in unique_dates:
            partition_df = df.filter(pl.col("update_date") == date)

            buffer = BytesIO()
            partition_df.write_parquet(buffer, compression="snappy")
            buffer.seek(0)

            # S3 경로 설정 (update_date 기준 파티션 구조)
            partition_path = f"{destination_prefix}/update_date={date}/file.parquet"

            # S3로 업로드
            self.s3.upload_fileobj(buffer, self.bucket, partition_path)
            print(f"[S3] 파티션 업로드 성공: s3://{self.bucket}/{partition_path}")

    def list_keys(self, prefix: str) -> List[str]:
        """S3 버킷의 주어진 prefix 아래 모든 파일 키를 나열합니다."""
        paginator = self.s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.bucket, Prefix=prefix)
        keys = []
        for page in pages:
            for obj in page.get('Contents', []):
                key = obj['Key']
                if key.endswith('.csv') or key.endswith('.parquet'):
                    keys.append(key)
        return keys

    def load_all_objects_parallel(self, prefix: str, max_workers: int = 8) -> pl.DataFrame:
        """지정한 prefix 아래의 모든 parquet/csv 파일을 병렬로 불러와 하나의 DataFrame으로 합칩니다."""
        keys = self.list_keys(prefix)
        if not keys:
            raise FileNotFoundError(f"No supported files found in prefix: {prefix}")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            dfs = list(executor.map(self.get_object, keys))
        return pl.concat(dfs)

    def get_unload_object(self, key: str) -> pl.DataFrame:
        s3_uri = f's3://{self.bucket}/{key}'
        return pl.read_parquet(s3_uri)