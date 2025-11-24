# Phase 3 Implementation Context

**Last Updated:** 2025-11-24
**Session Start:** 2025-11-17
**Session End:** 2025-11-24
**Agent:** Claude Sonnet 4.5

## Session Overview

This session spanned one week with a break in between. Started with implementation planning, completed Phase 3 transcription integration, migrated to GitHub, and encountered/analyzed an ElevenLabs API error with long videos.

## Key Files Modified

### Created Files

1. **`src/ytscribe/transcriber.py`** (268 lines)
   - Main transcription logic
   - ElevenLabs API integration
   - File validation (3GB/10h limits)
   - Output generation (JSON + Markdown)
   - Error handling with user-friendly messages

### Modified Files

1. **`src/ytscribe/cli.py`**
   - Added `from ytscribe.transcriber import Transcriber`
   - Replaced Phase 3 placeholder with full transcription loop
   - Added progress tracking per file
   - Added success/error counting and summary

2. **`README.md`**
   - Complete rewrite of Getting Started section
   - Added comprehensive Usage section with examples
   - Added Troubleshooting section
   - Updated Status to reflect Phase 1-3 completion
   - Added Development Commands section

### Removed Code

**From `transcriber.py`:**
- Removed "Detailed Timeline" section generation (lines 142-165)
- User feedback: redundant with JSON data, makes MD files too long

## Implementation Decisions

### 1. Transcriber Architecture

**File Validation:**
```python
def _validate_audio_file(self, audio_path: Path) -> None:
    # Check existence
    # Check file size < 3GB
    # Check not empty
```

**Output Path Generation:**
```python
def _generate_output_paths(self, audio_path: Path) -> tuple[Path, Path]:
    # Mirror audio structure in transcripts/
    # Extract channel from relative path
    # Return (json_path, md_path)
```

**Markdown Generation:**
```python
def _generate_markdown(self, transcript_data: dict, audio_path: Path) -> str:
    # Metadata section
    # Full transcript text
    # Audio events (if any)
    # NO detailed timeline (removed per user request)
```

### 2. API Call Strategy

**Problem:** ElevenLabs SDK converts `None` to empty string for `language_code`
**Solution:** Build kwargs dict conditionally

```python
api_kwargs = {
    "file": audio_file,
    "model_id": "scribe_v1",
    "tag_audio_events": tag_audio_events,
    "diarize": diarize,
}
if language:  # Only add if explicitly provided
    api_kwargs["language_code"] = language

response = self.client.speech_to_text.convert(**api_kwargs)
```

### 3. Error Handling

**Approach:** Catch all exceptions, provide context, continue processing

```python
try:
    result = transcriber.transcribe(...)
except Exception as e:
    typer.secho(f"  ✗ Error: {e}", fg=typer.colors.RED, err=True)
    error_count += 1
    continue  # Process remaining files
```

**Error types handled:**
- Authentication (401)
- Rate limiting (429)
- File too large (413)
- Server errors (500)
- Network errors

## Integration Points

### CLI → Transcriber Flow

1. User runs: `uv run ytscribe "URL"`
2. CLI loads config via `get_config()`
3. Downloader fetches audio to `data/audio/{channel}/{date}_{id}.opus`
4. If not `--skip-transcribe`:
   - Initialize `Transcriber(config)`
   - Loop through downloaded files
   - Call `transcriber.transcribe()` for each
   - Save to `data/transcripts/{channel}/{date}_{id}.{json,md}`

### File Path Convention

**Audio:** `data/audio/{channel_sanitized}/{YYYYMMDD}_{video_id}.opus`
**JSON:** `data/transcripts/{channel_sanitized}/{YYYYMMDD}_{video_id}.json`
**MD:** `data/transcripts/{channel_sanitized}/{YYYYMMDD}_{video_id}.md`

