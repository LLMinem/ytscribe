# Phase 3 Implementation Plan

**Last Updated:** 2025-11-24

## Executive Summary

This session successfully completed Phase 3 of the ytscribe project, implementing full ElevenLabs Scribe v1 transcription integration. The tool now provides an end-to-end workflow from YouTube URL to high-quality transcripts with speaker diarization. Additionally, the project was migrated to GitHub with a comprehensive roadmap documented via issues.

## Current State Analysis

### What Was Completed

1. **Phase 3: ElevenLabs Transcription Integration** ✅
   - Created `src/ytscribe/transcriber.py` (268 lines)
   - Implemented file validation (3GB/10h limits)
   - Added JSON and Markdown transcript generation
   - Integrated transcriber into CLI with progress tracking
   - Comprehensive error handling for API failures

2. **Documentation Updates** ✅
   - Updated README.md with usage examples and troubleshooting
   - Removed "Detailed Timeline" section from Markdown output per user request

3. **GitHub Migration** ✅
   - Archived old `ytscribe` repository → `ytscribe-old`
   - Created new repository at: https://github.com/LLMinem/ytscribe
   - Pushed all code (7 commits)

4. **Roadmap Planning** ✅
   - Created 7 GitHub issues documenting future phases
   - Issues cover: database, file naming, local files, VPS deployment, API, MCP server

### Current Architecture

```
ytscribe/
├── src/ytscribe/
│   ├── __init__.py       # Entry point
│   ├── config.py         # Environment config (Phase 1)
│   ├── cli.py            # Typer CLI (Phase 1, updated Phase 3)
│   ├── downloader.py     # YouTube audio downloader (Phase 2)
│   └── transcriber.py    # ElevenLabs integration (Phase 3) ← NEW
├── data/
│   ├── audio/            # Downloaded Opus files
│   └── transcripts/      # JSON + Markdown outputs
└── docs/
    ├── project-plan.md
    └── Elevenlabs/       # API reference docs
```

### Commits Made This Session

1. `ee8d2cc` - feat: implement ElevenLabs transcription integration
2. `ac59614` - docs: update README with Phase 3 usage and troubleshooting

## Proposed Future State

### Immediate Priority: Phase 4 (Database + File Naming)

**Goal:** Prevent duplicate transcriptions and improve file naming

**Key Components:**
- SQLite database in `data/ytscribe.db`
- Track: video_id, url, title, channel, dates, status, file paths
- Change filename format: `{title_sanitized}_{upload_date}.opus`
- Database module: `src/ytscribe/database.py`

**User Motivation:**
- Has 100k ElevenLabs credits to burn in 22 days (~200 hours)
- Needs to avoid accidentally re-transcribing the same video
- Wants human-readable filenames

### Future Phases (GitHub Issues Created)

