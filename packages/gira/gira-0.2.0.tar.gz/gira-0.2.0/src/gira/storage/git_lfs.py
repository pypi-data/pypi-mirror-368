"""Git LFS storage provider for Gira attachments.

This provider stores files directly in the Git repository using Git LFS,
which replaces large files with pointer files and stores the actual
content on the Git hosting provider's LFS server.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from gira.storage.base import StorageBackend, StorageObject
from gira.storage.exceptions import (
    StorageConfigurationError,
    StorageError,
    StorageNotFoundError,
)
from gira.storage.models import DownloadProgress, UploadProgress


class GitLFSStorage(StorageBackend):
    """Git LFS storage backend implementation.
    
    This backend stores files directly in the repository using Git LFS.
    Files are placed in .gira/attachments/{entity-id}/ and Git LFS
    handles converting them to pointer files.
    """
    
    def __init__(
        self,
        project_root: Optional[Path] = None,
        auto_track_extensions: Optional[List[str]] = None,
        size_warning_mb: float = 10.0,
        **kwargs
    ):
        """Initialize Git LFS storage backend.
        
        Args:
            project_root: Root directory of the Gira project
            auto_track_extensions: File extensions to automatically track with LFS
            size_warning_mb: File size in MB that triggers a warning
            **kwargs: Additional configuration options
        """
        self.project_root = project_root or Path.cwd()
        self.auto_track_extensions = auto_track_extensions or [
            "png", "jpg", "jpeg", "gif", "pdf", "zip", "tar", "gz",
            "mp4", "mov", "avi", "mp3", "wav", "exe", "dmg", "iso"
        ]
        self.size_warning_mb = size_warning_mb
        self.attachments_base = self.project_root / ".gira" / "attachments"
        
        # Validate Git LFS is installed and initialized
        self._validate_git_lfs()
    
    def _validate_git_lfs(self) -> None:
        """Validate that Git LFS is installed and initialized."""
        # Check if git is available
        try:
            subprocess.run(
                ["git", "--version"],
                check=True,
                capture_output=True,
                text=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise StorageConfigurationError(
                "Git is not installed or not in PATH"
            )
        
        # Check if Git LFS is installed
        try:
            result = subprocess.run(
                ["git", "lfs", "version"],
                check=True,
                capture_output=True,
                text=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise StorageConfigurationError(
                "Git LFS is not installed. Please install it with:\n"
                "  macOS: brew install git-lfs\n"
                "  Ubuntu: sudo apt-get install git-lfs\n"
                "  Windows: choco install git-lfs\n"
                "Then run: git lfs install"
            )
        
        # Check if Git LFS is initialized in the repository
        try:
            result = subprocess.run(
                ["git", "lfs", "env"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                # Try to initialize Git LFS
                subprocess.run(
                    ["git", "lfs", "install"],
                    cwd=self.project_root,
                    check=True
                )
        except subprocess.CalledProcessError:
            raise StorageConfigurationError(
                "Failed to initialize Git LFS in the repository"
            )
    
    def _ensure_lfs_tracking(self, file_path: Path) -> None:
        """Ensure file pattern is tracked by Git LFS."""
        extension = file_path.suffix.lstrip(".")
        if not extension or extension not in self.auto_track_extensions:
            return
        
        gitattributes_path = self.project_root / ".gitattributes"
        
        # Check if pattern is already tracked
        pattern = f"*.{extension}"
        lfs_attribute = f"{pattern} filter=lfs diff=lfs merge=lfs -text"
        
        if gitattributes_path.exists():
            content = gitattributes_path.read_text()
            if pattern in content and "filter=lfs" in content:
                return
        
        # Add LFS tracking for this extension
        try:
            subprocess.run(
                ["git", "lfs", "track", pattern],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            raise StorageError(f"Failed to track {pattern} with Git LFS: {e}")
    
    def _get_file_path(self, entity_id: str, filename: str) -> Path:
        """Get the full file path for an attachment."""
        return self.attachments_base / entity_id / filename
    
    def upload(
        self,
        file_path: Path,
        object_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[UploadProgress], None]] = None,
    ) -> StorageObject:
        """Upload a file to Git LFS storage.
        
        For Git LFS, the object_key should be in format:
        {entity-id}/{filename}
        """
        # Parse entity ID and filename from object key
        parts = object_key.split("/", 1)
        if len(parts) != 2:
            raise StorageError(f"Invalid object key format: {object_key}")
        
        entity_id, filename = parts
        
        # Create target directory
        target_dir = self.attachments_base / entity_id
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Target file path
        target_path = target_dir / filename
        
        # Check file size and warn if large
        file_size = file_path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        if size_mb > self.size_warning_mb:
            print(f"⚠️  Large file ({size_mb:.1f} MB) will be stored with Git LFS")
        
        # Ensure file type is tracked by LFS
        self._ensure_lfs_tracking(target_path)
        
        # Copy file to target location
        try:
            # Report progress during copy
            if progress_callback:
                bytes_copied = 0
                chunk_size = 1024 * 1024  # 1MB chunks
                
                with open(file_path, "rb") as src, open(target_path, "wb") as dst:
                    while True:
                        chunk = src.read(chunk_size)
                        if not chunk:
                            break
                        dst.write(chunk)
                        bytes_copied += len(chunk)
                        
                        progress = UploadProgress(
                            bytes_uploaded=bytes_copied,
                            bytes_total=file_size
                        )
                        progress_callback(progress)
            else:
                shutil.copy2(file_path, target_path)
        except Exception as e:
            raise StorageError(f"Failed to copy file: {e}")
        
        # Stage the file with git
        try:
            subprocess.run(
                ["git", "add", str(target_path.relative_to(self.project_root))],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            # Remove the file if git add failed
            target_path.unlink(missing_ok=True)
            raise StorageError(f"Failed to stage file with Git: {e}")
        
        # Also stage .gitattributes if it was modified
        gitattributes = self.project_root / ".gitattributes"
        if gitattributes.exists():
            try:
                subprocess.run(
                    ["git", "add", ".gitattributes"],
                    cwd=self.project_root,
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError:
                pass  # Non-critical if .gitattributes staging fails
        
        # Return storage object
        return StorageObject(
            key=object_key,
            size=file_size,
            content_type=content_type,
            metadata=metadata or {},
            last_modified=None,
            etag=None
        )
    
    def download(
        self,
        object_key: str,
        file_path: Path,
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None,
    ) -> None:
        """Download a file from Git LFS storage."""
        # Parse entity ID and filename
        parts = object_key.split("/", 1)
        if len(parts) != 2:
            raise StorageError(f"Invalid object key format: {object_key}")
        
        entity_id, filename = parts
        source_path = self.attachments_base / entity_id / filename
        
        if not source_path.exists():
            raise StorageNotFoundError(f"File not found: {object_key}")
        
        # Ensure Git LFS has the actual file content
        try:
            # Use git lfs pull to ensure we have the actual file
            subprocess.run(
                ["git", "lfs", "pull", "--include", str(source_path.relative_to(self.project_root))],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            raise StorageError(f"Failed to pull LFS content: {e}")
        
        # Copy file to target location
        try:
            file_size = source_path.stat().st_size
            
            if progress_callback:
                bytes_copied = 0
                chunk_size = 1024 * 1024  # 1MB chunks
                
                with open(source_path, "rb") as src, open(file_path, "wb") as dst:
                    while True:
                        chunk = src.read(chunk_size)
                        if not chunk:
                            break
                        dst.write(chunk)
                        bytes_copied += len(chunk)
                        
                        progress = DownloadProgress(
                            bytes_downloaded=bytes_copied,
                            bytes_total=file_size
                        )
                        progress_callback(progress)
            else:
                shutil.copy2(source_path, file_path)
        except Exception as e:
            raise StorageError(f"Failed to copy file: {e}")
    
    def delete(self, object_key: str) -> None:
        """Delete a file from Git LFS storage."""
        # Parse entity ID and filename
        parts = object_key.split("/", 1)
        if len(parts) != 2:
            raise StorageError(f"Invalid object key format: {object_key}")
        
        entity_id, filename = parts
        file_path = self.attachments_base / entity_id / filename
        
        if not file_path.exists():
            raise StorageNotFoundError(f"File not found: {object_key}")
        
        # Remove the file
        try:
            # Stage the removal with git
            subprocess.run(
                ["git", "rm", str(file_path.relative_to(self.project_root))],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            raise StorageError(f"Failed to remove file with Git: {e}")
        
        # Clean up empty directory
        entity_dir = self.attachments_base / entity_id
        if entity_dir.exists() and not any(entity_dir.iterdir()):
            entity_dir.rmdir()
    
    def exists(self, object_key: str) -> bool:
        """Check if a file exists in Git LFS storage."""
        parts = object_key.split("/", 1)
        if len(parts) != 2:
            return False
        
        entity_id, filename = parts
        file_path = self.attachments_base / entity_id / filename
        return file_path.exists()
    
    def list_objects(
        self,
        prefix: Optional[str] = None,
        max_results: Optional[int] = None
    ) -> List[StorageObject]:
        """List objects in Git LFS storage."""
        objects = []
        
        if not self.attachments_base.exists():
            return objects
        
        # If prefix is an entity ID, list only that entity's files
        if prefix and "/" not in prefix:
            entity_dir = self.attachments_base / prefix
            if entity_dir.exists() and entity_dir.is_dir():
                for file_path in entity_dir.iterdir():
                    if file_path.is_file():
                        object_key = f"{prefix}/{file_path.name}"
                        objects.append(StorageObject(
                            key=object_key,
                            size=file_path.stat().st_size,
                            content_type=None,
                            metadata={},
                            last_modified=None,
                            etag=None
                        ))
        else:
            # List all attachments
            for entity_dir in self.attachments_base.iterdir():
                if entity_dir.is_dir():
                    for file_path in entity_dir.iterdir():
                        if file_path.is_file():
                            object_key = f"{entity_dir.name}/{file_path.name}"
                            if not prefix or object_key.startswith(prefix):
                                objects.append(StorageObject(
                                    key=object_key,
                                    size=file_path.stat().st_size,
                                    content_type=None,
                                    metadata={},
                                    last_modified=None,
                                    etag=None
                                ))
        
        # Apply max_results limit
        if max_results:
            objects = objects[:max_results]
        
        return objects
    
    def get_url(self, object_key: str, expires_in: int = 3600) -> str:
        """Git LFS doesn't support presigned URLs."""
        raise NotImplementedError(
            "Git LFS storage does not support presigned URLs. "
            "Use the download method instead."
        )
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Git LFS connection and configuration."""
        try:
            # Check Git version
            git_result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True
            )
            git_version = git_result.stdout.strip()
            
            # Check Git LFS version
            lfs_result = subprocess.run(
                ["git", "lfs", "version"],
                capture_output=True,
                text=True
            )
            lfs_version = lfs_result.stdout.strip()
            
            # Check if we're in a Git repository
            repo_result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            in_git_repo = repo_result.returncode == 0
            
            # Check LFS tracking patterns
            tracking_result = subprocess.run(
                ["git", "lfs", "track"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            tracking_patterns = tracking_result.stdout.strip().split("\n") if tracking_result.returncode == 0 else []
            
            return {
                "success": True,
                "provider": "git-lfs",
                "git_version": git_version,
                "lfs_version": lfs_version,
                "in_git_repo": in_git_repo,
                "project_root": str(self.project_root),
                "attachments_path": str(self.attachments_base),
                "auto_track_extensions": self.auto_track_extensions,
                "tracking_patterns": tracking_patterns,
                "message": "Git LFS is properly configured"
            }
            
        except Exception as e:
            return {
                "success": False,
                "provider": "git-lfs",
                "error": str(e),
                "message": "Git LFS configuration error"
            }
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration - Git LFS doesn't need config validation."""
        pass
    
    def generate_presigned_url(self, object_key: str, expires_in: int = 3600) -> str:
        """Generate presigned URL - not supported for Git LFS."""
        raise NotImplementedError(
            "Git LFS storage does not support presigned URLs. "
            "Use the download method instead."
        )
    
    def get_metadata(self, object_key: str) -> Dict[str, Any]:
        """Get file metadata."""
        # Parse entity ID and filename
        parts = object_key.split("/", 1)
        if len(parts) != 2:
            raise StorageError(f"Invalid object key format: {object_key}")
        
        entity_id, filename = parts
        file_path = self.attachments_base / entity_id / filename
        
        if not file_path.exists():
            raise StorageNotFoundError(f"File not found: {object_key}")
        
        stat = file_path.stat()
        return {
            "size": stat.st_size,
            "last_modified": stat.st_mtime,
            "path": str(file_path),
        }