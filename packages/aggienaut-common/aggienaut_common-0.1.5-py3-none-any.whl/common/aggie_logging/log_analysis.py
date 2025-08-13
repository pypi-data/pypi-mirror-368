"""Module for log anaylysis."""
import os
import glob
from datetime import datetime
from typing import List, Dict, Optional
import re
import csv


def aggregate_logs(log_dir: str, output_file: Optional[str] = None) -> str:
    """
    Aggregate all logs from text files into one consolidated log file.

    Args:
        log_dir (str): Directory containing log files
        output_file (str, optional): Output file path. If None, creates a timestamped file in log_dir.

    Returns:
        str: Path to the aggregated log file
    """
    if not os.path.exists(log_dir):
        raise FileNotFoundError(f"Log directory {log_dir} does not exist")

    # Find all log files (including rotated ones)
    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    log_files.extend(glob.glob(os.path.join(log_dir, "*.log.*")))

    if not log_files:
        raise ValueError(f"No log files found in {log_dir}")

    # Create output file name if not provided
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(log_dir, f"aggregated_logs_{timestamp}.log")

    # Collect all log entries with timestamps for sorting
    log_entries = []
    total_logs = 0

    for log_file in log_files:
        try:
            source_name = os.path.basename(log_file)
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    # Try to extract timestamp from log line
                    timestamp_match = re.match(r'\[([^\]]+)\]', line)
                    if timestamp_match:
                        timestamp_str = timestamp_match.group(1)
                        try:
                            # Try to parse the timestamp
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        except ValueError:
                            # If parsing fails, use file modification time as fallback
                            timestamp = datetime.fromtimestamp(os.path.getmtime(log_file))
                    else:
                        # No timestamp found, use file modification time
                        timestamp = datetime.fromtimestamp(os.path.getmtime(log_file))

                    log_entries.append({
                        'timestamp': timestamp,
                        'source': source_name,
                        'line': line,
                        'original_line_num': line_num
                    })
                    total_logs += 1

        except Exception as e:  # pylint: disable=broad-except
            print(f"Error processing log file {log_file}: {e}")

    # Sort log entries by timestamp
    log_entries.sort(key=lambda x: x['timestamp'])

    # Write aggregated logs to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Aggregated logs from {len(log_files)} files\n")
        f.write(f"# Generated on {datetime.now().isoformat()}\n")
        f.write(f"# Total entries: {total_logs}\n\n")

        for entry in log_entries:
            f.write(f"[{entry['source']}:{entry['original_line_num']}] {entry['line']}\n")

    print(f"Aggregated {total_logs} logs from {len(log_files)} files into {output_file}")
    return output_file

def list_log_files(log_dir: str) -> List[Dict]:
    """
    List all log files and their statistics.

    Args:
        log_dir (str): Directory containing log files

    Returns:
        List[Dict]: List of dictionaries with log file information
    """
    if not os.path.exists(log_dir):
        return []

    # Find all log files (including rotated ones)
    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    log_files.extend(glob.glob(os.path.join(log_dir, "*.log.*")))

    if not log_files:
        return []

    results = []
    for log_file in log_files:
        try:
            file_info = {
                'file_path': log_file,
                'file_name': os.path.basename(log_file),
                'size': os.path.getsize(log_file),
                'modified': datetime.fromtimestamp(os.path.getmtime(log_file)),
                'created': datetime.fromtimestamp(os.path.getctime(log_file)),
                'line_count': 0,
                'earliest_log': None,
                'latest_log': None,
                'log_levels': {}
            }

            # Analyze file contents
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                first_timestamp = None
                last_timestamp = None

                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    file_info['line_count'] += 1

                    # Extract timestamp
                    timestamp_match = re.match(r'\[([^\]]+)\]', line)
                    if timestamp_match:
                        timestamp_str = timestamp_match.group(1)
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            if first_timestamp is None:
                                first_timestamp = timestamp
                            last_timestamp = timestamp
                        except ValueError:
                            pass

                    # Extract log level
                    level_match = re.search(r'\[(DEBUG|INFO|WARNING|ERROR|CRITICAL)\]', line)
                    if level_match:
                        level = level_match.group(1)
                        file_info['log_levels'][level] = file_info['log_levels'].get(level, 0) + 1

                file_info['earliest_log'] = first_timestamp
                file_info['latest_log'] = last_timestamp

            results.append(file_info)

        except Exception as e:  # pylint: disable=broad-except
            print(f"Error analyzing log file {log_file}: {e}")
            results.append({
                'file_path': log_file,
                'file_name': os.path.basename(log_file),
                'size': os.path.getsize(log_file),
                'modified': datetime.fromtimestamp(os.path.getmtime(log_file)),
                'error': str(e)
            })

    return results

