import os
import zipfile
import tarfile


class ExtractionError(Exception):
    pass


def _is_safe_member(member_name, dest_dir):
    dest_path = os.path.abspath(os.path.join(dest_dir, member_name))
    return dest_path.startswith(os.path.abspath(dest_dir) + os.sep)


def extract_zip(archive_path, dest_dir):
    with zipfile.ZipFile(archive_path, "r") as zf:
        for member in zf.namelist():
            if not _is_safe_member(member, dest_dir):
                raise ExtractionError(f"Unsafe path in archive: {member}")
        zf.extractall(dest_dir)


def extract_tar(archive_path, dest_dir):
    with tarfile.open(archive_path, "r:*") as tf:
        for member in tf.getmembers():
            if not _is_safe_member(member.name, dest_dir):
                raise ExtractionError(f"Unsafe path in archive: {member.name}")
        tf.extractall(dest_dir)


def extract_archive(archive_path, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    if archive_path.endswith(".zip"):
        extract_zip(archive_path, dest_dir)
    elif archive_path.endswith((".tar.gz", ".tgz", ".tar")):
        extract_tar(archive_path, dest_dir)
    else:
        raise ExtractionError("Unsupported archive format.")
