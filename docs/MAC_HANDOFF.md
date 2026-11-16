# Mac Validation Handoff

## Purpose

This repository was refactored and tested on Windows without launching the
macOS-focused GUI. This document describes the resulting structure, the checks
already completed, and the remaining Mac runtime validation.

## Completed Work

### Architecture

- Added a dependency-light `domain/` and `application/` layer for conversation
  turns, intent parsing, prompt building, Home Assistant actions, memory,
  pending-action decisions, and scheduling.
- Kept Qt-specific behavior at the controller and adapter boundaries.
- Moved external concerns behind adapters: legacy conversation, Home Assistant,
  memory, web search, Telegram, Qt scheduling, provider HTTP, and settings
  storage.
- Split Ollama and LM Studio HTTP behavior from the Qt LLM worker.
- Extracted model download polling, progress state, and cancellation into a
  non-Qt service while retaining the existing worker signal interface.

### Package Layout

The former flat `jarvis_assistant` module directory is now grouped without
splitting the original source files:

| Package | Responsibility |
| --- | --- |
| `app/` | Controller and application entrypoint |
| `application/` | Headless use cases |
| `audio/` | Recording, STT, and TTS |
| `core/` | Configuration, paths, secrets, and utilities |
| `domain/` | Models, outcomes, and ports |
| `infrastructure/` | Concrete adapters and provider support |
| `intelligence/` | Agents, intent helpers, and quick commands |
| `integrations/` | Home Assistant, memory, and conversation storage |
| `providers/` | LLM worker and model catalogs |
| `ui/` | PyQt GUI modules |

`run.py` is the canonical entrypoint and the PyInstaller spec uses it.
`entry.py` is a compatibility shim.

### Documentation

- `docs/ARCHITECTURE_REFACTOR_PLAN.md` tracks completed and deferred work.
- `docs/HEADLESS_WORKFLOW.md` documents the Windows-safe checks.
- Private research transcripts and runtime data are intentionally excluded from
  the public source repository.

## Windows Evidence

The following passed before this handoff:

```bash
python -m compileall -q jarvis_assistant tests
python -m unittest discover -s tests -q
python -c "import run, entry; assert entry.main is run.main"
git diff --check
```

The suite has 41 dependency-light tests covering the new application services,
provider clients, model downloads, configuration migration, and adapters. No
real web search, Telegram delivery, provider request, or Home Assistant action
was issued during those tests.

## Mac Validation Checklist

Run these checks on the target Mac before further structural refactors:

1. Install project dependencies and start the source launcher.
2. Open the main window and each settings panel.
3. Verify Ollama and LM Studio connection tests, model listing, download,
   cancellation, selection, and removal.
4. Verify microphone permission, push-to-talk, wake word, speech recognition,
   and cancellation behavior.
5. Verify Piper and macOS-system TTS playback.
6. Set and read a test credential through the macOS keychain-backed settings
   flow. Do not commit credentials.
7. Exercise a test Home Assistant action against a non-critical entity.
8. Build the DMG with the existing release script, install it, and verify the
   packaged app launches and can access bundled assets.

## Deferred Work

- Split `ui/gui.py` into focused UI modules after the live GUI is validated.
- Extract acknowledgement timer and request-cancellation state from
  `app/controller.py`.
- Remove inactive legacy implementations only after a Mac release checkpoint.

## Recent Commits

- `d3667a7` - Refactor assistant core and integrations
- `d9e1010` - Organize assistant modules by capability
