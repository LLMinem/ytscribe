"""Configuration management for ytscribe.

Loads settings from environment variables and ensures required directories exist.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load .env file if present
load_dotenv()


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    elevenlabs_api_key: str
    download_root: Path
    transcript_root: Path

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.

        Raises:
            ValueError: If ELEVENLABS_API_KEY is not set.
        """
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError(
                "ELEVENLABS_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )

        download_root = Path(os.getenv("DOWNLOAD_ROOT", "data/audio"))
        transcript_root = Path(os.getenv("TRANSCRIPT_ROOT", "data/transcripts"))

        # Ensure directories exist
        download_root.mkdir(parents=True, exist_ok=True)
        transcript_root.mkdir(parents=True, exist_ok=True)

        return cls(
            elevenlabs_api_key=api_key,
            download_root=download_root,
            transcript_root=transcript_root,
        )


# Global config instance - lazy loaded when needed
_config: Config | None = None


def get_config() -> Config:
    """Get the global configuration instance.

    Returns:
        Config: The application configuration.

    Raises:
        ValueError: If ELEVENLABS_API_KEY is not set.
    """
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config
