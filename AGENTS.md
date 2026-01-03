# Repository Guidelines

## Project Structure & Required Context

- Source lives in `src/ytscribe/`; downloaded media sits under `data/audio/` and transcripts under `data/transcripts/` (keep `.gitkeep` files).
- Documentation root: `docs/` (start with `docs/plans/2025-12-29-logging-reliability-design.md`; `docs/project-plan.md` is historical). Read the design doc **before** making changes, then run `git ls-files` and review the latest five commits (`git log -5 --oneline`) to understand history each session.
- Config: `.env.example`, `pyproject.toml`, `uv.lock`, `.gitignore`, `.python-version`.

## Build, Test, and Development Commands

**Use Just for all formatting and linting tasks.** Just is a command runner that simplifies common workflows.

- `just format` — format all Python code (ruff) and Markdown files (prettier). **Always run before committing.**
- `just lint` — lint Python code with ruff to catch errors.
- `just check` — run both format and lint in one command.
- `just test` — run the pytest test suite (add tests under `tests/` when created).
- `just sync` — install locked runtime + dev dependencies (alias for `uv sync`).
- `uv run ytscribe <url>` — run the CLI (also supports `uv run ytscribe fetch <url>`).

Direct commands (if needed):

- `uv sync` — install dependencies.
- `uv run ruff format .` / `uv run ruff check .` — format + lint Python.
- `prettier --write "**/*.md"` — format Markdown files.

## Coding Style & Naming Conventions

- Python 3.14+, 4-space indentation, type hints encouraged.
- Use Typer for CLI surfaces and favor small, composable modules (`downloader.py`, `transcriber.py`, etc.).
- **Always run `just format` before committing** to format Python (ruff) and Markdown (prettier) files. Markdown wraps at ~100 characters.

## Testing Guidelines

- Framework: `pytest`. Name files `test_*.py`.
- Cover format-selection helpers, config parsing, and mocked ElevenLabs uploads as they land; add fixtures for yt-dlp metadata.
- Future integration tests should be gated behind environment flags to avoid hitting real APIs.

## Commit & Pull Request Guidelines

- **Always run `just format` before committing.** This ensures all Python and Markdown files are properly formatted.
- Prefer atomic, logically grouped commits using conventional prefixes (e.g., `feat:`, `fix:`, `docs:`). Always inspect staged changes with `git diff --staged` before committing.
- A pre-commit hook runs `ruff check` automatically - it will block commits if there are linting errors (but won't modify files).
- Document user-visible changes in `README.md` or `docs/` immediately to avoid drift.
- PRs (if used) should describe motivation, testing performed, and any follow-up tasks.

## Agent-Specific Instructions

- Treat the user as a 10-month developer: explain the “why,” keep language beginner-friendly, and favor reliability over cleverness. Surface DX improvements whenever you spot friction.
- Plan work explicitly (list steps), keep documentation current, and narrate trade-offs.
- Use the Ref MCP server when lint/runtime errors suggest an API mismatch or when you’re unsure about the latest version of a dependency; don’t spam it for routine edits.