**Example:**
```
data/audio/jawed/20050424_jNQXAC9IVRw.opus
data/transcripts/jawed/20050424_jNQXAC9IVRw.json
data/transcripts/jawed/20050424_jNQXAC9IVRw.md
```

## Testing Performed

### Successful Tests ✅

1. **Basic transcription** - 19-second "Me at the zoo" video
   - Auto-detected language: English (99% confidence)
   - Generated both JSON and MD outputs
   - All timestamps and speaker IDs present

2. **Skip transcribe flag** - `--skip-transcribe` works correctly

3. **Explicit language** - `--language eng` accepted

4. **Disabled features** - `--no-diarize` and `--no-tag-audio-events` work

5. **Code quality** - All code passes `ruff format` and `ruff check`

### Known Issues ⚠️

1. **Long video API failures**
   - Video: 3h28m Shawn Ryan Show episode
   - Error: HTTP 500 from ElevenLabs
   - Trace ID: `192868d7c75a50cc1840355f206b071e`
   - Status: Server-side issue, not client code bug
   - Mitigation needed: Retry logic or file splitting

2. **Pydantic V1 warning**
   - ElevenLabs SDK incompatible with Python 3.14
   - Warning appears but doesn't affect functionality
   - Will be resolved when SDK updates

## Blockers and Issues

### Current Blocker

**ElevenLabs API 500 Error on Long Videos**

**Symptom:** 3.5-hour video fails with server error
**Root Cause:** ElevenLabs internal processing timeout/failure
**Evidence:**
- HTTP 500 (server error, not client)
- Message: "something_went_wrong"
- "You are not charged for this request"

**Potential Solutions:**
1. Retry the same video (may work second time)
2. Add automatic retry with exponential backoff
3. Split videos >2 hours before transcription
4. Contact ElevenLabs support with trace ID

**Status:** Deferred - waiting for user decision on priority

### Minor Issues

1. **API key in environment, not .env file**
   - User confused about where key comes from
   - Key is in shell environment: `ELEVENLABS_API_KEY=sk_c38ef2b...`
   - This is actually good (more secure)
   - Need to document in README

## GitHub Migration

### Actions Taken

1. Renamed old repo: `ytscribe` → `ytscribe-old`
2. Archived old repo (marked deprecated)
3. Created new repo: https://github.com/LLMinem/ytscribe
4. Pushed 7 commits to new repo
5. Set up remote tracking: `origin = git@github.com:LLMinem/ytscribe.git`

### Issues Created

