"""Command-line interface for ytscribe.

Provides a Typer-based CLI for downloading YouTube audio and transcribing with ElevenLabs.
"""

from typing import Optional

import typer
from typing_extensions import Annotated

from ytscribe.config import get_config
from ytscribe.downloader import AudioDownloader

app = typer.Typer(
    name="ytscribe",
    help="Download YouTube audio and transcribe with ElevenLabs Scribe v1",
    add_completion=False,
)


@app.command()
def fetch(
    url: Annotated[str, typer.Argument(help="YouTube video or playlist URL")],
    skip_transcribe: Annotated[
        bool,
        typer.Option(
            "--skip-transcribe", help="Download audio only, skip transcription"
        ),
    ] = False,
    language: Annotated[
        Optional[str],
        typer.Option(
            "--language",
            help="Language code for transcription (e.g., 'eng', 'spa'). Auto-detect if not specified.",
        ),
    ] = None,
    tag_audio_events: Annotated[
        bool,
        typer.Option(
            "--tag-audio-events/--no-tag-audio-events",
            help="Tag audio events like laughter, applause",
        ),
    ] = True,
    diarize: Annotated[
        bool,
        typer.Option(
            "--diarize/--no-diarize",
            help="Annotate who is speaking (speaker diarization)",
        ),
    ] = True,
) -> None:
    """Download YouTube audio and optionally transcribe with ElevenLabs.

    Accepts a YouTube video or playlist URL, downloads audio (preferring Opus format),
    and sends it to ElevenLabs Scribe v1 for transcription with speaker diarization.

    Examples:
        ytscribe fetch https://www.youtube.com/watch?v=VIDEO_ID
        ytscribe fetch https://www.youtube.com/playlist?list=PLAYLIST_ID
        ytscribe fetch VIDEO_URL --skip-transcribe
        ytscribe fetch VIDEO_URL --language spa --no-diarize
    """
    try:
        # Load and validate configuration
        config = get_config()

        typer.echo("ytscribe v0.1.0")
        typer.echo(f"URL: {url}")
        typer.echo(f"Download root: {config.download_root}")
        typer.echo(f"Transcript root: {config.transcript_root}\n")

        # Initialize downloader
        downloader = AudioDownloader(config.download_root)

        # Download audio
        try:
            downloaded_files = downloader.download(url, skip_existing=True)
        except Exception as e:
            typer.secho(f"\n✗ Download failed: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(1)

        # Summary
        typer.echo(f"\n✓ Downloaded {len(downloaded_files)} file(s)")

        if skip_transcribe:
            typer.secho(
                "\n⏭  Skipping transcription (--skip-transcribe)",
                fg=typer.colors.YELLOW,
            )
        else:
            typer.echo("\n[Phase 2 Complete - Phase 3 Pending]")
            typer.echo("Transcription will be implemented in Phase 3.")
            typer.echo("Transcription options:")
            typer.echo(f"  Language: {language or 'auto-detect'}")
            typer.echo(f"  Tag audio events: {tag_audio_events}")
            typer.echo(f"  Diarize: {diarize}")

    except ValueError as e:
        typer.secho(f"Configuration error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


def main() -> None:
    """Entry point for the CLI application."""
    app()
