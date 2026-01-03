# Logging + Reliability Design

**Date:** 2025-12-29
**Status:** Current (approved)

## Goal
Improve observability, reliability, and perceived responsiveness without changing the core download/transcribe workflow. The tool should show where time is spent, avoid silent stalls, and skip work that was already completed.

## Scope (This Phase)
- Replace ad-hoc prints with Loguru (console + rotating file logs).
- Add stage timers and heartbeat logs for long-running steps.
- Switch yt-dlp to single-pass download (no pre-extract pass).
- Use yt-dlp download archive to skip already-downloaded videos (by ID).
- Skip transcription if output files already exist, with a --force override.
- Add targeted retries for transient errors (429/5xx) with backoff.
- Preserve current audio/transcript file layout.
- Preserve "ytscribe URL" UX via root callback forwarding to fetch.

## Non-Goals (Deferred)
- Database-based tracking (postponed).
- Major refactors or new features beyond logging/skip reliability.
- Full automated test suite (manual smoke tests only for now).

## Design Summary
### Logging
- Use Loguru for all logs.
- Log to console and rotating files under `logs/`.
- Default level: INFO. Add `--debug` for verbose logs (options, paths, context).

### Timers + Heartbeats
- Track stage durations: metadata/download, transcription, total.
- Emit heartbeat logs during metadata and transcription when no progress output is available.
- Skip heartbeat for download (already has progress output).

### Single-Pass Download + Skip
- Remove explicit metadata-only extraction.
- Use yt-dlp output template to keep current layout:
  - `data/audio/{channel}/{upload_date}_{id}.opus`
- Use yt-dlp `download_archive` at `data/download_archive.txt` to skip re-downloads.

### Transcription Skip + Force
- If both transcript files exist (.json and .md), skip transcription.
- Add `--force` to override this and re-transcribe.

### Error Handling
- Retry transient download/transcription errors (429/5xx) with backoff (e.g., 10s, 30s).
- Log failure context: URL, video ID, stage, elapsed time, and error message.
- In debug mode, include stack traces.

### UX Compatibility
- Keep `ytscribe fetch URL` working.
- Add root CLI callback so `ytscribe URL` also works now and in the future.
- Always print final summary with counts and per-stage timings.

## Acceptance Criteria
- Runs produce clear logs in terminal and `logs/` files.
- No long silent stalls during metadata/transcription (heartbeat visible).
- Single URL download avoids double metadata pass.
- Previously downloaded videos are skipped via archive.
- Previously transcribed videos are skipped unless `--force`.
- Final summary includes timings and counts every run.

## Manual Test Plan
1. Short video: verify logs, heartbeat, and outputs.
2. Repeat same URL: download skipped via archive; transcription skipped via outputs.
3. Force re-transcription with `--force`: transcription runs again.
4. Optional: run with `--debug` to ensure extra detail appears.

## Notes
- URL format differences are resolved by relying on yt-dlp video IDs.
- Database phase stays postponed until observability is solid.