- **Phase 5:** Local file transcription support (#3)
- **Phase 6:** VPS deployment with Docker + FastAPI (#4)
- **Phase 7:** Generalized upload API for iOS integration (#5)
- **Future:** Auto-process playlist additions (#6)
- **Future:** MCP server for AI agents (#7)

## Implementation Phases

### Phase 4: Database & File Naming (NEXT)

**Estimated Effort:** 2-3 hours

**Tasks:**
1. Create database schema and module
2. Implement video tracking functions
3. Update downloader to check/update database
4. Update transcriber to log status
5. Modify file naming logic
6. Test with existing and new videos
7. Update documentation

**Acceptance Criteria:**
- Database created on first run
- Duplicate videos are skipped automatically
- Filenames use title instead of video_id
- All metadata properly tracked

### Phase 5: Local File Support

**Estimated Effort:** 30-45 minutes

**Tasks:**
1. Add file path detection in CLI
2. Skip yt-dlp for local files
3. Implement smart conversion logic
4. Update database schema for local files
5. Test with various formats

### Phase 6-7: VPS & API Deployment

**Estimated Effort:** 4-8 hours total

**Deferred:** User wants Docker/Docker Compose approach
- Will require FastAPI setup
- Background job processing
- Tailscale integration for secure access

## Risk Assessment and Mitigation

### Current Risks

1. **ElevenLabs API Reliability** ⚠️
   - **Issue:** Long videos (>3 hours) may fail with 500 errors
   - **Evidence:** Encountered with 3.5-hour video (trace ID: 192868d7c75a50cc1840355f206b071e)
   - **Mitigation:**
     - Add retry logic for 500 errors
     - Consider auto-splitting videos >2 hours
     - Document file splitting recommendations

2. **API Key Management** ⚠️
   - **Issue:** API key stored in shell environment, not `.env` file
   - **Current:** Works but could be confusing for new users
   - **Mitigation:** Document environment variable precedence in README

3. **File Naming Edge Cases** ⚠️
   - **Issue:** Video titles with special characters may cause filesystem issues
   - **Mitigation:** Robust sanitization logic in Phase 4

### Resolved Issues

1. ✅ Markdown detailed timeline removed per user request
2. ✅ Language auto-detection fixed (was sending empty string)
3. ✅ Repository properly migrated to GitHub

## Success Metrics

### Phase 3 Success Criteria (All Met) ✅

- [x] Transcription works with real ElevenLabs API
- [x] JSON and Markdown outputs generated
- [x] All CLI flags functional (language, diarize, tag-audio-events)
- [x] Error handling graceful
- [x] Code formatted and linted
- [x] Documentation complete

### Phase 4 Success Criteria (Upcoming)

- [ ] Database prevents duplicate transcriptions
- [ ] Filenames are human-readable
- [ ] All metadata tracked correctly
- [ ] Works with both new and existing videos
- [ ] Database queries functional

## Required Resources and Dependencies

### Current Dependencies

**Runtime:**
- Python 3.14+
- elevenlabs SDK
- yt-dlp
- typer
- python-dotenv
- FFmpeg (system dependency)

**Development:**
- ruff (formatting + linting)
- pytest (tests not yet written)
- prettier (markdown formatting)
- just (command runner)

### Phase 4 Additional Requirements

**New Dependencies:**
- None (SQLite is built into Python)

**New Modules:**
- `src/ytscribe/database.py`

## Timeline Estimates

### Completed (This Session)

- Phase 3 Implementation: ~2 hours
- Documentation: ~30 minutes
- GitHub setup: ~15 minutes
- Issue creation: ~30 minutes
- **Total:** ~3 hours 15 minutes

### Upcoming (Estimated)

- Phase 4 (Database): 2-3 hours
- Phase 5 (Local files): 30-45 minutes
- Phases 6-7 (VPS/API): 4-8 hours
- Future phases: TBD

## Technical Decisions Made

### 1. Language Parameter Handling

**Decision:** Conditionally include `language_code` in API call
**Reason:** ElevenLabs SDK converts `None` to empty string, causing 400 error
**Implementation:** Build kwargs dict, only add language_code if truthy

### 2. Markdown Format Simplification

**Decision:** Remove "Detailed Timeline" section
**Reason:** User feedback - JSON already contains all granular data
**Impact:** Cleaner Markdown output, easier reading

### 3. File Naming Strategy

**Decision:** Defer to Phase 4 with database integration
**Reason:** Need database for uniqueness guarantees
**Proposed:** `{title_sanitized}_{upload_date}.opus`

### 4. Repository Migration

**Decision:** Archive old attempt, use `ytscribe` name for working version
**Reason:** Clean slate, proper naming for production tool
**Result:** https://github.com/LLMinem/ytscribe

## Next Immediate Steps

1. **Test the error retry** - Re-run failed 3.5-hour video transcription
2. **Implement Phase 4** - Database and file naming improvements
3. **Handle long videos** - Add retry logic or splitting recommendations
4. **Document API key precedence** - Clarify environment variable behavior

## Notes and Observations

### API Key Discovery

The tool works despite `.env` having `test_key_for_phase1_validation` because:
- Real API key (`sk_c38ef2b...`) is set in shell environment
- `os.getenv()` checks shell environment first, then `.env`
- This is actually good security practice (secret not in file)

### Performance Characteristics

- Download speed: ~8-10 MB/s average
- Transcription time: ~1-2 minutes for 19-second video
- File size: Opus at 64kbps is very efficient (~64MB for 3.5 hours)

### User Workflow Preferences

- Wants Docker/Docker Compose for VPS deployment
- Plans heavy usage (100k credits in 22 days)
- iOS Shortcuts integration is priority
- MCP server for AI integration is exciting future goal
