# Development Documentation

This directory contains strategic planning and session handoff documentation for the ytscribe project.

## Structure

```
dev/
├── README.md              # This file
└── active/                # Active development sessions
    └── phase-3-implementation/
        ├── phase-3-plan.md        # Comprehensive strategic plan
        ├── phase-3-context.md     # Session context and decisions
        └── phase-3-tasks.md       # Task checklist with progress
```

## Documentation Files

### `*-plan.md` - Strategic Plan
Comprehensive planning document including:
- Executive Summary
- Current State Analysis
- Proposed Future State
- Implementation Phases
- Risk Assessment
- Success Metrics
- Timeline Estimates

### `*-context.md` - Session Context
Session-specific details including:
- Files modified
- Implementation decisions
- Integration points
- Testing performed
- Blockers and issues
- Handoff notes

### `*-tasks.md` - Task Checklist
Task tracking with:
- Completed tasks (✅)
- In progress tasks (🔄)
- Pending tasks (📋)
- Blocked tasks (🚫)
- Deferred tasks (⏸️)

## Usage

### Starting a New Session

1. Read the latest `*-context.md` to understand current state
2. Review `*-tasks.md` to see what's pending
3. Check `*-plan.md` for overall strategy

### During Development

- Update `*-context.md` with decisions and discoveries
- Check off completed tasks in `*-tasks.md`
- Add new tasks as they're discovered

### Before Context Reset

Run the `/dev-docs-update` command to ensure all documentation is current:
- Update implementation state
- Document key decisions
- Note blockers and next steps
- Update task progress

### After Completing a Phase

1. Mark all tasks complete in `*-tasks.md`
2. Update `*-context.md` with final state
3. Create new directory for next phase
4. Archive or move completed phase documentation

## Current Active Work

**Phase:** 3 - ElevenLabs Transcription Integration (COMPLETED)
**Status:** ✅ Implemented, tested, and committed
**Next:** Phase 4 - Database & File Naming

## Guidelines

### When to Create New Documentation

Create a new `dev/active/{phase-name}/` directory when:
- Starting a new major phase or feature
- Switching to a different area of the codebase
- Beginning work after a long break
- Context window is getting full

### Documentation Best Practices

- **Update frequently:** Don't wait until end of session
- **Be specific:** Include file names, line numbers, exact commands
- **Document decisions:** Explain WHY, not just WHAT
- **Track blockers:** Note issues that need resolution
- **Include examples:** Code snippets, commands, output samples

### File Naming Convention

Use descriptive, hyphenated names:
- ✅ `phase-4-database-plan.md`
- ✅ `api-integration-context.md`
- ✅ `refactor-downloader-tasks.md`
- ❌ `plan.md` (too generic)
- ❌ `context_2.md` (unclear purpose)

## Integration with Git

Documentation files should be committed to the repository:

```bash
# Commit documentation after completing a session
git add dev/
git commit -m "docs: add Phase 3 implementation documentation"

# Or commit with main code
git add dev/ src/
git commit -m "feat: implement feature X + documentation"
```

## Benefits of This System

1. **Survives context resets** - All knowledge persisted to disk
2. **Onboards new contributors** - Complete project history
3. **Tracks decisions** - Why choices were made
4. **Enables planning** - Clear roadmap and priorities
5. **Facilitates handoffs** - Between agents or developers
6. **Documents learnings** - Solutions to problems

## Related Documentation

- `/docs/project-plan.md` - Original project planning
- `/README.md` - User-facing documentation
- `/AGENTS.md` - Agent-specific guidelines
- GitHub Issues - Roadmap and feature tracking
