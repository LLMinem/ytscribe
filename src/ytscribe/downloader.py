"""YouTube audio downloader using yt-dlp.

Downloads audio from YouTube videos and playlists, preferring Opus format (itag 250).
"""

import sys
from pathlib import Path
from typing import Any

import yt_dlp


class AudioDownloader:
    """Downloads audio from YouTube using yt-dlp with format preferences."""

    def __init__(self, output_root: Path) -> None:
        """Initialize the downloader.

        Args:
            output_root: Root directory for downloaded audio files.
        """
        self.output_root = output_root
        self.output_root.mkdir(parents=True, exist_ok=True)

    def _get_format_selector(self) -> str:
        """Get the format selector string for yt-dlp.

        Prefers Opus itag 250 (~64-70kbps), falls back to best audio.

        Returns:
            Format selector string for yt-dlp.
        """
        # Try itag 250 (Opus ~64-70kbps) first, then any Opus <= 70kbps,
        # then fall back to best audio available
        return "250/bestaudio[abr<=70][acodec^=opus]/bestaudio"

    def _get_output_template(self, info: dict[str, Any]) -> str:
        """Generate output file path template based on video metadata.

        Creates paths like: {output_root}/{channel_or_playlist}/{upload_date}_{video_id}.opus

        Args:
            info: Video info dictionary from yt-dlp.

        Returns:
            Output file path as string.
        """
        # Extract metadata
        video_id = info.get("id", "unknown")
        upload_date = info.get("upload_date", "00000000")
        channel = info.get("channel", info.get("uploader", "unknown_channel"))
        playlist = info.get("playlist_title")

        # Sanitize directory name (remove special chars that might cause issues)
        dir_name = playlist if playlist else channel
        dir_name = "".join(
            c if c.isalnum() or c in (" ", "-", "_") else "_" for c in dir_name
        )
        dir_name = dir_name.strip().replace(" ", "_")

        # Create subdirectory
        output_dir = self.output_root / dir_name
        output_dir.mkdir(parents=True, exist_ok=True)

        # Format: YYYYMMDD_VIDEO_ID (extension will be added by yt-dlp/ffmpeg)
        filename = f"{upload_date}_{video_id}"
        return str(output_dir / filename)

    def _progress_hook(self, d: dict[str, Any]) -> None:
        """Progress callback for yt-dlp downloads.

        Args:
            d: Progress dictionary from yt-dlp.
        """
        if d["status"] == "downloading":
            # Show download progress
            percent = d.get("_percent_str", "N/A")
            speed = d.get("_speed_str", "N/A")
            eta = d.get("_eta_str", "N/A")
            print(f"  Downloading: {percent} | Speed: {speed} | ETA: {eta}", end="\r")
        elif d["status"] == "finished":
            print(f"\n  ✓ Download complete: {d.get('filename', 'unknown')}")
        elif d["status"] == "error":
            print("\n  ✗ Download error", file=sys.stderr)

    def download(self, url: str, skip_existing: bool = True) -> list[Path]:
        """Download audio from a YouTube URL (video or playlist).

        Args:
            url: YouTube video or playlist URL.
            skip_existing: Skip downloads if file already exists.

        Returns:
            List of downloaded file paths.

        Raises:
            yt_dlp.utils.DownloadError: If download fails.
        """
        downloaded_files: list[Path] = []

        # First pass: Extract metadata without downloading
        print(f"📋 Extracting metadata from: {url}")
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except Exception as e:
                print(f"✗ Failed to extract metadata: {e}", file=sys.stderr)
                raise

        if not info:
            raise ValueError("Failed to extract video information")

        # Handle playlist vs single video
        entries = info.get("entries", [info])
        total_videos = len(entries) if isinstance(entries, list) else 1

        print(f"📦 Found {total_videos} video(s) to download\n")

        # Download each video
        for idx, entry in enumerate(
            entries if isinstance(entries, list) else [info], 1
        ):
            if not entry:
                continue

            # Generate output path (FFmpeg will add .opus extension)
            output_path_str = self._get_output_template(entry)
            output_path_with_ext = Path(f"{output_path_str}.opus")

            # Check if file already exists
            if skip_existing and output_path_with_ext.exists():
                print(
                    f"[{idx}/{total_videos}] ⏭  Skipping (already exists): {output_path_with_ext.name}"
                )
                downloaded_files.append(output_path_with_ext)
                continue

            # Download options
            ydl_opts = {
                "format": self._get_format_selector(),
                "outtmpl": output_path_str,
                "quiet": False,
                "no_warnings": False,
                "progress_hooks": [self._progress_hook],
                # Audio processing
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "opus",
                        "preferredquality": "64",
                    }
                ],
                # Don't embed metadata to keep files small
                "writethumbnail": False,
                "embedthumbnail": False,
            }

            print(
                f"[{idx}/{total_videos}] 🎵 Downloading: {entry.get('title', 'Unknown')}"
            )
            print(f"  Channel: {entry.get('channel', 'Unknown')}")
            print(f"  Video ID: {entry.get('id', 'Unknown')}")

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([entry.get("webpage_url", url)])
                downloaded_files.append(output_path_with_ext)
            except Exception as e:
                print(f"  ✗ Failed to download: {e}", file=sys.stderr)
                # Continue with other videos in playlist
                continue

        return downloaded_files