| Issue | Title | Priority |
|-------|-------|----------|
| [#1](https://github.com/LLMinem/ytscribe/issues/1) | Phase 4: Add SQLite database for video tracking | HIGH |
| [#2](https://github.com/LLMinem/ytscribe/issues/2) | Improve file naming convention | HIGH |
| [#3](https://github.com/LLMinem/ytscribe/issues/3) | Phase 5: Add local file transcription support | MEDIUM |
| [#4](https://github.com/LLMinem/ytscribe/issues/4) | Phase 6: VPS deployment with Docker | MEDIUM |
| [#5](https://github.com/LLMinem/ytscribe/issues/5) | Phase 7: Generalized upload API | LOW |
| [#6](https://github.com/LLMinem/ytscribe/issues/6) | Future: Auto-process playlist additions | FUTURE |
| [#7](https://github.com/LLMinem/ytscribe/issues/7) | Future: MCP server for AI agents | FUTURE |

## Next Immediate Actions

### Before Next Development Session

1. **Test error retry:**
   ```bash
   uv run ytscribe "https://youtu.be/4p3kNCrJ31w"
   ```
   Audio file already exists, will skip download and retry transcription

2. **Verify git status:**
   ```bash
   git status
   git log --oneline -5
   ```

### Phase 4 Preparation

1. Review database schema in issue #1
2. Decide on file naming format (title_date vs date_title)
3. Plan migration for existing files (optional)

### Commands to Run on Session Start

```bash
# Sync environment
just sync

# Check git status
git status

# List existing transcripts
ls -lh data/transcripts/*/

# Check current issues
gh issue list
```

## Architectural Observations

### What Works Well

1. **Modular design** - Each phase builds on previous cleanly
2. **Error handling** - Graceful failures, continues processing
3. **Output flexibility** - Both JSON (machine) and MD (human) formats
4. **Progress tracking** - Clear feedback during long operations
5. **Config management** - Environment-based, easy to deploy

### Areas for Improvement

1. **No database** - Can't track what's been processed
2. **No retry logic** - API failures are permanent
3. **No file splitting** - Long videos problematic
4. **No tests** - All testing manual so far
5. **File naming** - Date+ID format not human-friendly

## User Workflow Insights

### Current Usage Pattern

- Has 100k ElevenLabs credits (~200 hours of transcription)
- Credits expire in 22 days
- Needs to burn through credits efficiently
- Risk of re-transcribing same videos

### Future Vision

1. **Database** - Track everything, prevent duplicates
2. **Local files** - Transcribe anything, not just YouTube
3. **VPS + API** - Run on server, access from iPhone/Mac
4. **iOS integration** - Shortcuts app for quick transcriptions
5. **MCP server** - AI agents can transcribe videos on-demand

### Technical Preferences

- Docker/Docker Compose for deployment
- FastAPI for APIs
- Tailscale for secure networking
- Simple, robust solutions over complex ones

## Environment Details

**Python Version:** 3.14+
**Package Manager:** uv
**Formatter:** ruff + prettier
**Linter:** ruff
**Command Runner:** just
**Version Control:** git + GitHub CLI (gh)

**Key Environment Variables:**
- `ELEVENLABS_API_KEY` - Set in shell (not .env file)
- `DOWNLOAD_ROOT` - Default: data/audio
- `TRANSCRIPT_ROOT` - Default: data/transcripts

## Uncommitted Changes

**Status:** All changes committed ✅

**Latest commits:**
- `ac59614` - docs: update README with Phase 3 usage and troubleshooting
- `ee8d2cc` - feat: implement ElevenLabs transcription integration

**Git Status:** Clean working tree (except new `dev/` directory)

## Session Insights

### What Went Smoothly

- Phase 3 implementation completed in ~2 hours
- GitHub migration executed perfectly
- All tests passed on first try
- Documentation comprehensive

### What Was Challenging

- Debugging the `language_code` empty string issue
- Understanding why API key worked without being in .env
- Deciding on file naming strategy (deferred to Phase 4)

### Lessons Learned

1. ElevenLabs API can handle 19-second videos instantly
2. Long videos (3+ hours) are risky for API timeouts
3. Environment variables override .env files
4. User wants database before proceeding with heavy usage
5. Markdown timeline section was not valued by user

## Handoff Notes for Next Session

### Exact State

- **Current branch:** main
- **Last commit:** ac59614
- **Working directory:** Clean (dev/ is new, not yet committed)
- **Remote:** https://github.com/LLMinem/ytscribe

### Priority Tasks

1. **Decide:** Fix ElevenLabs error now or implement Phase 4 first?
2. **Implement Phase 4:** Database + file naming (user priority)
3. **Document:** API key environment precedence
4. **Test:** Long video retry or splitting strategy

### Test Commands

```bash
# Test existing functionality
uv run ytscribe "https://www.youtube.com/watch?v=jNQXAC9IVRw"

# Retry failed video
uv run ytscribe "https://youtu.be/4p3kNCrJ31w"

# Test with explicit language
uv run ytscribe "URL" --language eng

# Test skip transcribe
uv run ytscribe "URL" --skip-transcribe
```

### Context to Remember

- User returned after 1-week break
- Encountered 500 error on 3.5-hour video
- Wants to prioritize database implementation
- Has aggressive timeline (100k credits in 22 days)
- Prefers documentation before implementation
