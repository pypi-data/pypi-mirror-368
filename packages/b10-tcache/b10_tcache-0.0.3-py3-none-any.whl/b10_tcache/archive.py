import os
import logging
import tarfile
from pathlib import Path

from .utils import timed_fn

logger = logging.getLogger(__name__)


class ArchiveError(Exception):
    """Archive operation failed."""

    pass


def validate_path(path: Path, allowed_prefixes: list[str]) -> None:
    """Validate path is within allowed directories."""
    resolved_path = str(path.resolve())

    if any(resolved_path.startswith(prefix) for prefix in allowed_prefixes):
        return

    raise ArchiveError(f"Path {resolved_path} outside allowed: {allowed_prefixes}")


def get_file_size_mb(file_path: Path) -> float:
    """Get file size in MB."""
    try:
        return file_path.stat().st_size / (1024 * 1024)
    except OSError:
        return 0.0


def _compress_directory_to_tar(source_dir: Path, target_file: Path) -> None:
    """Compress directory contents to a tar.gz file."""
    with tarfile.open(target_file, "w:gz", compresslevel=3) as tar:
        for item in source_dir.rglob("*"):
            if item.is_file():
                arcname = item.relative_to(source_dir)
                tar.add(item, arcname=arcname)


@timed_fn(logger=logger, name="Creating archive")
def create_archive(
    source_dir: Path, target_file: Path, max_size_mb: int = 1024
) -> None:
    """Create compressed archive safely."""
    # Validate paths
    validate_path(source_dir, ["/tmp/", str(source_dir.parent)])
    validate_path(target_file, ["/app", "/cache"])

    if not source_dir.exists():
        raise ArchiveError(f"Source directory missing: {source_dir}")

    target_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        _compress_directory_to_tar(source_dir, target_file)
        size_mb = get_file_size_mb(target_file)

        if size_mb > max_size_mb:
            target_file.unlink(missing_ok=True)
            raise ArchiveError(f"Archive too large: {size_mb:.1f}MB > {max_size_mb}MB")

    except Exception as e:
        target_file.unlink(missing_ok=True)
        raise ArchiveError(f"Archive creation failed: {e}") from e


@timed_fn(logger=logger, name="Extracting archive")
def extract_archive(archive_file: Path, target_dir: Path) -> None:
    """Extract archive safely."""
    # Validate paths
    validate_path(archive_file, ["/app", "/cache"])
    validate_path(target_dir, ["/tmp/", str(target_dir.parent)])

    if not archive_file.exists():
        raise ArchiveError(f"Archive missing: {archive_file}")

    try:
        target_dir.mkdir(parents=True, exist_ok=True)

        with tarfile.open(archive_file, "r:gz") as tar:
            # Security check
            for member in tar.getmembers():
                if os.path.isabs(member.name) or ".." in member.name:
                    raise ArchiveError(f"Unsafe path in archive: {member.name}")

            tar.extractall(path=target_dir)

    except Exception as e:
        raise ArchiveError(f"Extraction failed: {e}") from e
