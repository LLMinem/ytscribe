# ytscribe

Minimal CLI workflow for downloading YouTube audio (via yt-dlp) and transcribing it with ElevenLabs Scribe v1. This repo currently focuses on planning + scaffolding; implementation will build on the decisions captured in `docs/project-plan.md`.

## Requirements

- [uv](https://docs.astral.sh/uv/) (manages Python 3.12+ runtimes, deps, and scripts)
- `ffmpeg` available on your `PATH` (yt-dlp uses it for muxing/transcoding)
- ElevenLabs account + `ELEVENLABS_API_KEY`

## Getting started

1. **Install deps**
   ```bash
   uv sync
   ```
2. **Configure secrets**
   - Copy `.env.example` to `.env` and fill `ELEVENLABS_API_KEY` (plus optional path overrides).
3. **Project structure**
   - Source lives under `src/ytscribe/`.
   - Audio downloads land in `data/audio/`.
   - Transcripts land in `data/transcripts/` (both JSON + Markdown per job).

## Tooling

- Runtime deps are managed with `uv add ...` (see `pyproject.toml` + `uv.lock`).
- `ruff` handles formatting + linting: `uv run ruff format .` / `uv run ruff check .`.
- `pytest` is available for tests once implementation lands.

## Status

- Research + planning captured in `docs/`.
- Implementation agent TBD—see forthcoming instructions file.
