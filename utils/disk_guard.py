
import shutil
from .logger import app_logger as logger

def get_disk_usage(path):
    """Returns disk usage statistics about the given path."""
    try:
        total, used, free = shutil.disk_usage(path)
        return {
            "total": total,
            "used": used,
            "free": free
        }
    except FileNotFoundError:
        logger.error(f"Path not found for disk usage check: {path}")
        return None

def has_sufficient_space(path, threshold_gb=1):
    """Check if the disk has sufficient free space."""
    usage = get_disk_usage(path)
    if usage:
        free_gb = usage['free'] / (1024**3)
        return free_gb > threshold_gb
    return False
