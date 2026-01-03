# ytscribe Planning Brief

> **Status:** Historical. The current direction is the logging/reliability design in `docs/plans/2025-12-29-logging-reliability-design.md`. An implementation plan will be created next; database/file-naming work is postponed until observability is improved.

## 1. Project goals & scope

- Build a repeatable CLI workflow that (a) downloads audio from any YouTube video or playlist, (b) stores the audio under a deterministic path inside this repo, and (c) uploads the asset to ElevenLabs Scribe v1 for transcription.
- Prioritize reliability and simplicity over extra features; video support can come later.
- Provide a foundation (project structure, docs, tooling choices) for a follow-up implementation agent.

## 2. Key requirements distilled from the user

- Accept a single URL that could be a video or playlist; automatically handle playlist enumeration but keep UX lightweight (likely a single command).
- Prefer Opus itag 250 (~64–70 kbps) for downloads when available; gracefully fall back to another high-quality audio-only track if it is missing.
- Output audio-only files in a consistent format ElevenLabs accepts (Opus/WebM or FLAC/M4A are all valid per `docs/Elevenlabs/speech-to-text.md`).
- Automate uploads to ElevenLabs’ `/speech-to-text/convert` API with the `scribe_v1` model, tagging audio events and diarization as defaults the user can override later.
- Respect current ElevenLabs constraints: max 3 GB / 10 h per file, up to 32 speakers, 99 languages, webhook optional (`docs/Elevenlabs/speech-to-text.md`, `docs/Elevenlabs/async-stt-webhook.md`).
- Keep credentials in environment variables (`ELEVENLABS_API_KEY`, optional `ELEVENLABS_WEBHOOK_SECRET`).

## 3. Tooling decisions

### 3.1 Language/runtime

