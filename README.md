# ytscribe

Minimal CLI workflow for downloading YouTube audio (via yt-dlp) and transcribing it with ElevenLabs Scribe v1. Download videos or playlists, get high-quality Opus audio, and receive detailed transcripts with speaker diarization and timestamps.

## Requirements

- [uv](https://docs.astral.sh/uv/) (manages Python 3.12+ runtimes, deps, and scripts)
- `ffmpeg` available on your `PATH` (yt-dlp uses it for muxing/transcoding)
- ElevenLabs account + `ELEVENLABS_API_KEY`

## Getting started

1. **Install dependencies**

   ```bash
   uv sync
   ```

2. **Configure API key**

   Copy `.env.example` to `.env` and add your ElevenLabs API key:

   ```bash
   cp .env.example .env
   # Edit .env and set ELEVENLABS_API_KEY=your-key-here
   ```

   Get your API key at: https://elevenlabs.io/app/settings/api-keys

3. **Run your first transcription**

   ```bash
   uv run ytscribe "https://www.youtube.com/watch?v=VIDEO_ID"
   ```

## Usage

### Basic Commands

**Download and transcribe a video:**

```bash
uv run ytscribe "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Download only (skip transcription):**

```bash
uv run ytscribe "VIDEO_URL" --skip-transcribe
```

**Process an entire playlist:**

```bash
uv run ytscribe "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

### Transcription Options

**Specify language (skip auto-detection):**

```bash
uv run ytscribe "VIDEO_URL" --language spa  # Spanish
uv run ytscribe "VIDEO_URL" --language fra  # French
```

**Disable speaker diarization:**

```bash
uv run ytscribe "VIDEO_URL" --no-diarize
```

**Disable audio event tagging (laughter, applause, etc):**

```bash
uv run ytscribe "VIDEO_URL" --no-tag-audio-events
```

**Combine options:**

```bash
uv run ytscribe "VIDEO_URL" --language eng --no-tag-audio-events
```

### Output Files

**Audio files:** `data/audio/{channel}/{YYYYMMDD}_{video_id}.opus`

- High-quality Opus format (~64kbps)
- Organized by channel/playlist name
- Dated with upload date for easy sorting

**Transcript files:**

- **JSON:** `data/transcripts/{channel}/{YYYYMMDD}_{video_id}.json`
  - Raw API response with all metadata
  - Word-level timestamps and speaker IDs
  - Audio events (if enabled)
- **Markdown:** `data/transcripts/{channel}/{YYYYMMDD}_{video_id}.md`
  - Human-readable format
  - Full transcript text
  - Detailed timeline with speakers
  - Audio event annotations

### Project Structure

```
ytscribe/
├── src/ytscribe/        # Source code
│   ├── config.py        # Configuration management
│   ├── cli.py           # Command-line interface
│   ├── downloader.py    # YouTube audio downloader
│   └── transcriber.py   # ElevenLabs transcription
├── data/
│   ├── audio/           # Downloaded audio files (gitignored)
│   └── transcripts/     # Generated transcripts (gitignored)
└── docs/                # Documentation and research
```

## Development Commands

**Format code and markdown:**

```bash
just format    # Runs ruff + prettier
```

**Lint Python code:**

```bash
just lint      # Runs ruff check
```

**Run all checks:**

```bash
just check     # Format + lint
```

**Install/sync dependencies:**

```bash
just sync      # or: uv sync
```

## Status

✅ **Phase 1-3 Complete:** Full download + transcription pipeline

- Config management with environment variables
- YouTube audio downloader with playlist support
- ElevenLabs Scribe v1 integration
- JSON and Markdown transcript generation
- Comprehensive error handling
- Speaker diarization and audio event tagging

## Troubleshooting

**"Authentication failed" or 401 errors:**

- Check your `.env` file has a valid `ELEVENLABS_API_KEY`
- Get a key at: https://elevenlabs.io/app/settings/api-keys
- Make sure there are no extra spaces or quotes around the key

**"Rate limit exceeded" or 429 errors:**

- ElevenLabs API has concurrency limits based on your plan
- Wait a few minutes and try again
- Consider upgrading your ElevenLabs plan for higher limits
- Process smaller batches if transcribing playlists

**"File size exceeds 3GB" errors:**

- ElevenLabs has a 3GB / 10 hour limit per file
- Try downloading a shorter segment of the video
- Future enhancement: audio splitting support will be added

**"FFmpeg not found" errors:**

- Install FFmpeg: `brew install ffmpeg` (macOS) or see https://ffmpeg.org/download.html
- Verify installation: `which ffmpeg`
- Make sure FFmpeg is in your system PATH

**Download succeeds but transcription fails:**

- Check your ElevenLabs API quota hasn't been exhausted
- Verify the audio file exists in `data/audio/`
- Try running with `--language eng` to skip auto-detection
- Check the error message for specific API issues

**Pydantic V1 compatibility warning:**

- This is a known warning from the ElevenLabs SDK with Python 3.14
- It doesn't affect functionality and can be safely ignored
- The warning will be resolved when the SDK updates to Pydantic V2

## API Costs

ElevenLabs charges per minute of audio transcribed. See their [pricing page](https://elevenlabs.io/pricing) for current rates. The CLI will display how many files were processed, which you can use to estimate costs.

## Contributing

See `AGENTS.md` for development guidelines and coding standards.
