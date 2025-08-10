"""
Torrent download utilities for QuickDownload.

This module provides functionality to download torrents using magnet links,
.torrent files, or .torrent URLs using the libtorrent library.
"""

import os
import sys
import time
import tempfile
import urllib.request

try:
    import libtorrent as lt

    LIBTORRENT_AVAILABLE = True
except ImportError:
    LIBTORRENT_AVAILABLE = False


def is_torrent_url(url):
    """
    Check if URL is a torrent file or magnet link.

    Args:
        url (str): The URL or file path to check

    Returns:
        bool: True if it's a torrent-related URL/file
    """
    return (
        url.startswith("magnet:")
        or url.endswith(".torrent")
        or (os.path.isfile(url) and url.endswith(".torrent"))
    )


def check_libtorrent():
    """
    Check if libtorrent is available and provide helpful error message.

    Raises:
        ImportError: If libtorrent is not available
    """
    if not LIBTORRENT_AVAILABLE:
        print("Error: libtorrent is required for torrent downloads.")
        print("Install it with: pip install libtorrent")
        print("Or on macOS: brew install libtorrent-rasterbar")
        sys.exit(1)


def download_torrent_file(url):
    """
    Download a .torrent file from URL to a temporary file.

    Args:
        url (str): URL to the .torrent file

    Returns:
        str: Path to the downloaded temporary .torrent file
    """
    print(f"Downloading .torrent file from: {url}")
    temp_file = tempfile.NamedTemporaryFile(suffix=".torrent", delete=False)
    try:
        urllib.request.urlretrieve(url, temp_file.name)
        return temp_file.name
    except Exception as e:
        print(f"Error downloading .torrent file: {e}")
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise


def format_size(bytes_size):
    """
    Format bytes as human readable string.

    Args:
        bytes_size (int): Size in bytes

    Returns:
        str: Formatted size string
    """
    if bytes_size == 0:
        return "0 B"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def format_time(seconds):
    """
    Format seconds as human readable time string.

    Args:
        seconds (int): Time in seconds

    Returns:
        str: Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds // 60:.0f}m {seconds % 60:.0f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours:.0f}h {minutes:.0f}m"


def download_torrent(torrent_input, output_dir=None, seed_time=0):
    """
    Download a torrent file or magnet link.

    Args:
        torrent_input (str): Path to .torrent file, magnet link, or URL to .torrent
        output_dir (str): Directory to save downloaded files (default: current directory)
        seed_time (int): Time to seed in minutes after download completes (default: 0)
    """
    check_libtorrent()

    if output_dir is None:
        output_dir = os.getcwd()

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    print("QuickDownload - Torrent Mode")
    print(f"Output directory: {output_dir}")
    print("=" * 50)

    # Create libtorrent session with optimized settings
    settings = {
        "user_agent": "QuickDownload/1.0",
        "listen_interfaces": "0.0.0.0:6881",
        "enable_dht": True,
        "enable_lsd": True,  # Local Service Discovery
        "enable_upnp": True,
        "enable_natpmp": True,
    }

    session = lt.session(settings)

    temp_torrent_file = None

    try:
        # Add torrent based on input type
        if torrent_input.startswith("magnet:"):
            print("Adding magnet link...")
            handle = lt.add_magnet_uri(
                session, torrent_input, {"save_path": output_dir}
            )
        elif torrent_input.startswith("http"):
            print("Downloading and adding .torrent file...")
            temp_torrent_file = download_torrent_file(torrent_input)
            info = lt.torrent_info(temp_torrent_file)
            handle = session.add_torrent({"ti": info, "save_path": output_dir})
        else:
            print(f"Loading .torrent file: {torrent_input}")
            if not os.path.exists(torrent_input):
                raise FileNotFoundError(f"Torrent file not found: {torrent_input}")
            info = lt.torrent_info(torrent_input)
            handle = session.add_torrent({"ti": info, "save_path": output_dir})

        # Wait for metadata (especially important for magnet links)
        print("Waiting for metadata...")
        metadata_timeout = 60  # 60 seconds timeout
        start_time = time.time()

        while not handle.has_metadata():
            if time.time() - start_time > metadata_timeout:
                raise TimeoutError("Timeout waiting for torrent metadata")
            print(".", end="", flush=True)
            time.sleep(1)

        print("\nMetadata received!")
        print(f"Torrent name: {handle.name()}")
        print(f"Total size: {format_size(handle.status().total_wanted)}")
        print(f"Files: {handle.get_torrent_info().num_files()}")
        print("=" * 50)

        # Download loop
        print("Starting download...")
        last_progress = -1
        start_download_time = time.time()

        while not handle.is_seed():
            status = handle.status()

            # Calculate progress and stats
            progress = status.progress * 100
            download_rate = status.download_rate / 1024  # KB/s
            upload_rate = status.upload_rate / 1024
            downloaded = status.total_done
            total_size = status.total_wanted
            num_peers = status.num_peers
            num_seeds = status.num_seeds

            # Calculate ETA
            if download_rate > 0:
                remaining_bytes = total_size - downloaded
                eta_seconds = remaining_bytes / (download_rate * 1024)
                eta_str = format_time(eta_seconds)
            else:
                eta_str = "∞"

            # Only update progress if it changed significantly
            if int(progress) != last_progress:
                # Create progress bar for torrent download
                bar_length = 30
                filled_length = int(bar_length * progress / 100)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)

                print(
                    f"\r[{bar}] {progress:.1f}% | "
                    f"{format_size(downloaded)}/{format_size(total_size)} | "
                    f"↓{download_rate:.1f} KB/s ↑{upload_rate:.1f} KB/s | "
                    f"Peers: {num_peers} Seeds: {num_seeds} | "
                    f"ETA: {eta_str}",
                    end="",
                )
                last_progress = int(progress)

            time.sleep(1)

        download_time = time.time() - start_download_time
        print(f"\n{'=' * 50}")
        print(f"Download completed: {handle.name()}")
        print(f"Time taken: {format_time(download_time)}")
        print(
            f"Average speed: {format_size(handle.status().total_wanted / download_time)}/s"
        )

        # Seed for specified time
        if seed_time > 0:
            print(f"\nSeeding for {seed_time} minutes...")
            seed_end = time.time() + (seed_time * 60)
            total_seed_time = seed_time * 60

            while time.time() < seed_end:
                status = handle.status()
                upload_rate = status.upload_rate / 1024
                uploaded = status.total_upload
                remaining_time = seed_end - time.time()
                elapsed_time = total_seed_time - remaining_time

                # Create seeding progress bar
                seed_progress = (elapsed_time / total_seed_time) * 100
                bar_length = 20
                filled_length = int(bar_length * seed_progress / 100)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)

                print(
                    f"\rSeeding [{bar}] {seed_progress:.1f}% | "
                    f"↑{upload_rate:.1f} KB/s | "
                    f"Uploaded: {format_size(uploaded)} | "
                    f"Time left: {format_time(remaining_time)}",
                    end="",
                )
                time.sleep(1)

            print("\nSeeding completed.")

        print(f"Files saved to: {output_dir}")

    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during torrent download: {e}")
        sys.exit(1)
    finally:
        # Clean up temporary torrent file
        if temp_torrent_file and os.path.exists(temp_torrent_file):
            os.unlink(temp_torrent_file)
