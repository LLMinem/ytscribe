"""Transcriber for audio files using ElevenLabs Scribe v1.

Handles transcription of audio files with speaker diarization and audio event tagging.
"""

import json
from pathlib import Path
from typing import Any, Optional

from elevenlabs.client import ElevenLabs

from ytscribe.config import Config

# ElevenLabs limits
MAX_FILE_SIZE_BYTES = 3 * 1024 * 1024 * 1024  # 3 GB
MAX_DURATION_HOURS = 10


class Transcriber:
    """Transcribes audio files using ElevenLabs Scribe v1 API."""

    def __init__(self, config: Config) -> None:
        """Initialize the transcriber.

        Args:
            config: Application configuration with API key and paths.
        """
        self.config = config
        self.client = ElevenLabs(api_key=config.elevenlabs_api_key)

    def _validate_audio_file(self, audio_path: Path) -> None:
        """Validate audio file before transcription.

        Args:
            audio_path: Path to the audio file.

        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If file exceeds size limits.
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if not audio_path.is_file():
            raise ValueError(f"Path is not a file: {audio_path}")

        # Check file size
        file_size = audio_path.stat().st_size
        if file_size > MAX_FILE_SIZE_BYTES:
            size_gb = file_size / (1024**3)
            raise ValueError(
                f"File size ({size_gb:.2f} GB) exceeds ElevenLabs limit of 3 GB. "
                "Consider splitting the audio file."
            )

        if file_size == 0:
            raise ValueError(f"Audio file is empty: {audio_path}")

    def _generate_output_paths(self, audio_path: Path) -> tuple[Path, Path]:
        """Generate output paths for transcript files.

        Creates paths matching the audio file structure:
        - Audio: data/audio/{channel}/{date}_{id}.opus
        - JSON:  data/transcripts/{channel}/{date}_{id}.json
        - MD:    data/transcripts/{channel}/{date}_{id}.md

        Args:
            audio_path: Path to the audio file.

        Returns:
            Tuple of (json_path, markdown_path).
        """
        # Extract relative path structure from audio path
        # audio_path structure: {output_root}/{channel}/{filename}.opus
        try:
            # Get the parts relative to audio root
            relative_parts = audio_path.relative_to(self.config.download_root).parts
            channel_dir = relative_parts[0] if len(relative_parts) > 1 else "unknown"
            filename_stem = audio_path.stem  # Remove .opus extension
        except ValueError:
            # If audio_path is not relative to download_root, use parent dir
            channel_dir = audio_path.parent.name
            filename_stem = audio_path.stem

        # Create transcript subdirectory
        transcript_dir = self.config.transcript_root / channel_dir
        transcript_dir.mkdir(parents=True, exist_ok=True)

        json_path = transcript_dir / f"{filename_stem}.json"
        md_path = transcript_dir / f"{filename_stem}.md"

        return json_path, md_path

    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp in MM:SS.mmm format.

        Args:
            seconds: Time in seconds.

        Returns:
            Formatted timestamp string.
        """
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes:02d}:{secs:06.3f}"

    def _generate_markdown(
        self, transcript_data: dict[str, Any], audio_path: Path
    ) -> str:
        """Generate human-readable Markdown from transcript data.

        Args:
            transcript_data: Raw API response from ElevenLabs.
            audio_path: Path to original audio file.

        Returns:
            Formatted Markdown string.
        """
        lines = []

        # Header
        filename = audio_path.name
        lines.append(f"# Transcript: {filename}\n")

        # Metadata
        lines.append("## Metadata\n")
        lines.append(f"- **Audio File:** `{audio_path}`")
        lines.append(
            f"- **Language:** {transcript_data.get('language_code', 'unknown')}"
        )
        lines.append(
            f"- **Language Probability:** {transcript_data.get('language_probability', 0):.2f}"
        )
        lines.append("")

        # Full transcript
        lines.append("## Full Transcript\n")
        full_text = transcript_data.get("text", "")
        lines.append(full_text)
        lines.append("")

        # Audio events
        words = transcript_data.get("words", [])
        audio_events = [word for word in words if word.get("type") == "audio_event"]
        if audio_events:
            lines.append("## Audio Events\n")
            for event in audio_events:
                start = event.get("start", 0)
                end = event.get("end", 0)
                text = event.get("text", "unknown")
                timestamp_str = (
                    f"[{self._format_timestamp(start)} - {self._format_timestamp(end)}]"
                )
                lines.append(f"- {timestamp_str} *{text}*")
            lines.append("")

        return "\n".join(lines)

    def transcribe(
        self,
        audio_path: Path,
        language: Optional[str] = None,
        tag_audio_events: bool = True,
        diarize: bool = True,
    ) -> dict[str, Any]:
        """Transcribe an audio file using ElevenLabs Scribe v1.

        Args:
            audio_path: Path to the audio file.
            language: Language code (e.g., 'eng', 'spa'). None for auto-detect.
            tag_audio_events: Whether to tag audio events like laughter.
            diarize: Whether to identify speakers.

        Returns:
            Dictionary containing transcript data and output paths.
            Keys: 'transcript', 'json_path', 'md_path'

        Raises:
            FileNotFoundError: If audio file doesn't exist.
            ValueError: If file exceeds size limits.
            Exception: For API errors or network issues.
        """
        # Validate input file
        self._validate_audio_file(audio_path)

        # Generate output paths
        json_path, md_path = self._generate_output_paths(audio_path)

        # Call ElevenLabs API
        try:
            with open(audio_path, "rb") as audio_file:
                # Build kwargs dynamically to avoid passing None as empty string
                api_kwargs = {
                    "file": audio_file,
                    "model_id": "scribe_v1",
                    "tag_audio_events": tag_audio_events,
                    "diarize": diarize,
                }

                # Only include language_code if explicitly provided
                if language:
                    api_kwargs["language_code"] = language

                response = self.client.speech_to_text.convert(**api_kwargs)

            # Convert response to dictionary
            transcript_data = (
                response.model_dump()
                if hasattr(response, "model_dump")
                else dict(response)
            )

        except Exception as e:
            # Re-raise with more context
            error_msg = str(e)
            if "401" in error_msg or "authentication" in error_msg.lower():
                raise Exception(
                    f"Authentication failed. Please check your ELEVENLABS_API_KEY: {e}"
                )
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                raise Exception(
                    f"Rate limit exceeded. Please wait and try again later: {e}"
                )
            elif "413" in error_msg or "too large" in error_msg.lower():
                raise Exception(
                    f"File too large for ElevenLabs API (max 3GB, 10h): {e}"
                )
            else:
                raise Exception(f"Transcription API error: {e}")

        # Save JSON output
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, indent=2, ensure_ascii=False)

        # Generate and save Markdown
        markdown_content = self._generate_markdown(transcript_data, audio_path)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        return {
            "transcript": transcript_data,
            "json_path": json_path,
            "md_path": md_path,
        }
