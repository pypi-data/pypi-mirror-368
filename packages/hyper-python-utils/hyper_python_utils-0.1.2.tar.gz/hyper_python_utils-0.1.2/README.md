# Hyper Python Utils

AWS S3 and Athena utilities for data processing with Polars.

## Installation

```bash
pip install hyper-python-utils
```

## Features

- **FileHandler**: S3 file operations with Polars DataFrames
  - Upload/download CSV and Parquet files
  - Parallel loading of multiple files
  - Partitioned uploads by range or date
  - Support for compressed formats

- **QueryManager**: Athena query execution and management
  - Execute queries with result monitoring
  - Clean up query result files
  - Error handling and timeouts

## Quick Start

### FileHandler Usage

```python
from hyper_python_utils import FileHandler
import polars as pl

# Initialize FileHandler
handler = FileHandler(bucket="my-s3-bucket", region="ap-northeast-2")

# Read a file from S3
df = handler.get_object("data/sample.parquet")

# Upload a DataFrame to S3
sample_df = pl.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
handler.upload_dataframe(sample_df, "output/result.parquet", "parquet")

# Upload with partitioning by range
handler.upload_dataframe_partitioned_by_range(
    df, "partitioned_data/", partition_size=50000
)

# Load all files from a prefix in parallel
combined_df = handler.load_all_objects_parallel("data/batch_*/", max_workers=4)
```

### QueryManager Usage

```python
from hyper_python_utils import QueryManager, EmptyResultError
import polars as pl

# Initialize QueryManager with custom result prefix and auto cleanup
query_manager = QueryManager(
    bucket="my-athena-results",
    result_prefix="custom/query_results/",
    auto_cleanup=True  # Default: True - automatically delete query result files after reading
)

# Method 1: Execute query and get DataFrame result directly (recommended)
query = "SELECT * FROM my_table LIMIT 100"
try:
    df = query_manager.query(query, database="my_database")
    print(df)
except EmptyResultError:
    print("Query returned no results")

# Method 2: Manual query execution with result retrieval
query_id = query_manager.execute(query, database="my_database")
result_location = query_manager.wait_for_completion(query_id)
df = query_manager.get_result(query_id)  # Auto cleanup based on QueryManager setting

# Method 2b: Override auto cleanup for specific query
df_no_cleanup = query_manager.get_result(query_id, auto_cleanup=False)  # Keep result file

# Method 3: Execute UNLOAD query and get list of output files
unload_query = """
UNLOAD (SELECT * FROM my_large_table)
TO 's3://my-bucket/unloaded-data/'
WITH (format = 'PARQUET', compression = 'SNAPPY')
"""
output_files = query_manager.unload(unload_query, database="my_database")
print(f"Unloaded files: {output_files}")

# Manual cleanup of old query results (if auto_cleanup is disabled)
query_manager.delete_query_results_by_prefix("s3://my-bucket/old-results/")

# Disable auto cleanup for all queries
query_manager_no_cleanup = QueryManager(
    bucket="my-athena-results",
    auto_cleanup=False
)
```

## Requirements

- Python >= 3.8
- boto3 >= 1.26.0
- polars >= 0.18.0

## AWS Configuration

Make sure your AWS credentials are configured either through:
- AWS CLI (`aws configure`)
- Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- IAM roles (when running on EC2)

Required permissions:
- S3: `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`, `s3:DeleteObject`
- Athena: `athena:StartQueryExecution`, `athena:GetQueryExecution`

## License

MIT License