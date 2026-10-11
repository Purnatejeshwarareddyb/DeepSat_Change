import os
import urllib.request
from app.dataset.dataset_extractor import extract_archive, ExtractionError
from app.utils.config import config, ROOT_DIR
from app.utils.logger import log


class DownloadError(Exception):
    pass


def download_file(url, dest_path, progress_callback=None):
    if not url.lower().startswith("https://") and not url.lower().startswith("http://"):
        raise DownloadError("Only HTTP/HTTPS URLs are supported.")

    def _hook(block_num, block_size, total_size):
        if progress_callback and total_size > 0:
            downloaded = block_num * block_size
            percent = min(100.0, downloaded / total_size * 100)
            progress_callback(percent, downloaded, total_size)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    urllib.request.urlretrieve(url, dest_path, _hook)
    return dest_path


def download_dataset(dataset_entry, progress_callback=None):
    url = dataset_entry.get("download_url", "")
    if not url:
        raise DownloadError(
            "No automated download URL is configured for this dataset. "
            "Please download it manually from the homepage and use 'USE LOCAL DATASET' instead."
        )
    dest_dir = config.abs_path("dataset_path")
    archive_name = os.path.basename(url.split("?")[0]) or "dataset_download"
    archive_path = os.path.join(ROOT_DIR, "dataset", archive_name)

    log.info(f"Starting dataset download from {url}")
    download_file(url, archive_path, progress_callback)
    log.info("Download complete, extracting archive")
    try:
        extract_archive(archive_path, dest_dir)
    except ExtractionError as exc:
        raise DownloadError(str(exc))
    log.info("Dataset extraction complete")
    return dest_dir