- Use Python 3.12+ managed by [uv](https://docs.astral.sh/uv/). uv gives us reproducible dependency locking, fast installs, and single-command script execution (`uv run`, `uv pip`, `uv lock`).
- Create a `pyproject.toml` via `uv init --package ytscribe` so we get a project with an entry-point script (`ytscribe/__main__.py`) and `uv.lock` for pinned deps.

### 3.2 External tools

- **yt-dlp** (CLI + embedded Python module) for downloads; it supports thousands of sites, playlists, format filtering (`-f/--format`), sorting (`-S/--format-sort`), chunked downloads, and needs FFmpeg for audio post-processing (see docs/research/yt-dlp.md).
- **FFmpeg** for container/codec conversions. yt-dlp shell-outs to FFmpeg when we use `-x/--extract-audio` or remuxing, so it must be on PATH.
- **scrape** CLI already present for persisting reference docs; keep curated resources under `docs/research/` (done for yt-dlp + uv).

### 3.3 Python dependencies (initial)

- `yt-dlp` (if we embed it instead of invoking CLI directly—keeps arguments in Python land and unifies logging).
- `httpx` or `requests` for ElevenLabs uploads (sdk `elevenlabs` is also option; quickstart shows `elevenlabs` package usage).
- `pydantic` (optional) for typed config.
- `rich`/`textual` (optional) for nicer CLI output—probably overkill for v0; standard `typer` or `argparse` is enough.
- `python-dotenv` if we want `.env` support during `uv run`.

### 3.4 Minimum DX stack to lock in

- `typer` for the single-command CLI, expandable later without rewrites.
- `yt-dlp` + `elevenlabs` SDK as runtime dependencies, managed through `uv add`.
- `ruff` (formatter + linter) and `pytest` configured via UV scripts; MyPy can be added later if needed but is optional today.
- All dependencies—app or tooling—must be added with `uv add ...` so the lockfile stays authoritative.

## 4. Proposed workflow

1. **Command interface** (e.g., `uv run ytscribe download <youtube_url> [--transcribe/--skip-transcribe]`).
2. **Download planning**
   - Probe metadata with `yt_dlp.YoutubeDL({'skip_download': True})` to learn available formats.
   - Prefer format `bestaudio[abr<=70][acodec^=opus]/bestaudio` or explicitly request itag 250 if present.
   - Save under `data/audio/{playlist_title or channel}/{upload_date}_{video_id}.opus` (configurable root).
3. **Audio normalization**
   - If the fetched stream is already Opus-in-WebM, store as-is.
   - Otherwise, run FFmpeg via yt-dlp post-processing to transcode to Opus 64k using `--audio-format opus --audio-quality 64K` to keep ElevenLabs-friendly format.
4. **Transcription dispatcher**
   - For synchronous MVP: read file bytes into memory (or stream chunked) and call `ElevenLabsClient.speech_to_text.convert` with options `model_id='scribe_v1'`, `tag_audio_events=True`, `diarize=True`, `language_code='eng'` or `None` for auto-detect.
   - For near-future: support `webhook=True` + metadata to move to async mode.
5. **Result handling**
   - Persist JSON response under `data/transcripts/{same_base}.json` plus pretty `.md` or `.txt` summary.
   - For playlists, optionally collate transcripts into a single folder index.

## 5. Implementation task backlog for the next agent

1. Initialize the uv project (`uv init --package ytscribe`), add base dependencies with `uv add ...`, create `uv.lock`.
2. Add `.env.example` documenting `ELEVENLABS_API_KEY`, default download root, optional webhook data.
3. Implement a small config module that reads `.env`/env vars and ensures `downloads/` + `transcripts/` directories exist.
4. Wrap yt-dlp functionality in `ytscribe/downloader.py`:
   - Format selection helper (prefer itag 250; fallback order; raise actionable errors if nothing matches).
   - Playlist iteration + metadata capture (title, index, url, duration, channel).
   - Option to skip downloads that already exist (checksum by file name or `--no-overwrite`).
5. Add `ytscribe/transcriber.py` using the ElevenLabs Python SDK (per `docs/Elevenlabs/stt-quickstart.md`). Include toggles for `tag_audio_events`, `diarize`, `language_code`, `webhook`.
6. Build CLI entry point (Typer or argparse) that wires download + transcription steps, with flags for `--only-download`, `--only-transcribe`, `--playlist`, `--output-dir`.
7. Provide structured logging + progress output (maybe `rich` progress bars for playlist jobs).
8. Write docs: `README.md` usage, `docs/usage.md` with reproducible commands, `docs/troubleshooting.md` for yt-dlp/ffmpeg gotchas.
9. (Stretch) Add simple regression tests for format selection + config parsing (pytest) and a mocked ElevenLabs uploader to avoid hitting API during CI.

## 6. Risks & caveats

- Opus itag 250 is not guaranteed; must fall back gracefully (documented format tables show availability varies per upload).
- Playlist downloads can be throttled by YouTube; we may need to expose yt-dlp rate-limit args or cookies if the playlist is private.
- Files longer than 10 hours / 3 GB must be split before upload; plan for a future `segmenter` helper using FFmpeg’s `-f segment`.
- Need to surface API failure states (429s, 5xx) and implement retries with exponential backoff to avoid losing downloads.
- Storing raw audio quickly consumes disk; add an optional `--cleanup-audio` flag to delete files once ElevenLabs confirms receipt.

## 7. Decisions (as of 2025-11-09)

1. **Execution model**: ship a synchronous flow first; CLI waits for each ElevenLabs transcript to finish. Async/webhook mode can be layered on later for high-volume playlists.
2. **Storage layout**: keep everything under `data/audio/` and `data/transcripts/` within this repo for now.
3. **Artifacts**: write both `.json` (raw API response) and `.md` (reader-friendly) outputs per transcription.
4. **CLI UX**: single `ytscribe fetch <url>` command with flags for optional behaviors, no separate subcommands.
5. **Diarization**: always enabled (`diarize=True`) in every request.
6. **Fallbacks**: ElevenLabs is the sole transcription backend; no local/GPU alternative required.

## 8. Reference materials on disk

- ElevenLabs docs already mirrored under `docs/Elevenlabs/`.
- Fresh yt-dlp README snapshot: `docs/research/yt-dlp.md`.
- uv quickstart references: `docs/research/uv*.md`.

This document plus the scraped references should equip the next agent to begin implementation without re-doing the research.
