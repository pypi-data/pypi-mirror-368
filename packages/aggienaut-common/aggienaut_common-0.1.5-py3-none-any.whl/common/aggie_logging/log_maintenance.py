"""Module for maintaining and managing log files."""
import os
import glob
import shutil
from datetime import datetime, timedelta
import math
import gzip

from common.utils import from_root

def reset_log_files(log_dir: str, backup: bool = True) -> int:
    """
    Reset all log files in the specified directory.

    Args:
        log_dir (str): Directory containing log files
        backup (bool, optional): Whether to backup logs before resetting. Defaults to True.

    Returns:
        int: Number of log files reset
    """
    if not os.path.exists(log_dir):
        return 0

    # Use find_log_files() instead of duplicating the glob logic
    log_files = find_log_files(log_dir)

    if not log_files:
        return 0

    # Create backup directory if needed
    if backup:
        backup_dir = os.path.join(log_dir, "backup")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = os.path.join(backup_dir, f"backup_{timestamp}")
        os.makedirs(backup_subdir)

    reset_count = 0
    for log_file in log_files:
        try:
            # Backup the file if requested
            if backup:
                backup_file = os.path.join(backup_subdir, os.path.basename(log_file))  #type:ignore
                shutil.copy2(log_file, backup_file)

            # Clear the log file (keep the file but remove contents)
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"# Log file reset on {datetime.now().isoformat()}\n")

            reset_count += 1

        except Exception as e:  # pylint: disable=broad-except
            print(f"Error resetting log file {log_file}: {e}")

    if backup and reset_count > 0:
        print(f"Backed up {reset_count} log files to {backup_subdir}")  #type:ignore

    return reset_count

def delete_all_logs(log_dir: str|None=None, confirm: bool = True) -> int:
    """
    Delete all log files in the specified directory.

    Args:
        log_dir (str): Directory containing log files
        confirm (bool, optional): If True, requires confirmation before deletion. Defaults to True.

    Returns:
        int: Number of log files deleted
    """
    if log_dir is None:
        log_dir = str(from_root('logs'))
    if not os.path.exists(log_dir):
        print(f"Log directory {log_dir} does not exist")
        return 0

    # Use find_log_files() instead of duplicating the glob logic
    log_files = find_log_files(log_dir)

    if not log_files:
        print("No log files found")
        return 0

    # Confirmation step
    if confirm:
        file_count = len(log_files)
        print(f"About to delete {file_count} log files from {log_dir}")
        confirmation = input("Are you sure you want to proceed? (y/n): ")
        if confirmation.lower() not in ['y', 'yes']:
            print("Operation cancelled")
            return 0

    # Delete files
    deleted_count = 0
    for file_path in log_files:
        try:
            os.remove(file_path)
            deleted_count += 1
        except Exception as e:  # pylint: disable=broad-except
            print(f"Error deleting {file_path}: {e}")

    # Also check for and delete the backup directory if it exists
    backup_dir = os.path.join(log_dir, "backup")
    if os.path.exists(backup_dir):
        try:
            shutil.rmtree(backup_dir)
            print(f"Deleted backup directory: {backup_dir}")
        except Exception as e:  # pylint: disable=broad-except
            print(f"Error deleting backup directory: {e}")

    print(f"Successfully deleted {deleted_count} log files")
    return deleted_count

def find_log_files(log_dir: str) -> list[str]:
    """
    Find all log files in the specified directory.

    Args:
        log_dir (str): Directory containing log files

    Returns:
        list[str]: List of log file paths
    """
    if not os.path.exists(log_dir):
        return []

    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    log_files.extend(glob.glob(os.path.join(log_dir, "*.log.*")))
    return log_files

def create_archive_directory(log_dir: str) -> str:
    """
    Create and return the archive directory path.

    Args:
        log_dir (str): Base log directory

    Returns:
        str: Path to the timestamped archive subdirectory
    """
    archive_dir = os.path.join(log_dir, "archives")
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_subdir = os.path.join(archive_dir, f"archive_{timestamp}")
    os.makedirs(archive_subdir)
    return archive_subdir

