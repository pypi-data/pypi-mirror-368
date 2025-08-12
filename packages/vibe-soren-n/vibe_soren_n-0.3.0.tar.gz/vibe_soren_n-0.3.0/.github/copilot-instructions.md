# Vibe Project — AI Agent Guide (Concise)

Goal: Use Vibe to develop Vibe while minimizing token usage and rate-limit hits.

## MCP tools (minimal set)
- start_workflow, get_workflow_status, advance_workflow, back_workflow,
  restart_workflow, break_workflow, list_workflow_sessions.
Use them for step-wise execution and compact status.

## When uncertain
- Ask Vibe first. Examples: "run quality checks", "set up Python env", "create ADR", "start development session".

## Anti-patterns (avoid)
- Skipping Vibe guidance; long narrative replies; repeating unchanged sections; copying large docs; running tools without brief preamble and compact post-summary.

## Validation (fast path)
- Ask: "what quality checks should I run?" then run those commands.
- Keep outputs terse (summaries + PASS/FAIL and next step).

## Categories (where workflows live)
- core, python, frontend, documentation, development, session, automation, testing, media.

## Minimal examples
- Discovery: uv run vibe guide "help me test my Python code"
- Validation: uv run vibe guide "validate my recent changes"
- Docs: uv run vibe guide "create documentation for X"

## Success criteria
- Guidance-first behavior demonstrated; compact outputs; validation run; reusable patterns captured.

## Troubleshooting (short)
- If a workflow isn’t found: check YAML name/category.
- If guidance is noisy: enable/keep concise mode; summarize results.
- If rate-limited: pause/retry with backoff; split large outputs; reduce detail.