def export_logs_to_csv(log_file: str, output_dir: Optional[str] = None) -> str:
    """
    Export logs from a text file to CSV format.

    Args:
        log_file (str): Path to the log file
        output_dir (str, optional): Directory to save CSV file. If None, uses the same directory as log_file.

    Returns:
        str: Path to the exported CSV file
    """
    if not os.path.exists(log_file):
        raise FileNotFoundError(f"Log file {log_file} does not exist")

    if output_dir is None:
        output_dir = os.path.dirname(log_file)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create CSV filename
    log_name = os.path.basename(log_file).replace('.log', '')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = os.path.join(output_dir, f"{log_name}_{timestamp}.csv")


    with open(csv_file, 'w', newline='', encoding='utf-8') as csvf:
        writer = csv.writer(csvf)

        # Write header
        writer.writerow(['timestamp', 'logger_name', 'level', 'thread_name', 'message', 'raw_line'])

        with open(log_file, 'r', encoding='utf-8', errors='ignore') as logf:
            for line in logf:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Parse log line using regex
                # Expected format: [timestamp] [logger] [level] [thread] - message
                match = re.match(r'\[([^\]]+)\] \[([^\]]+)\] \[([^\]]+)\] \[([^\]]+)\] - (.+)', line)

                if match:
                    timestamp_str, logger_name, level, thread_name, message = match.groups()
                    writer.writerow([timestamp_str, logger_name, level, thread_name, message, line])
                else:
                    # If parsing fails, write the raw line with empty fields
                    writer.writerow(['', '', '', '', '', line])

    print(f"Exported log file {log_file} to CSV: {csv_file}")
    return csv_file

def search_logs(log_dir: str, search_term: str, case_sensitive: bool = False,  # pylint: disable=too-many-arguments, too-many-positional-arguments
                level_filter: Optional[str] = None, start_date: Optional[datetime] = None,
                end_date: Optional[datetime] = None) -> List[Dict]:
    """
    Search for specific terms in log files with optional filters.

    Args:
        log_dir (str): Directory containing log files
        search_term (str): Term to search for
        case_sensitive (bool): Whether search should be case sensitive
        level_filter (str, optional): Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        start_date (datetime, optional): Filter logs after this date
        end_date (datetime, optional): Filter logs before this date

    Returns:
        List[Dict]: List of matching log entries
    """
    if not os.path.exists(log_dir):
        return []

    log_files = _find_log_files(log_dir)
    if not log_files:
        return []

    results = []
    search_pattern = search_term if case_sensitive else search_term.lower()

    for log_file in log_files:
        file_results = _search_single_log_file(
            log_file,
            search_pattern,
            case_sensitive,
            level_filter,
            start_date,
            end_date
        )
        results.extend(file_results)

    return results


def _find_log_files(log_dir: str) -> List[str]:
    """
    Find all log files in the specified directory.

    Args:
        log_dir (str): Directory to search for log files

    Returns:
        List[str]: List of log file paths
    """
    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    log_files.extend(glob.glob(os.path.join(log_dir, "*.log.*")))
    return log_files


