# Headless Workflow

Use this command on Windows or any machine without the macOS audio stack to
exercise the text-processing spine without opening the Qt application:

```powershell
python -m unittest discover -s tests -p "test_headless_text_flow.py" -v
```

Run the full headless verification before committing a refactor milestone:

```powershell
python -m compileall -q jarvis_assistant tests
python -m unittest discover -s tests -v
git diff --check
```

## Current Behavior Baseline

This describes the current source behavior. It is not a substitute for GUI,
audio, keychain, or packaging validation on macOS.

### Text Input

1. The controller ignores empty input and refuses new text while a request is
   transcribing, classifying intent, executing an action, or generating a
   response.
2. A valid message is normalized and persisted through `AssistantService`.
3. The controller updates Qt state, starts acknowledgements and timeouts, then
   passes recent history, memory, Home Assistant entities, capabilities, and
   time context to `IntentRequestService`.
4. The Qt LLM adapter receives a JSON-format intent request.
5. The response is classified as structured intent, web-search tool call,
   unsafe plain-text control request, or direct conversation.
6. A direct reply is persisted, displayed, and sent to TTS. Structured intents
   continue through the existing action and response pipeline.

### Voice Input

1. Recording completion enters transcription unless the capture is empty.
2. Empty transcription restores idle state and resumes wake-word listening.
3. Non-empty transcription uses the same `_process_user_input` path as text.
4. A wake-word interrupt can stop recording, TTS, or an in-flight LLM request
   before starting a new wake-word recording.
