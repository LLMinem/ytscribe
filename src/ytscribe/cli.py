"""Command-line interface for ytscribe.

Provides a Typer-based CLI for downloading YouTube audio and transcribing with ElevenLabs.
"""

from typing import Optional

import typer
from typing_extensions import Annotated

from ytscribe.config import get_config
from ytscribe.downloader import AudioDownloader
from ytscribe.transcriber import Transcriber

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
            # Transcribe downloaded files
            typer.echo("\n🎙️  Starting transcription...\n")

            transcriber = Transcriber(config)
            success_count = 0
            error_count = 0

            for idx, audio_file in enumerate(downloaded_files, 1):
                typer.echo(
                    f"[{idx}/{len(downloaded_files)}] 🎙️  Transcribing: {audio_file.name}"
                )

                try:
                    result = transcriber.transcribe(
                        audio_path=audio_file,
                        language=language,
                        tag_audio_events=tag_audio_events,
                        diarize=diarize,
                    )

                    typer.secho("  ✓ API request successful", fg=typer.colors.GREEN)
                    typer.echo(f"  ✓ Saved: {result['json_path']}")
                    typer.echo(f"  ✓ Saved: {result['md_path']}")
                    success_count += 1

                except Exception as e:
                    typer.secho(f"  ✗ Error: {e}", fg=typer.colors.RED, err=True)
                    error_count += 1
                    # Continue with remaining files
                    continue

            # Final summary
            typer.echo("")
            if success_count > 0:
                typer.secho(
                    f"✓ Transcribed {success_count} of {len(downloaded_files)} file(s) successfully",
                    fg=typer.colors.GREEN,
                )
            if error_count > 0:
                typer.secho(
                    f"✗ Failed to transcribe {error_count} file(s)",
                    fg=typer.colors.RED,
                    err=True,
                )

    except ValueError as e:
        typer.secho(f"Configuration error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


def main() -> None:
    """Entry point for the CLI application."""
    app()