def _search_single_log_file(log_file: str, search_pattern: str, case_sensitive: bool,  # pylint: disable=too-many-arguments, too-many-positional-arguments
                           level_filter: Optional[str], start_date: Optional[datetime],
                           end_date: Optional[datetime]) -> List[Dict]:
    """
    Search a single log file for matching entries.

    Args:
        log_file (str): Path to the log file
        search_pattern (str): Term to search for
        case_sensitive (bool): Whether search should be case sensitive
        level_filter (str, optional): Filter by log level
        start_date (datetime, optional): Filter logs after this date
        end_date (datetime, optional): Filter logs before this date

    Returns:
        List[Dict]: Matching log entries from this file
    """
    results = []
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Apply case sensitivity
                search_line = line if case_sensitive else line.lower()

                # Check if search term is in line
                if search_pattern not in search_line:
                    continue

                entry = _parse_log_line(log_file, line_num, line)

                # Skip if entry doesn't match filters
                if not _matches_filters(entry, level_filter, start_date, end_date):
                    continue

                results.append(entry)

    except Exception as e:  # pylint: disable=broad-except
        print(f"Error searching log file {log_file}: {e}")

    return results


def _parse_log_line(log_file: str, line_num: int, line: str) -> Dict:
    """
    Parse a log line into a structured dictionary.

    Args:
        log_file (str): Source log file
        line_num (int): Line number in the file
        line (str): The log line content

    Returns:
        Dict: Structured log entry
    """
    # Parse log line for additional filtering
    match = re.match(r'\[([^\]]+)\] \[([^\]]+)\] \[([^\]]+)\] \[([^\]]+)\] - (.+)', line)

    if match:
        timestamp_str, logger_name, level, thread_name, message = match.groups()
        return {
            'file': os.path.basename(log_file),
            'line_number': line_num,
            'timestamp': timestamp_str,
            'logger': logger_name,
            'level': level,
            'thread': thread_name,
            'message': message,
            'raw_line': line
        }

    return {
        'file': os.path.basename(log_file),
        'line_number': line_num,
        'timestamp': '',
        'logger': '',
        'level': '',
        'thread': '',
        'message': '',
        'raw_line': line
    }


def _matches_filters(entry: Dict, level_filter: Optional[str],
                    start_date: Optional[datetime], end_date: Optional[datetime]) -> bool:
    """
    Check if a log entry matches the specified filters.

    Args:
        entry (Dict): The log entry to check
        level_filter (str, optional): Filter by log level
        start_date (datetime, optional): Filter logs after this date
        end_date (datetime, optional): Filter logs before this date

    Returns:
        bool: True if the entry matches all filters, False otherwise
    """
    # Apply level filter
    if level_filter and entry['level'] != level_filter:
        return False

    # Apply date filters if we have a timestamp
    if entry['timestamp']:
        try:
            log_timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
            if start_date and log_timestamp < start_date:
                return False
            if end_date and log_timestamp > end_date:
                return False
        except ValueError:
            # If timestamp parsing fails, include the entry
            pass

    return True

def get_log_summary(log_dir: str) -> Dict:
    """
    Get a summary of all logs in the directory.

    Args:
        log_dir (str): Directory containing log files

    Returns:
        Dict: Summary statistics
    """
    if not os.path.exists(log_dir):
        return {}

    log_files = list_log_files(log_dir)

    if not log_files:
        return {}

    summary = {
        'total_files': len(log_files),
        'total_size': sum(f.get('size', 0) for f in log_files),
        'total_lines': sum(f.get('line_count', 0) for f in log_files),
        'earliest_log': None,
        'latest_log': None,
        'log_levels': {},
        'files_with_errors': 0
    }

    earliest = None
    latest = None

    for file_info in log_files:
        if 'error' in file_info:
            summary['files_with_errors'] += 1
            continue

        # Track earliest and latest logs
        if file_info.get('earliest_log'):
            if earliest is None or file_info['earliest_log'] < earliest:
                earliest = file_info['earliest_log']

        if file_info.get('latest_log'):
            if latest is None or file_info['latest_log'] > latest:
                latest = file_info['latest_log']

        # Aggregate log levels
        for level, count in file_info.get('log_levels', {}).items():
            summary['log_levels'][level] = summary['log_levels'].get(level, 0) + count

    summary['earliest_log'] = earliest
    summary['latest_log'] = latest

    return summary
