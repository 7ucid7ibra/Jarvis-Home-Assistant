# Jarvis Architecture Refactor Plan

This is the working checklist for the incremental refactor. Keep the current
application behavior working after each phase. Do not make broad file moves
until the new boundary has tests and a working adapter.

## Working Rules

- Prefer small, reversible changes over a rewrite.
- Keep Qt at the UI and worker boundary.
- Keep provider, audio, persistence, and Home Assistant integrations behind
  application-facing interfaces.
- Use standard-library tests where possible; do not require macOS to test the
  headless core.
- Run compilation, tests, and `git diff --check` after each batch.
- Validate GUI, microphone, macOS keychain, and DMG behavior on a Mac agent.

## Phase 0: Baseline

- [x] Map entrypoints and package responsibilities.
- [x] Identify oversized orchestration modules.
- [x] Confirm the repository starts with a clean working tree.
- [x] Add a documented headless smoke command.
- [x] Record the current text-input and voice-input behavior.

## Phase 1: Headless Application Spine

- [x] Add domain conversation message types.
- [x] Add conversation and text-generation ports.
- [x] Add `AssistantService` for a complete synchronous text turn.
- [x] Add a legacy conversation adapter.
- [x] Route user-input normalization and persistence through the service.
- [x] Route assistant-response persistence through the service.
- [x] Add a provider adapter boundary for the existing asynchronous LLM worker.
- [x] Add a controller-level smoke test with fake providers.

## Phase 2: Extract Intent Processing

- [x] Extract intent prompt construction from `JarvisController`.
- [x] Extract structured intent parsing and validation.
- [x] Define application results for conversation, action, and clarification.
- [x] Keep Qt signal handling in the controller adapter.
- [x] Add tests for valid JSON, fenced JSON, web-search tool calls, plain
  conversation replies, and rejected control-like plain text.

## Phase 3: Separate Actions And Integrations

- [ ] Extract Home Assistant action execution behind a port.
- [x] Introduce the first Home Assistant service-call port and legacy adapter.
- [x] Extract and test the core Home Assistant action execution and verification path.
- [x] Cover Home Assistant action failure and timeout behavior.
- [x] Extract memory operations behind a port.
- [x] Introduce the memory port and legacy adapter for active controller operations.
- [x] Extract web search and Telegram operations behind ports.
- [ ] Move scheduling and confirmation state into application services.
- [x] Extract delayed-task scheduling and confirmation/cancellation decisions.
- [x] Add fake integration tests for action success/failure, download
  cancellation, and pending-action confirmation flows.

## Phase 4: Split Providers And Configuration

- [x] Separate Ollama and LM Studio connection and text-generation implementations.
- [x] Separate model catalog access from text generation.
- [x] Extract model download progress and cancellation from the Qt worker.
- [x] Separate JSON settings persistence and secret storage from the `Config` facade.
- [x] Preserve legacy settings migration with dedicated tests.

## Phase 5: Split The UI

- [ ] Split `gui.py` into the main window, settings dialog, widgets, model UI,
  resource monitor, and theme/animation modules.
- [ ] Make UI classes call application services instead of implementing domain
  decisions.
- [ ] Preserve the existing visual behavior during the split.

## Phase 6: Cleanup And Release Validation

- [x] Group existing modules into capability packages without splitting their contents.
- [x] Choose one canonical entrypoint and make the other a compatibility shim.
- [x] Add a documented test and development workflow.
- [ ] Update packaging only after imports stabilize.
- [x] Run Windows headless checks.
- [ ] Run Mac GUI, audio, keychain, and DMG checks.
- [ ] Remove obsolete compatibility code only after a release checkpoint.

## Next Milestone

1. Validate the GUI, audio, keychain, and packaging flow on macOS.
2. Extract acknowledgement and request-cancellation state from the controller.
3. Split the settings and model-management UI from `gui.py`.
