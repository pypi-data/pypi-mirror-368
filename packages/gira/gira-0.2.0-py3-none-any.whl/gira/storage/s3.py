"""S3-compatible storage backend implementation."""

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, Optional, Union

from gira.storage.base import (
    DownloadProgress,
    StorageBackend,
    StorageObject,
    UploadProgress,
)
from gira.storage.exceptions import (
    StorageAuthenticationError,
    StorageConnectionError,
    StorageError,
    StorageNotFoundError,
    StoragePermissionError,
)
from gira.storage.retry import retry_with_config, RetryConfig
from gira.storage.utils import (
    calculate_checksum,
    detect_content_type,
    verify_checksum,
)

try:
    import boto3
    from botocore.exceptions import (
        BotoCoreError,
        ClientError,
        NoCredentialsError,
        ParamValidationError,
    )
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None
    BotoCoreError = Exception
    ClientError = Exception
    NoCredentialsError = Exception
    ParamValidationError = Exception


class S3Backend(StorageBackend):
    """Storage backend for S3-compatible services.
    
    Supports:
    - AWS S3
    - Cloudflare R2
    - Backblaze B2
    - MinIO
    - Any S3-compatible API
    """
    
    # Multipart upload threshold and chunk size
    MULTIPART_THRESHOLD = 5 * 1024 * 1024  # 5MB
    MULTIPART_CHUNK_SIZE = 5 * 1024 * 1024  # 5MB
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize S3 backend.
        
        Config keys:
            bucket: S3 bucket name (required)
            region: AWS region (default: us-east-1)
            endpoint_url: Custom endpoint for S3-compatible services
            access_key_id: AWS access key ID
            secret_access_key: AWS secret access key
            session_token: Optional session token
            use_ssl: Whether to use SSL (default: True)
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        if not BOTO3_AVAILABLE:
            raise ImportError(
                "boto3 is required for S3 backend. Install with: pip install boto3"
            )
        
        super().__init__(config)
        self._client = None
        self._resource = None
        
    def _validate_config(self) -> None:
        """Validate S3 configuration."""
        if "bucket" not in self.config:
            raise StorageError("Missing required config: bucket")
        
        # Set defaults
        self.config.setdefault("region", "us-east-1")
        self.config.setdefault("use_ssl", True)
        self.config.setdefault("verify_ssl", True)
        
    @property
    def client(self):
        """Get or create S3 client."""
        if self._client is None:
            self._client = self._create_client()
        return self._client
    
    @property
    def resource(self):
        """Get or create S3 resource."""
        if self._resource is None:
            self._resource = self._create_resource()
        return self._resource
    
    @property
    def bucket(self):
        """Get bucket name."""
        return self.config["bucket"]
    
    @property
    def region(self):
        """Get region name."""
        return self.config.get("region", "us-east-1")
    
    @property
    def endpoint_url(self):
        """Get endpoint URL."""
        return self.config.get("endpoint_url")
    
    def _create_client(self):
        """Create boto3 S3 client."""
        try:
            # Build client configuration
            client_config = {
                "service_name": "s3",
                "region_name": self.config.get("region"),
                "use_ssl": self.config.get("use_ssl", True),
                "verify": self.config.get("verify_ssl", True),
            }
            
            # Add endpoint URL for S3-compatible services
            if "endpoint_url" in self.config:
                client_config["endpoint_url"] = self.config["endpoint_url"]
            
            # Add credentials if provided
            if "access_key_id" in self.config:
                client_config.update({
                    "aws_access_key_id": self.config["access_key_id"],
                    "aws_secret_access_key": self.config["secret_access_key"],
                })
                
                if "session_token" in self.config:
                    client_config["aws_session_token"] = self.config["session_token"]
            
            return boto3.client(**client_config)
            
        except NoCredentialsError as e:
            raise StorageAuthenticationError(
                "No AWS credentials found. Configure credentials or set "
                "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
            ) from e
        except Exception as e:
            raise StorageConnectionError(f"Failed to create S3 client: {e}") from e
    
    def _create_resource(self):
        """Create boto3 S3 resource."""
        try:
            # Build resource configuration (similar to client)
            resource_config = {
                "service_name": "s3",
                "region_name": self.config.get("region"),
                "use_ssl": self.config.get("use_ssl", True),
                "verify": self.config.get("verify_ssl", True),
            }
            
            if "endpoint_url" in self.config:
                resource_config["endpoint_url"] = self.config["endpoint_url"]
            
            if "access_key_id" in self.config:
                resource_config.update({
                    "aws_access_key_id": self.config["access_key_id"],
                    "aws_secret_access_key": self.config["secret_access_key"],
                })
                
                if "session_token" in self.config:
                    resource_config["aws_session_token"] = self.config["session_token"]
            
            return boto3.resource(**resource_config)
            
        except Exception as e:
            raise StorageConnectionError(f"Failed to create S3 resource: {e}") from e
    
    @retry_with_config(RetryConfig(retryable_exceptions=(ClientError, BotoCoreError)))
    def upload(
        self,
        file_path: Union[str, Path],
        object_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        progress_callback: Optional[Callable[[UploadProgress], None]] = None,
    ) -> StorageObject:
        """Upload a file to S3."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Detect content type if not provided
        if content_type is None:
            content_type = detect_content_type(file_path)
        
        # Calculate checksum
        checksum = calculate_checksum(file_path, algorithm="sha256")
        
        # Prepare metadata
        s3_metadata = metadata or {}
        s3_metadata["sha256"] = checksum
        
        # Prepare extra arguments
        extra_args = {
            "ContentType": content_type,
            "Metadata": s3_metadata,
        }
        
        file_size = file_path.stat().st_size
        
        try:
            if file_size > self.MULTIPART_THRESHOLD:
                # Use multipart upload for large files
                self._multipart_upload(
                    file_path, object_key, extra_args, progress_callback
                )
            else:
                # Simple upload for small files
                self._simple_upload(
                    file_path, object_key, extra_args, progress_callback
                )
            
            # Get object metadata
            response = self.client.head_object(
                Bucket=self.config["bucket"],
                Key=object_key,
            )
            
            return StorageObject(
                key=object_key,
                size=file_size,
                content_type=content_type,
                last_modified=response.get("LastModified", datetime.utcnow()),
                etag=response.get("ETag", "").strip('"'),
                metadata=s3_metadata,
            )
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "AccessDenied":
                raise StoragePermissionError(f"Access denied: {e}") from e
            elif error_code == "NoSuchBucket":
                raise StorageError(f"Bucket not found: {self.config['bucket']}") from e
            else:
                raise StorageError(f"Upload failed: {e}") from e
        except Exception as e:
            raise StorageError(f"Upload failed: {e}") from e
    
    def _simple_upload(
        self,
        file_path: Path,
        object_key: str,
        extra_args: Dict[str, Any],
        progress_callback: Optional[Callable[[UploadProgress], None]] = None,
    ) -> None:
        """Simple upload for small files."""
        file_size = file_path.stat().st_size
        
        if progress_callback:
            class ProgressWrapper:
                def __init__(self, callback, total_size):
                    self.callback = callback
                    self.total_size = total_size
                    self.bytes_uploaded = 0
                
                def __call__(self, bytes_amount):
                    self.bytes_uploaded += bytes_amount
                    progress = UploadProgress(
                        bytes_uploaded=self.bytes_uploaded,
                        total_bytes=self.total_size,
                        percentage=(self.bytes_uploaded / self.total_size) * 100,
                    )
                    self.callback(progress)
            
            callback = ProgressWrapper(progress_callback, file_size)
            
            self.client.upload_file(
                str(file_path),
                self.config["bucket"],
                object_key,
                ExtraArgs=extra_args,
                Callback=callback,
            )
        else:
            self.client.upload_file(
                str(file_path),
                self.config["bucket"],
                object_key,
                ExtraArgs=extra_args,
            )
    
    def _multipart_upload(
        self,
        file_path: Path,
        object_key: str,
        extra_args: Dict[str, Any],
        progress_callback: Optional[Callable[[UploadProgress], None]] = None,
    ) -> None:
        """Multipart upload for large files."""
        file_size = file_path.stat().st_size
        bytes_uploaded = 0
        
        # Initiate multipart upload
        response = self.client.create_multipart_upload(
            Bucket=self.config["bucket"],
            Key=object_key,
            **extra_args,
        )
        upload_id = response["UploadId"]
        
        parts = []
        
        try:
            with open(file_path, "rb") as f:
                part_number = 1
                
                while True:
                    data = f.read(self.MULTIPART_CHUNK_SIZE)
                    if not data:
                        break
                    
                    # Upload part
                    response = self.client.upload_part(
                        Bucket=self.config["bucket"],
                        Key=object_key,
                        PartNumber=part_number,
                        UploadId=upload_id,
                        Body=data,
                    )
                    
                    parts.append({
                        "PartNumber": part_number,
                        "ETag": response["ETag"],
                    })
                    
                    bytes_uploaded += len(data)
                    
                    if progress_callback:
                        progress = UploadProgress(
                            bytes_uploaded=bytes_uploaded,
                            total_bytes=file_size,
                            percentage=(bytes_uploaded / file_size) * 100,
                        )
                        progress_callback(progress)
                    
                    part_number += 1
            
            # Complete multipart upload
            self.client.complete_multipart_upload(
                Bucket=self.config["bucket"],
                Key=object_key,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts},
            )
            
        except Exception as e:
            # Abort multipart upload on error
            self.client.abort_multipart_upload(
                Bucket=self.config["bucket"],
                Key=object_key,
                UploadId=upload_id,
            )
            raise
    
    @retry_with_config(RetryConfig(retryable_exceptions=(ClientError, BotoCoreError)))
    def download(
        self,
        object_key: str,
        file_path: Union[str, Path],
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None,
    ) -> Path:
        """Download an object from S3."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Get object size
            response = self.client.head_object(
                Bucket=self.config["bucket"],
                Key=object_key,
            )
            file_size = response["ContentLength"]
            expected_checksum = response.get("Metadata", {}).get("sha256")
            
            if progress_callback:
                class ProgressWrapper:
                    def __init__(self, callback, total_size):
                        self.callback = callback
                        self.total_size = total_size
                        self.bytes_downloaded = 0
                    
                    def __call__(self, bytes_amount):
                        self.bytes_downloaded += bytes_amount
                        progress = DownloadProgress(
                            bytes_downloaded=self.bytes_downloaded,
                            total_bytes=self.total_size,
                            percentage=(self.bytes_downloaded / self.total_size) * 100,
                        )
                        self.callback(progress)
                
                callback = ProgressWrapper(progress_callback, file_size)
                
                self.client.download_file(
                    self.config["bucket"],
                    object_key,
                    str(file_path),
                    Callback=callback,
                )
            else:
                self.client.download_file(
                    self.config["bucket"],
                    object_key,
                    str(file_path),
                )
            
            # Verify checksum if available
            if expected_checksum:
                verify_checksum(file_path, expected_checksum, algorithm="sha256")
            
            return file_path
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "NoSuchKey":
                # Don't wrap in StorageError for proper retry handling
                raise StorageNotFoundError(f"Object not found: {object_key}") from e
            elif error_code == "AccessDenied":
                raise StoragePermissionError(f"Access denied: {e}") from e
            else:
                raise
        except Exception as e:
            raise StorageError(f"Download failed: {e}") from e
    
    @retry_with_config(RetryConfig(retryable_exceptions=(ClientError, BotoCoreError)))
    def delete(self, object_key: str) -> None:
        """Delete an object from S3."""
        try:
            self.client.delete_object(
                Bucket=self.config["bucket"],
                Key=object_key,
            )
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "NoSuchKey":
                raise StorageNotFoundError(f"Object not found: {object_key}") from e
            elif error_code == "AccessDenied":
                raise StoragePermissionError(f"Access denied: {e}") from e
            else:
                raise StorageError(f"Delete failed: {e}") from e
        except Exception as e:
            raise StorageError(f"Delete failed: {e}") from e
    
    def exists(self, object_key: str) -> bool:
        """Check if an object exists in S3."""
        try:
            self.client.head_object(
                Bucket=self.config["bucket"],
                Key=object_key,
            )
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "404" or error_code == "NoSuchKey":
                return False
            else:
                # For other errors, use retry decorator
                @retry_with_config(RetryConfig(retryable_exceptions=(ClientError, BotoCoreError)))
                def _retry_head():
                    self.client.head_object(
                        Bucket=self.config["bucket"],
                        Key=object_key,
                    )
                    return True
                
                return _retry_head()
        except Exception as e:
            raise StorageError(f"Existence check failed: {e}") from e
    
    @retry_with_config(RetryConfig(retryable_exceptions=(ClientError, BotoCoreError)))
    def get_metadata(self, object_key: str) -> StorageObject:
        """Get metadata for an object."""
        try:
            response = self.client.head_object(
                Bucket=self.config["bucket"],
                Key=object_key,
            )
            
            return StorageObject(
                key=object_key,
                size=response["ContentLength"],
                content_type=response.get("ContentType", "application/octet-stream"),
                last_modified=response.get("LastModified", datetime.utcnow()),
                etag=response.get("ETag", "").strip('"'),
                metadata=response.get("Metadata", {}),
            )
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "NoSuchKey":
                raise StorageNotFoundError(f"Object not found: {object_key}") from e
            elif error_code == "AccessDenied":
                raise StoragePermissionError(f"Access denied: {e}") from e
            else:
                raise StorageError(f"Metadata retrieval failed: {e}") from e
        except Exception as e:
            raise StorageError(f"Metadata retrieval failed: {e}") from e
    
    @retry_with_config(RetryConfig(retryable_exceptions=(ClientError, BotoCoreError)))
    def list_objects(
        self,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> Iterator[StorageObject]:
        """List objects in S3."""
        try:
            paginator = self.client.get_paginator("list_objects_v2")
            
            params = {
                "Bucket": self.config["bucket"],
            }
            
            if prefix:
                params["Prefix"] = prefix
            if delimiter:
                params["Delimiter"] = delimiter
            if max_results:
                params["MaxKeys"] = min(max_results, 1000)  # S3 limit
            
            count = 0
            
            for page in paginator.paginate(**params):
                if "Contents" not in page:
                    continue
                
                for obj in page["Contents"]:
                    yield StorageObject(
                        key=obj["Key"],
                        size=obj["Size"],
                        content_type="application/octet-stream",  # Not provided in listing
                        last_modified=obj["LastModified"],
                        etag=obj.get("ETag", "").strip('"'),
                        metadata=None,  # Not provided in listing
                    )
                    
                    count += 1
                    if max_results and count >= max_results:
                        return
                        
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "AccessDenied":
                raise StoragePermissionError(f"Access denied: {e}") from e
            else:
                raise StorageError(f"List failed: {e}") from e
        except Exception as e:
            raise StorageError(f"List failed: {e}") from e
    
    @retry_with_config(RetryConfig(retryable_exceptions=(ClientError, BotoCoreError)))
    def generate_presigned_url(
        self,
        object_key: str,
        expiration: int = 3600,
        method: str = "GET",
    ) -> str:
        """Generate a presigned URL for temporary access."""
        try:
            client_method = {
                "GET": "get_object",
                "PUT": "put_object",
                "DELETE": "delete_object",
            }.get(method.upper())
            
            if not client_method:
                raise ValueError(f"Unsupported method: {method}")
            
            url = self.client.generate_presigned_url(
                ClientMethod=client_method,
                Params={
                    "Bucket": self.config["bucket"],
                    "Key": object_key,
                },
                ExpiresIn=expiration,
            )
            
            return url
            
        except ClientError as e:
            raise StorageError(f"URL generation failed: {e}") from e
        except Exception as e:
            raise StorageError(f"URL generation failed: {e}") from e
    
    def test_connection(self) -> bool:
        """Test if the S3 connection is working."""
        try:
            # Try to list buckets or head the configured bucket
            self.client.head_bucket(Bucket=self.config["bucket"])
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "NoSuchBucket":
                raise StorageError(f"Bucket not found: {self.config['bucket']}") from e
            elif error_code in ["AccessDenied", "Forbidden"]:
                # Bucket exists but we don't have permission to HEAD it
                # Try a different operation
                try:
                    # Try listing with max 1 result
                    list(self.list_objects(max_results=1))
                    return True
                except:
                    return False
            return False
        except NoCredentialsError:
            raise StorageAuthenticationError("No AWS credentials configured")
        except Exception:
            return False
    
    @retry_with_config(RetryConfig(retryable_exceptions=(ClientError, BotoCoreError)))
    def copy(
        self,
        source_key: str,
        destination_key: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> StorageObject:
        """Copy an object within S3 (server-side copy)."""
        try:
            # Get source metadata
            source_obj = self.get_metadata(source_key)
            
            # Prepare copy source
            copy_source = {
                "Bucket": self.config["bucket"],
                "Key": source_key,
            }
            
            # Use metadata from source if not provided
            if metadata is None:
                metadata = source_obj.metadata or {}
            
            # Server-side copy
            self.client.copy_object(
                CopySource=copy_source,
                Bucket=self.config["bucket"],
                Key=destination_key,
                ContentType=source_obj.content_type,
                Metadata=metadata,
                MetadataDirective="REPLACE",
            )
            
            return self.get_metadata(destination_key)
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "NoSuchKey":
                raise StorageNotFoundError(f"Source object not found: {source_key}") from e
            elif error_code == "AccessDenied":
                raise StoragePermissionError(f"Access denied: {e}") from e
            else:
                raise StorageError(f"Copy failed: {e}") from e
        except Exception as e:
            raise StorageError(f"Copy failed: {e}") from e