def identify_old_files(log_files: list[str], days_old: int) -> list[str]:
    """
    Identify files older than the specified number of days.

    Args:
        log_files (list[str]): List of log file paths
        days_old (int): Age threshold in days

    Returns:
        list[str]: List of files older than the threshold
    """
    cutoff_date = datetime.now() - timedelta(days=days_old)
    files_to_archive = []

    for log_file in log_files:
        try:
            file_modified = datetime.fromtimestamp(os.path.getmtime(log_file))
            if file_modified < cutoff_date:
                files_to_archive.append(log_file)
        except Exception as e:  # pylint: disable=broad-except
            print(f"Error checking file date for {log_file}: {e}")

    return files_to_archive

def archive_file(log_file: str, archive_dir: str, compress: bool) -> bool:
    """
    Archive a single file, with optional compression.

    Args:
        log_file (str): Path to the log file to archive
        archive_dir (str): Directory to archive the file to
        compress (bool): Whether to compress the file

    Returns:
        bool: True if archiving was successful, False otherwise
    """
    try:
        filename = os.path.basename(log_file)

        if compress:
            # Compress and move file
            archive_filepath = os.path.join(archive_dir, f"{filename}.gz")
            with open(log_file, 'rb') as f_in:
                with gzip.open(archive_filepath, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            # Remove original file
            os.remove(log_file)
        else:
            # Just move file
            archive_filepath = os.path.join(archive_dir, filename)
            shutil.move(log_file, archive_filepath)

        return True
    except Exception as e:  # pylint: disable=broad-except
        print(f"Error archiving {log_file}: {e}")
        return False

def archive_old_logs(log_dir: str, days_old: int = 30, compress: bool = True) -> int:
    """
    Archive log files older than specified days.

    Args:
        log_dir (str): Directory containing log files
        days_old (int): Archive files older than this many days
        compress (bool): Whether to compress archived files

    Returns:
        int: Number of files archived
    """
    # Find all log files
    log_files = find_log_files(log_dir)
    if not log_files:
        return 0

    # Identify files to archive
    files_to_archive = identify_old_files(log_files, days_old)
    if not files_to_archive:
        print(f"No log files older than {days_old} days found")
        return 0

    # Create archive directory
    archive_subdir = create_archive_directory(log_dir)

    # Archive files
    archived_count = 0
    for log_file in files_to_archive:
        if archive_file(log_file, archive_subdir, compress):
            archived_count += 1

    print(f"Archived {archived_count} log files to {archive_subdir}")
    return archived_count

def cleanup_rotated_logs(log_dir: str, keep_count: int = 5) -> int:
    """
    Clean up old rotated log files, keeping only the most recent ones.

    Args:
        log_dir (str): Directory containing log files
        keep_count (int): Number of rotated files to keep for each logger

    Returns:
        int: Number of files cleaned up
    """
    if not os.path.exists(log_dir):
        return 0

    # Find all rotated log files (*.log.1, *.log.2, etc.)
    # We can't use find_log_files() directly here as we need only rotated files
    rotated_files = glob.glob(os.path.join(log_dir, "*.log.*"))

    if not rotated_files:
        return 0

    # Group files by base name
    file_groups = {}
    for file_path in rotated_files:
        # Extract base name (everything before the rotation number)
        base_name = file_path.rsplit('.', 1)[0]  # Remove the rotation number
        if base_name not in file_groups:
            file_groups[base_name] = []
        file_groups[base_name].append(file_path)

    cleaned_count = 0

    # Process each group
    for base_name, files in file_groups.items():
        # Sort files by modification time (newest first)
        files.sort(key=os.path.getmtime, reverse=True)

        # Keep only the most recent files
        files_to_delete = files[keep_count:]

        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                cleaned_count += 1
            except Exception as e:  # pylint: disable=broad-except
                print(f"Error deleting rotated log file {file_path}: {e}")

    if cleaned_count > 0:
        print(f"Cleaned up {cleaned_count} old rotated log files")

    return cleaned_count

def get_log_disk_usage(log_dir: str) -> dict:
    """
    Get disk usage statistics for log files.

    Args:
        log_dir (str): Directory containing log files

    Returns:
        dict: Dictionary with disk usage information
    """
    if not os.path.exists(log_dir):
        return {}

    # Use find_log_files() instead of duplicating the glob logic
    log_files = find_log_files(log_dir)

    archive_dir = os.path.join(log_dir, "archives")
    backup_dir = os.path.join(log_dir, "backup")

    usage = {
        'current_logs': {
            'count': len(log_files),
            'size': 0
        },
        'archives': {
            'count': 0,
            'size': 0
        },
        'backups': {
            'count': 0,
            'size': 0
        },
        'total_size': 0
    }

    # Calculate current log files size
    for log_file in log_files:
        try:
            usage['current_logs']['size'] += os.path.getsize(log_file)
        except Exception:  # pylint: disable=broad-except
            print(f"Error getting size of {log_file}")

    # Calculate archive directory size
    if os.path.exists(archive_dir):
        for root, _, files in os.walk(archive_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    usage['archives']['size'] += os.path.getsize(file_path)
                    usage['archives']['count'] += 1
                except Exception:  # pylint: disable=broad-except
                    print(f"Error getting size of file: {file_path}")

    # Calculate backup directory size
    if os.path.exists(backup_dir):
        for root, _, files in os.walk(backup_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    usage['backups']['size'] += os.path.getsize(file_path)
                    usage['backups']['count'] += 1
                except Exception:  # pylint: disable=broad-except
                    print(f"Error getting size of file: {file_path}")

    usage['total_size'] = (usage['current_logs']['size'] +
                          usage['archives']['size'] +
                          usage['backups']['size'])

    return usage

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.

    Args:
        size_bytes (int): Size in bytes

    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def print_log_usage_report(log_dir: str) -> None:
    """
    Print a detailed report of log disk usage.

    Args:
        log_dir (str): Directory containing log files
    """
    usage = get_log_disk_usage(log_dir)

    if not usage:
        print(f"No log directory found at {log_dir}")
        return

    print(f"\n=== Log Disk Usage Report for {log_dir} ===")
    print(f"Current Log Files: {usage['current_logs']['count']} files, {format_file_size(usage['current_logs']['size'])}")
    print(f"Archived Files: {usage['archives']['count']} files, {format_file_size(usage['archives']['size'])}")
    print(f"Backup Files: {usage['backups']['count']} files, {format_file_size(usage['backups']['size'])}")
    print(f"Total Usage: {format_file_size(usage['total_size'])}")
    print("=" * 50)

def maintenance_routine(log_dir: str, archive_days: int = 30, cleanup_rotated: int = 5,
                       compress_archives: bool = True) -> dict:
    """
    Run a complete log maintenance routine.

    Args:
        log_dir (str): Directory containing log files
        archive_days (int): Archive files older than this many days
        cleanup_rotated (int): Number of rotated files to keep
        compress_archives (bool): Whether to compress archived files

    Returns:
        dict: Summary of maintenance actions performed
    """
    if not os.path.exists(log_dir):
        return {'error': f"Log directory {log_dir} does not exist"}

    print(f"Starting log maintenance routine for {log_dir}")

    results = {
        'archived_files': 0,
        'cleaned_rotated': 0,
        'disk_usage_before': get_log_disk_usage(log_dir),
        'disk_usage_after': {},
        'errors': []
    }

    try:
        # Archive old files
        results['archived_files'] = archive_old_logs(log_dir, archive_days, compress_archives)

        # Clean up rotated files
        results['cleaned_rotated'] = cleanup_rotated_logs(log_dir, cleanup_rotated)

        # Get final disk usage
        results['disk_usage_after'] = get_log_disk_usage(log_dir)

        # Calculate space saved
        space_before = results['disk_usage_before']['total_size']
        space_after = results['disk_usage_after']['total_size']
        space_saved = space_before - space_after

        print("Maintenance completed:")
        print(f"  - Archived {results['archived_files']} old files")
        print(f"  - Cleaned {results['cleaned_rotated']} rotated files")
        print(f"  - Space saved: {format_file_size(space_saved)}")

    except Exception as e:  # pylint: disable=broad-except
        error_msg = f"Error during maintenance routine: {e}"
        results['errors'].append(error_msg)
        print(error_msg)

    return results
