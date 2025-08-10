import os
import pandas as pd
import polars as pl
import json
import pickle as pkl
import warnings
import boto3
from botocore.exceptions import ClientError
from typing import Union
from io import BytesIO, StringIO
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')

class S3CloudHelper:
    """
    A class to easily upload, download, and delete files from Amazon S3.

    Credentials can be managed in various ways. The boto3 library will automatically
    look for credentials in a specific order (e.g., environment variables,
    shared credentials file, IAM role). For simplicity, this example uses
    environment variables.
    """

    def __init__(self, obj: Union[pd.DataFrame, pl.DataFrame, dict, str, None] = None, path: str = None, region_name: str = AWS_REGION):
        if obj is not None and path is not None:
            raise ValueError("Only one of 'obj' or 'path' should be provided, not both.")

        self.obj = obj
        self.path = path
        self.s3_client = boto3.client('s3', region_name=region_name,
                                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    def _infer_file_type(self, file_name: str) -> Union[str, None]:
        ext = os.path.splitext(file_name)[1].lower()
        return {
            ".csv": "csv",
            ".json": "json",
            ".pkl": "pickle",
            ".pickle": "pickle",
            ".parquet": "parquet",
            ".pq": "parquet",
            ".txt": "txt",
        }.get(ext, None)

    def upload_to_s3(self, bucket_name: str, file_name: str, file_type: str = None):
        if file_type is None:
            file_type = self._infer_file_type(file_name)
            if file_type is None:
                raise ValueError(f"Cannot infer file_type from filename: {file_name}")

        if self.path:
            try:
                self.s3_client.upload_file(self.path, bucket_name, file_name)
            except ClientError as e:
                raise RuntimeError(f"Error uploading file from path: {e}")
        elif self.obj is not None:
            buffer = BytesIO()

            if file_type == "csv":
                if isinstance(self.obj, pd.DataFrame):
                    self.obj.to_csv(buffer, index=False)
                elif isinstance(self.obj, pl.DataFrame):
                    csv_data = self.obj.write_csv()
                    buffer.write(csv_data.encode('utf-8'))
                else:
                    raise ValueError("Only pandas or polars DataFrames supported for CSV.")
                buffer.seek(0)
                self.s3_client.upload_fileobj(buffer, bucket_name, file_name, ExtraArgs={'ContentType': 'text/csv'})

            elif file_type == "pickle":
                pkl.dump(self.obj, buffer)
                buffer.seek(0)
                self.s3_client.upload_fileobj(buffer, bucket_name, file_name, ExtraArgs={'ContentType': 'application/octet-stream'})

            elif file_type == "parquet":
                if isinstance(self.obj, pd.DataFrame):
                    self.obj.to_parquet(buffer, index=False)
                elif isinstance(self.obj, pl.DataFrame):
                    self.obj.write_parquet(buffer)
                else:
                    raise ValueError("Only pandas or polars DataFrames supported for Parquet.")
                buffer.seek(0)
                self.s3_client.upload_fileobj(buffer, bucket_name, file_name, ExtraArgs={'ContentType': 'application/octet-stream'})

            elif file_type == "txt" and isinstance(self.obj, str):
                self.s3_client.put_object(Body=self.obj.encode('utf-8'), Bucket=bucket_name, Key=file_name, ContentType='text/plain')

            elif file_type == "json":
                if not isinstance(self.obj, dict):
                    raise ValueError("For JSON uploads, `self.obj` must be a dictionary")
                json_str = json.dumps(self.obj, indent=2)
                self.s3_client.put_object(Body=json_str.encode('utf-8'), Bucket=bucket_name, Key=file_name, ContentType='application/json')

            else:
                raise ValueError(f"Unsupported combination of file_type='{file_type}' and object type.")
        else:
            raise ValueError("Either 'path' or 'obj' must be set.")
        
    def download_from_s3(self, s3_filepath: str, file_type: str = None, use_polars: bool = False):
        """
        Downloads a file from S3. Tries to infer file type if not specified.
        Set use_polars=True to return a polars.DataFrame instead of pandas.
        """
        try:
            # Handle both 's3://bucket/key' and 'bucket/key' formats
            if s3_filepath.startswith("s3://"):
                s3_filepath = s3_filepath[5:]
            
            bucket_name, *blob_path = s3_filepath.split("/", 1)
            blob_path = blob_path[0]
            
            response = self.s3_client.get_object(Bucket=bucket_name, Key=blob_path)
            data = response['Body'].read()
            
            buffer = BytesIO(data)

            if file_type is None:
                file_type = self._infer_file_type(blob_path)

            if file_type == "csv":
                if use_polars:
                    return pl.read_csv(buffer)
                return pd.read_csv(buffer)

            elif file_type == "pickle":
                return pkl.loads(data)

            elif file_type == "parquet":
                if use_polars:
                    return pl.read_parquet(buffer)
                return pd.read_parquet(buffer)

            elif file_type == "txt":
                return data.decode("utf-8")
            
            elif file_type == "json":
                return json.loads(data.decode("utf-8"))

            else:
                raise ValueError(f"Unsupported or unspecified file type for download: '{file_type}'")
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                warnings.warn(f"File not found @ s3://{bucket_name}/{blob_path}. Returning empty DataFrame.")
                return pl.DataFrame() if use_polars else pd.DataFrame()
            else:
                raise

    def delete_from_s3(self, bucket_name: str, file_name: str):
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                warnings.warn(f"No such file '{file_name}' found in bucket '{bucket_name}'.")
            else:
                raise