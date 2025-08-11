from __future__ import annotations

import os
import tempfile
from urllib.parse import urlparse

import rasterio
from boto3 import Session
from botocore.exceptions import ClientError
from botocore.response import StreamingBody
from rasterio.session import AWSSession

from digitalarzengine.utils.singletons import da_logger
from typing import List, Optional, Any


class S3Manager:
    """
      Manages interaction with AWS S3 for uploading, downloading, reading, writing,
      and listing objects using boto3 and rasterio.
      """
    session: Session

    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, region_name: str):
        self.session = Session(
            aws_access_key_id,
            aws_secret_access_key,
            region_name=region_name
        )
        self._s3_resource = self.session.resource("s3")

    def get_s3_resource(self):
        return self._s3_resource

    def get_session(self):
        return self.session

    def get_resource_file(self, object_uri: str) -> StreamingBody | None:
        """
        Stream a file from S3 without downloading it. Useful for in-memory reading.
       """
        try:
            bucket_name, object_name = self.get_bucket_name_and_path(object_uri)
            bucket = self._s3_resource.Bucket(bucket_name)
            for obj in bucket.objects.filter(Prefix=object_name):
                return obj.get()['Body']
        except Exception as e:
            da_logger.error(f"Error fetching resource file from {object_uri}: {e}")
        return None

    def is_file_exists(self, object_uri: str) -> bool:
        """
        Check if a file exists in the given S3 path.
        """
        try:
            bucket_name, object_name = self.get_bucket_name_and_path(object_uri)
            bucket = self._s3_resource.Bucket(bucket_name)
            objs = list(bucket.objects.filter(Prefix=object_name))
            return len(objs) > 0
        except Exception as e:
            da_logger.error(f"Error checking file existence for {object_uri}: {e}")
            return False

    def get_files_list_dir(self, object_uri: str) -> List[Any]:
        """
        List all files in a directory-like prefix in an S3 bucket.
        """
        try:
            bucket_name, object_name = self.get_bucket_name_and_path(object_uri)
            bucket = self._s3_resource.Bucket(bucket_name)
            return list(bucket.objects.filter(Prefix=object_name))
        except Exception as e:
            da_logger.error(f"Error listing files under {object_uri}: {e}")
            return []

    def upload_file(self, src_fp: str, des_path_uri: str) -> bool:
        """
        Upload a local file to a given S3 URI.
        """
        try:
            bucket_name, object_path = self.get_bucket_name_and_path(des_path_uri)
            self.session.client("s3").upload_file(src_fp, bucket_name, object_path)
            da_logger.info(f"Uploaded {src_fp} to {des_path_uri}")
            return True
        except ClientError as e:
            da_logger.exception(f"Upload failed: {e}")
            return False

    def delete_file(self, uri: str) -> bool:
        """
        Delete an object from S3.
        """
        try:
            bucket_name, object_name = self.get_bucket_name_and_path(uri)
            self.session.client("s3").delete_object(Bucket=bucket_name, Key=object_name)
            da_logger.info(f"Deleted file {uri}")
            return True
        except ClientError as e:
            da_logger.exception(f"Deletion failed for {uri}: {e}")
            return False

    def download_file(self, uri: str, download_dir_path: str) -> str | None:
        """
        Download an S3 object and save it locally, keeping its path structure.
        Skip downloading if the file already exists.
        """
        try:
            bucket_name, object_name = self.get_bucket_name_and_path(uri)
            download_file_path = os.path.join(download_dir_path, object_name)
            os.makedirs(os.path.dirname(download_file_path), exist_ok=True)

            # Skip if file already exists
            if os.path.exists(download_file_path):
                da_logger.info(f"Skipping download; file already exists: {download_file_path}")
                return download_file_path

            self.session.client("s3").download_file(
                Bucket=bucket_name, Key=object_name, Filename=download_file_path
            )
            da_logger.info(f"Downloaded {uri} to {download_file_path}")
            return download_file_path

        except ClientError as e:
            da_logger.exception(f"Download failed for {uri}: {e}")
            return None

    def read_file(self, object_uri: str) -> str | None:
        """
        Read content of a text-based S3 object into memory (as UTF-8 string).
        Ideal for reading small configs, JSONs, etc.
        """
        try:
            bucket_name, object_name = self.get_bucket_name_and_path(object_uri)
            bucket = self._s3_resource.Bucket(bucket_name)
            for obj in bucket.objects.filter(Prefix=object_name):
                return obj.get()['Body'].read().decode('utf-8')
        except Exception as e:
            da_logger.error(f"Read failed for {object_uri}: {e}")
        return None

    def write_file(self, content: str, des_uri: str) -> bool:
        """
        Write a string (in memory) directly to S3 without writing to disk first.
        Ideal for logs, configs, or dynamic content.
        """
        try:

            bucket_name, key = self.get_bucket_name_and_path(des_uri)
            result = self._s3_resource.Object(bucket_name, key).put(Body=content, ContentEncoding="utf-8")
            status = result.get('ResponseMetadata', {}).get('HTTPStatusCode', 0)
            if status == 200:
                da_logger.info(f"Successfully wrote to {des_uri}")
                return True
            else:
                da_logger.error(f"Write failed for {des_uri} with status {status}")
        except Exception as e:
            da_logger.exception(f"Error writing file to {des_uri}: {e}")
        return False

    def get_rio_dataset(self, url: str) -> Optional[rasterio.io.DatasetReader]:
        """
        Open a remote or local raster file using rasterio.
        """
        try:
            # For tests: handle local paths directly
            if not url.startswith("s3://"):
                raster = rasterio.open(url)
                return raster

            # For S3 URLs: attempt to use AWS session
            with rasterio.Env(AWSSession(self.session)):
                raster = rasterio.open(url)
                if not raster.crs:
                    da_logger.warning(f"No CRS found in {url}")
                    raster = self.convert_tiff_to_geo_tiff(raster, url)
                    if raster is None:
                        return None
                return raster
        except Exception as e:
            da_logger.exception(f"Failed to open raster {url}: {e}")
            return None


    @staticmethod
    def get_s3_uri(s3_bucket_name: str, rel_file_path: str) -> str:
        """
        Build a proper S3 URI from bucket and relative path.
        """
        return f"s3://{s3_bucket_name}/{rel_file_path}"

    @staticmethod
    def get_bucket_name_and_path(uri: str) -> tuple[str, str]:
        """
        Parse an S3 URI and return (bucket_name, key/path).
        """
        parsed = urlparse(uri)
        if parsed.scheme != "s3":
            raise ValueError(f"Invalid URI scheme in {uri}. Expected s3://")
        bucket = parsed.netloc
        key = parsed.path.lstrip('/')
        return bucket, key

    def get_file_size(self, uri: str) -> int | None:
        """
        Get size (in bytes) of an S3 object.
        """
        try:
            bucket_name, object_name = self.get_bucket_name_and_path(uri)
            response = self.session.client("s3").head_object(Bucket=bucket_name, Key=object_name)
            return response['ContentLength']
        except ClientError as e:
            da_logger.exception(f"Could not get size for {uri}: {e}")
            return None

    def generate_presigned_url(self, uri: str, expires_in: int = 3600) -> str | None:
        try:
            bucket, key = self.get_bucket_name_and_path(uri)
            url = self.session.client("s3").generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            da_logger.exception(f"Error generating presigned URL for {uri}: {e}")
            return None

    def convert_tiff_to_geo_tiff(
            self,
            raster: rasterio.io.DatasetReader,
            url: str,
            crs: str = 'EPSG:4326'
    ) -> Optional[rasterio.io.DatasetReader]:
        """
        Assign a CRS to a raster and return a valid GeoTIFF dataset.

        Parameters:
            raster: The original rasterio dataset without CRS.
            url: The original file path (for logging).
            crs: The CRS to assign (e.g., 'EPSG:4326').

        Returns:
            A rasterio dataset with CRS assigned.
        """
        try:
            with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp_file:
                tmp_path = tmp_file.name

            profile = raster.profile
            profile.update({'crs': crs})

            with rasterio.open(tmp_path, 'w', **profile) as dst:
                for i in range(1, raster.count + 1):
                    dst.write(raster.read(i), i)

            da_logger.info(f"Assigned CRS '{crs}' to raster from {url}")
            return rasterio.open(tmp_path)

        except Exception as e:
            da_logger.exception(f"Failed to convert TIFF to GeoTIFF for {url}: {e}")
            return None
