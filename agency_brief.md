# RESUME.md — Havenwright interruption-recovery handoff

**Read this file and HANDOFF.md before editing anything.** HANDOFF.md describes the architecture, and this file describes the current state.
Last written: 2026-10-19 03:34 (system clock) by the previous coding agent (Claude Code).
Times in this file come from the system clock or file timestamps. Where only the order is known, it says "before".
This is a note, so it can go stale: inspect the actual files and rerun the tests before trusting it.

---

## 0. Work log (keep this current)

| When | Step | Status |
|---|---|---|
| before 03:33 | Read-only checks: secret scan, checkpoint comparison, full test rerun on a copy | DONE: see section 5 |
| before 03:33 | Rewrite RESUME.md (this file) | DONE |
| 03:33:48 | Add a RESUME pointer to HANDOFF.md | DONE: a banner at the top of HANDOFF.md. A hash diff against `checkpoint-20261019-032223` shows exactly the 6 files listed in section 3, and no data changes |
| 03:33:57 | Make a current-state checkpoint and verify it | DONE: `checkpoint-20261019-033357`, `Checked 41 files: OK`, 0 secret-pattern matches. **This row and the time corrections were written after that checkpoint**, so its copy of RESUME.md shows this step as IN PROGRESS. The live RESUME.md is newer |
| 03:34 | Read back RESUME.md and HANDOFF.md | DONE: contents confirmed on disk. The handoff work is complete. The live project differs from `checkpoint-20261019-033357` only in this file (`RESUME.md`) |
| after 03:34 | AI integration inspection (read-only; no code changes) and recording the findings in section 11 | DONE: findings in section 11. Evidence came from code reading plus checks on a copy, with the network blocked and a mock transport |
| 03:41:31 | **New task: focused AI safety fix** (search-off config per model, tool/citation rejection, finish_reason, approval binding). Pre-edit checkpoint taken | DONE: `checkpoint-20261019-034131`, Verified (41 files). Only RESUME.md differed from 033852 |
| 03:42–03:46 | Read Poe's docs and public model metadata (no project data, no key, no inference) | DONE. Public catalog `GET https://api.poe.com/v1/models` fetched without auth at 03:42:36: 336 models, sha256 prefix `3ab10c1d567f4eee`. The models use 24 different search-related parameter names, many **on by default**. **Documentation conflict:** the OpenAI-compatible page says custom bot params go via `extra_body`, but the Client SDKs page says the OpenAI-compatible API has "No custom parameter support". Neither documents the raw HTTP placement. **Decision: build the mechanism, keep every model BLOCKED.** |
| 03:42–03:48 | Edit `ai_analysis.py`: reviewed search-off table (5 models, all blocked), search-off fields in the body, approval bound to the full request, a lock on tokens, tool/citation/finish_reason checks | DONE (code written, not yet tested). Also changed `dashboard.html` (the preview shows the search-off fields and review status, and the card shows the fields used) |
| 03:42–03:48 | Update `test_ai_analysis.py` for the new body and model rules. Add `test_ai_safety.py` | DONE: both pass (mocked, network blocked). Mutation check: dropping the search-off field or disabling the metadata check makes `test_ai_safety.py` fail, as it should |
| before 03:48:48 | Run the full suite on a fresh copy, then update HANDOFF.md and RESUME.md | DONE: all 9 test scripts pass. Production data is unchanged. HANDOFF.md has a "Search-off safety fix" section, and this file has section 12 |
| 03:48:48 | Post-change checkpoint | The checkpoint is **the first `checkpoint-*` folder created after 2026-10-19 03:48:48**. It was taken immediately after this row was written, and no file was edited afterwards, so it contains these final notes. Check it with `python backup.py --verify <folder>` |
| 12:02 | Record the user's browser check of the disabled AI preview (sections 4 and 12). Notes only; no code changed, no external requests | DONE. Checkpoint: the first `checkpoint-*` folder created after 2026-10-19 12:02:27, taken right after this edit |
| 12:04:18 | **New task: draft-only marketing workflow.** Pre-edit checkpoint | DONE: `checkpoint-20261019-120418`, Verified (42 files) |
| after 12:04 | Agent inventory (read-only): `src\*.py`, `app.py`, `dashboard.html`, `run_agent.py`, `auto_gen.py`, Task Scheduler | DONE: see section 13. No project scheduled task exists |
| after 12:04 | Build `campaigns.py` + routes + Marketing page campaign workflow + `test_campaigns.py` | DONE: see section 13. All 10 test scripts pass on a fresh copy (network blocked in the new test); mutation check OK; production data unchanged |
| before final checkpoint | Update HANDOFF.md and this file; post-change checkpoint | The post-change checkpoint is **the first `checkpoint-*` folder created after this row was written** (taken immediately afterwards, no later edits) |
| 16:17:39 | **New task: research workflow.** Pre-edit checkpoint | DONE: `checkpoint-20261019-161739`, Verified (44 files). Since 120851 only `logs\run_history.jsonl` changed (one user Marketing Agent run at 16:14:01). No `data\campaigns.json` yet |
| after 16:17 | Build `research.py` (local sources, run controls) + routes + Contractors → Research tab + `test_research.py` | DONE: see section 14. All 11 test scripts pass on a fresh copy; mutation check OK; HTTP run/stop/blocked checked on a copy server; production data unchanged |
| before final checkpoint | Update HANDOFF.md and this file; post-change checkpoint | The post-change checkpoint is **the first `checkpoint-*` folder created after this row was written** (taken immediately afterwards, no later edits) |
| 16:40:29 | **User approved ("allow all make them operational") the bounded L&I run from section 14.** Interpreted as: max 2 public requests to data.wa.gov, $0, listed fields only, and a working adapter. NOT covered: Poe/paid AI, outreach, publishing, ad spend. Pre-edit checkpoint | DONE: `checkpoint-20261019-164029`, Verified (46 files) |
| after 16:40 | Request 1 (dataset catalog lookup), adapter + offline tests, request 2 (Lacey query) | DONE: see section 15. 16:40:41 catalog lookup confirmed `m8qx-ubtq`; 11 test scripts pass offline; 16:42:27 live run `research-5c041fb9c387` completed, 25 findings saved. **2 external requests total, $0.** Production briefs/notes/shortlists/prospects unchanged |
| before final checkpoint | Update HANDOFF.md and this file; post-change checkpoint | The post-change checkpoint is **the first `checkpoint-*` folder created after this row was written** |
| 2026-10-20 20:59:11 | **New task: n8n operations dashboard + Agency specialist catalog.** Pre-edit checkpoint | DONE: `checkpoint-20261020-205911`, Verified (48 files) |
| after 20:59 | Discovery: n8n not installed (no command, no npm global, no ~/.n8n, nothing on :5678, no Docker, WSL not installed); Node v24.19.0 present; no ~/.claude/agents or project .claude/agents; Agency repo at `C:\Users\relli\Downloads\agency-agents-main\agency-agents-main` (from agency-agents-main.zip, MIT, no .git) | DONE: see section 16 |
| after 20:59 | Build catalog.py, n8n.py, workflow export, research n8n source, routes, Agent Library + Workflows pages, tests, docs/ | DONE: see section 16. 12 test scripts + test_dashboard pass on a fresh copy; 5 mutations detected; production briefs/prospects/research/history unchanged |
| before final checkpoint | Update HANDOFF.md and this file; post-change checkpoint | The post-change checkpoint is **the first `checkpoint-*` folder created after this row was written** |
| 03:38:52 | Checkpoint this RESUME.md | DONE: `checkpoint-20261019-033852`, `Checked 41 files: OK`, 0 secret-pattern matches, section 11 included. Its copy shows this row as IN PROGRESS, because this row was written afterwards |
| 2026-10-24 18:47 | **New task: "Infinite Context" memory layer** — SQLite context store (`context_manager.py`), `.env` loading, memory injection before LLM calls, trend-scan memory saves, HQ Memory Status widget. Pre-edit checkpoint | IN PROGRESS. Pre-edit checkpoint: `checkpoint-20261024-184714`, Verified (112 files). Brief said the app was in `memecoin-ai/`; it is `C:\generational_run` (discrepancy reported to the user in chat) |

**Rule:** before each substantial edit, add a row marked IN PROGRESS. After it, record the outcome and the tests.

---

## 1. Successor rules (mandatory)

- Only **one** coding agent may edit the project at a time.
- Read HANDOFF.md and RESUME.md before editing.
- Notes may be stale. Inspect the actual files and rerun the relevant tests.
- Preserve unfinished work before changing it: run `python backup.py` and check that it prints "Verified."
- Continue the existing implementation. Do not rebuild or refactor unrelated features.
- **Never restore over working files without the user's approval.** Restore only into a new, empty folder unless the user says otherwise.
- Use isolated test data (temporary folders, as the existing tests do). Never alter real records for testing.
- No live AI calls, spending, outreach, dependency installation, deployment, or destructive changes without the user's approval.
- If these notes and the code conflict, report the discrepancy to the user before proceeding.
- Never write API keys or other secrets into any file in `C:\generational_run` (backups copy project files) or into chat.

---

## 2. Current milestone: Manual AI project analysis, disabled by default

**Original acceptance criteria (as the user requested, condensed):**
1. An "Analyze project" option on each brief, with a preview of the exact outgoing data:
   - Included: goals, scope, approximate location, budget, timing, review info, and only the real prospects the operator selected
     (their capabilities, evidence, and verification status).
   - Excluded: contact details, paths, credentials, Activity, and unrelated records. Notes stay out unless explicitly ticked.
   - The preview explains that data leaves the computer and uses the provider allowance, and every request needs explicit confirmation.
2. A server-side adapter for Poe's OpenAI-compatible API (from the official docs):
   - The model is configurable, and no model ID is guessed.
   - The key comes from a server environment variable only and is never written to HTML, records, logs, or backups.
   - Disabled until configured and explicitly enabled, with "AI not configured" shown meanwhile.
   - No automatic calls of any kind, and no dependency installed without asking.
3. Structured output:
   - Missing info and homeowner questions, specialties with reasoning, possible fits among the selected prospects (by ID)
     with evidence and uncertainties, and a next action. "Insufficient evidence" and an empty list are allowed.
   - Nothing invented, records treated as untrusted, and no tools, browsing, outreach, or code.
   - Output and IDs validated, safe rendering, and the label "AI suggestions — not verified or approved".
4. Storage and control:
   - Analyses kept separate from review notes and shortlists, and statuses or links never changed automatically.
   - Model, timestamp, and input fingerprint stored, with a stale flag. Safe writes and backups.
   - Bounded sizes and timeouts, double-click prevention, no automatic retries, and a note that the output limit is not a spending cap.
   - Missing credentials, insufficient allowance, timeouts, and malformed replies handled without damaging records.
   - No sensitive content in Activity.
5. Mocked tests only and isolated files. Run the existing tests, update HANDOFF.md and RESUME.md, make a verified checkpoint.

**Status, from the files I inspected and the tests I reran on 2026-10-19 (before 03:33):**

| Area | Status | Evidence |
|---|---|---|
| 1. Analysis interface (preview, selection, opt-in notes, notices, confirmation) | IMPLEMENTED; NOT browser-checked | `dashboard.html` (`analysisPanel`, `selectionForm`, `previewView`, `analysisCard`); `ai_analysis.preview` |
| 2. Poe adapter, env-only key, disabled by default, no auto calls | IMPLEMENTED; NEVER run live | `ai_analysis.py` (`config`, `call_provider`, `_urllib_transport`); mocked tests |
| 3. Structured output, validation, ID checks, labels | IMPLEMENTED; mock-tested | `ai_analysis.validate`; `test_ai_analysis.py` |
| 4. Storage, fingerprint and stale flag, limits, one-time token, error handling, log privacy | IMPLEMENTED; mock-tested | `ai_analysis.analyze` / `with_stale_flags`; `app.ai_request` |
| 5. Tests and handoff | DONE (mocked only) | section 5 below |
| Search-off safety fix (follow-up task) | IMPLEMENTED; mock-tested. **Every model is blocked** because of the Poe documentation conflict (section 12) | `ai_analysis.REVIEWED_MODELS`; `test_ai_safety.py` |
| Live AI request | **BLOCKED: not authorized.** No model chosen, no key configured | none of the 3 environment variables are set at Process, User, or Machine scope (checked by name only) |
| Browser verification of the AI panel | PARTIAL: user saw the disabled preview with no model set (section 4). Search-off preview lines not yet seen | user report |

**Not done on purpose:** no live call, no `GET /v1/models` call, no dependency installed, no Task Scheduler change.

---

## 3. Files changed in this milestone (all complete; no partial edits)

Since the known-good checkpoint `checkpoint-20261019-032223`:
- `ai_analysis.py`: **new**, the whole AI path.
- `test_ai_analysis.py`: **new**, mocked tests.
- `app.py`: added `ai_state()`, `AI_ROUTES`, `ai_request()`, two AI entries in `PATHS`, and AI routing in `do_POST`.
  `ai` was added to `/api/state`.
- `dashboard.html`: added the AI panel functions, an `ai-status-line` in the Projects section, and `ai: "AI analysis"` in `NAMES`.
- `HANDOFF.md`: AI sections, test results, configuration steps, and the pointer to this file.
- `RESUME.md`: **new** (this file).
- Unchanged: `store.py`, `projects.py`, `prospects.py`, `backup.py`, `src\*`, and all data files.
  No `data\analyses.json` exists yet, because no analysis has ever been saved.

---

## 4. What the user confirmed vs. what the agent tested

**Reported by the user in the browser (not re-verified by me):**
- Project briefs work.
- Review notes persist.
- Shortlist add and remove work, and removing a link leaves the prospect intact.
- Earlier: agent results, ad previews, diagnostics, and Activity history render.
- "AI not configured" notice shown (section 11).
- **2026-10-19 (recorded 12:02): disabled AI preview.** With no key and no model configured, the preview opened and showed
  `candidate_businesses: []`, `max_tokens: 2000`, `stream: false`, a sending-blocked warning, and only "Close preview" (no Send button).
  The request showed `model: "(model not configured)"` and **no `web_search` field**, which is correct when no model is set.
  **So the model-specific search-off preview lines are still NOT browser-verified.** No live analysis was authorized; every model stays blocked.

**Never confirmed in a browser by anyone:**
- **AI:** the search-off/review-status/approval-scope preview lines (need a reviewed model name set), the approval checkbox,
  sending state, results, the "sent with" line, and the stale flag.
- **Projects and branding:** the DEMO banner and checkbox, the single-column brief layout, the Projects "Show" filter,
  and the Havenwright sidebar branding.
- **Prospects and Overview:** prospect form duplicate dialog, the Backup now button, and the clipboard buttons.

---

## 5. Tests the agent actually ran (2026-10-19, before 03:33, on a fresh copy of the current files)

The copy was `...\scratchpad\regress_handoff`, with the dashboard API served on 127.0.0.1:5055 and backups redirected to scratch.

| Command | Result |
|---|---|
| `python test_dashboard.py http://127.0.0.1:5055` | PASS (exit 0) |
| `python test_engine.py` | PASS (prints SUCCESS twice). Note: this script prints FAIL but still exits 0 on failure, so read its output |
| `python test_marketing.py` | PASS (prints output). It has no assertions, so it only proves the code runs |
| `python test_prospects.py` | PASS (exit 0) |
| `python test_projects.py` | PASS (exit 0) |
| `python test_review.py` | PASS (exit 0) |
| `python test_ai_analysis.py` | PASS (exit 0). **MOCKED provider, no network.** This does not prove that Poe accepts the request, that a model follows the JSON format, or what a request costs |
| `node --check` on the page script | PASS |
| `compile()` of all 15 root `.py` files | PASS |
| Secret-pattern scan of the project and all backups (Bearer or `sk-` tokens, `POE_API_KEY=value`, api_key literals, `.env` or key files) | 0 matches |

**Untested:** everything in section 4 not reported by the user, any live Poe request, a full disk,
a restore on another machine, and concurrent edits from two browser tabs.

---

## 6. Checkpoints (`C:\generational_run_backups\`)

| Role | Identifier | Verify result | Meaning |
|---|---|---|---|
| **Known-good** | `checkpoint-20261019-032223` | `Checked 38 files: OK` (verified before 03:33 during this handoff) | The last state before the AI milestone. Its code is byte-identical to `checkpoint-20261019-031318` (the review/shortlist milestone the user browser-confirmed); only the user's data differs. **File integrity is verified; that it is a working app comes from the user's report, not a fresh browser test.** |
| Previous current | `checkpoint-20261019-033021` | `Checked 41 files: OK` (verified before 03:33) | AI milestone complete, before this handoff rewrite |
| **Current state** | `checkpoint-20261019-033357` at `C:\generational_run_backups\checkpoint-20261019-033357` | `Checked 41 files: OK` (03:33:57); 0 secret-pattern matches | AI milestone code complete. **Mock-tested only, NOT browser-verified, never live-tested.** Not labeled INCOMPLETE: every code item in the acceptance criteria exists and passes its tests. The open items (browser check, live call) are waiting on the user |

- Every checkpoint is kept. Nothing has ever been pruned.
- `checkpoint-20261019-021744` is an old 9-file manual copy with no manifest. It is incomplete, so don't use it.
- **A checkpoint that verifies only proves its files match its manifest. It does not prove the app works.**

---

## 7. Exact next smallest safe action (for a replacement coder)

1. Make sure no other agent is editing.
2. Run `cd /d C:\generational_run`, then `python backup.py`, and confirm it prints "Verified."
3. Compare the files to section 3. If anything differs, report it to the user before proceeding.
4. Rerun the tests (section 8). Expect all to pass.
5. **Do not start a feature.** Read section 12: section 11's fixes A to C are implemented, but every model is blocked
   by a Poe documentation conflict. Then ask the user for the pending decisions:
   - (a) DONE by the user with no model set (section 4). Still open: set `HAVENWRIGHT_AI_MODEL` to a reviewed (blocked) model
     such as `claude-sonnet-4.6`, with no key and AI still disabled, and check that the preview shows `"web_search": false`,
     the BLOCKED review status, and no Send button.
   - (b) Choose a Poe model name. The user configures the key themselves.
   - (c) Authorize exactly **one** live analysis of the DEMO brief `project-fefd9e157750`.
     Record the outcome in HANDOFF.md under "Pending decision: first live AI request".

---

## 8. Restart and test commands (Windows CMD)

**Restart the dashboard:**
- **Running server mismatch:** during this handoff (before 03:33), a server was running on port 5000 (PID 28120, started 03:14:21), from **before** the AI code.
  It serves the new `dashboard.html` (the page is read on every request) but runs the old `app.py`,
  so the AI routes return 404 until it is restarted.
- Stop it with Ctrl+C in its window, then run each line separately:
```
cd /d C:\generational_run
python app.py
```
Then open http://127.0.0.1:5000. You should see "AI not configured" on the Projects page.

**Tests:**
- Run these from `C:\generational_run`. They use temporary folders and never touch real records.
  test_dashboard also runs agent actions, which append entries to the real Activity log.
  To avoid that, run it against a copy, as section 5 did.
```
python test_engine.py
python test_marketing.py
python test_prospects.py
python test_projects.py
python test_review.py
python test_ai_analysis.py
python test_ai_safety.py
python test_campaigns.py
python test_research.py
```
- `test_dashboard.py` needs a running server. Start `python app.py` in another window, then run `python test_dashboard.py`.

**Backup:**
- Create: `python backup.py`
- Verify: `python backup.py --verify C:\generational_run_backups\<checkpoint>`
- Restore only into a new, empty folder, and only with user approval.
  The full steps are in HANDOFF.md under "Backup and restore" and in each backup's RESTORE.md.

---

## 9. Dependencies and configuration (no secret values)

- Python 3.12 (3.12.10 was used here). Standard library only, with no third-party packages and no requirements file.
- Node.js was used only for the optional `node --check` syntax test.
- `auto_gen.py` (an old, unused script) needs the `anthropic` package and its own key. It is not part of the dashboard.
- AI analysis needs server environment variables. **None are set now.**
  - `POE_API_KEY`: the user creates it at poe.com/api/keys and types it only into their own terminal.
  - `HAVENWRIGHT_AI_MODEL`: a Poe model name chosen by the user. There is no default.
  - `HAVENWRIGHT_AI_ENABLED=1`: leave it unset until the user authorizes a live call.
  - The steps are in HANDOFF.md under "Configuration steps".

---

## 10. Outstanding risks

- **Stale server: resolved.** During the inspection, port 5000 was served by PID 31288, started 03:32:45,
  which is after the AI code was written. The user has restarted the server.
- **Never run live:** the AI path has never been exercised against Poe.
  Model behavior, JSON compliance, cost, and the real error bodies are all unknown.
- **Server waits during AI calls:** the server is single-threaded, so a live call freezes the dashboard for up to about 90 seconds per socket operation.
  That timeout is not a total-duration cap.
- **Weak guards:**
  - The email/phone/path guard is pattern-based and won't catch names or street addresses.
  - Two old tests (`test_engine.py`, `test_marketing.py`) don't fail with a nonzero exit code.
- **Backups grow forever:** both the backups folder and the `data\*_backups` folders are never pruned.
- **No offsite copy:** every backup is on the same disk.
- **Web search:** section 11's finding A has been addressed in code, but it is unproven on the wire (see section 12).
  Every model is blocked from sending.

---

## 11. AI integration inspection (2026-10-19, read-only; no application code changed)

**User report:** the user saw **"AI not configured"** in the browser.
That confirms only that the notice renders. It does not confirm that preview works in the browser, that sending works,
or that any live analysis has happened. None of those have been browser-tested or run live.

**How the evidence was gathered:**
- I read `ai_analysis.py` and the AI routes in `app.py`.
- I ran checks on a copy (`...\scratchpad\inspect_ai`) with `urlopen` patched to raise, no AI environment variables,
  and a mock transport. No external request was made.

1. **Endpoint and request.** The request is `POST https://api.poe.com/v1/chat/completions` (`ai_analysis.ENDPOINT`),
   sent with urllib `Request(method="POST")`, a timeout of 90 seconds per socket operation, and a reply read capped at 200 KB.
   - Headers: `Authorization: Bearer <POE_API_KEY>` and `Content-Type: application/json`.
   - Body (`request_body()`); the preview shows it exactly, apart from the headers:
     ```
     {"model": "<HAVENWRIGHT_AI_MODEL>",
      "messages": [{"role": "system", "content": "<fixed SYSTEM_PROMPT>"},
                   {"role": "user", "content": "Analyze this project for internal planning.\n<project_data>\n<payload JSON>\n</project_data>"}],
      "max_tokens": 2000, "stream": false}
     ```
   - The payload is `{"project": {approximate_location, goals, scope, scope_other, budget_homeowner_estimate, timing, [opt-in notes]},
     "internal_review": {...}, "candidate_businesses": [only the selected prospects]}`.
   - The check confirmed the body keys are exactly `max_tokens, messages, model, stream`.
2. **Web search: NOT explicitly disabled. UNSAFE/UNCERTAIN.**
   - The only measure is one prompt line ("You have no tools, browsing or code execution").
   - The request sends no parameter that turns off search. Nothing checks the reply for signs of search
     (citations or annotations), and `finish_reason` is ignored.
   - Some Poe models may search on the provider's side, which could send query text derived from project data to a search service.
     Whether the chosen model does is unknown, because no model is chosen and the docs weren't consulted for this.
3. **Tools: none supplied, and none can run here.** There is no `tools` key.
   - The app reads only `choices[0].message.content`. If that isn't a string (for example a tool-call-only reply),
     the reply is rejected as malformed and nothing is saved.
   - No code path runs anything the model asks for. Provider-side capabilities (finding A) are outside the app's control.
4. **JSON output: requested vs. enforced.**
   - **Asked only:** the system prompt asks for one JSON object in a fixed shape, no invention, data treated as untrusted,
     only the given IDs, and insufficient_evidence allowed.
   - **Not sent:** `response_format`. Poe's docs say it is ignored, so the provider enforces no JSON at all.
   - **Sent:** `max_tokens` 2000. The provider is expected to honor it, but the app can't verify that.
   - **Enforced by the app (`validate`):**
     - strict `json.loads`, with only one whole-reply code fence tolerated
     - all 5 top-level keys required, `insufficient_evidence` must be a boolean, and the required keys and types per item
     - string length caps (200 to 2000) and list caps (20 items; 20 fits)
     - fit IDs must be among the *selected* IDs: unknown or repeated IDs are dropped with a visible warning
     - any other violation means nothing is saved
   - **Not enforced:** factual accuracy, that the "evidence" actually appears in the data, and non-empty strings.
     Extra keys are silently dropped.
5. **Preview with AI disabled and no key: works (verified on the copy).**
   - It returns the full request body, with model shown as `(model not configured)`, and `confirm_token: None`.
   - `analyze` raises NotReady, and the transport was called 0 times.
   - Over HTTP, `/api/ai/analyze` returns 409 in that state (covered by `test_ai_analysis.py`).
6. **The enable value is exactly `1`.**
   - Leading and trailing whitespace is stripped, so `" 1 "` also enables it.
   - `true`, `TRUE`, `yes`, `on`, `01`, `1.0`, and empty all leave it disabled (verified).
   - Sending also requires `POE_API_KEY` and a valid `HAVENWRIGHT_AI_MODEL`.
7. **The one-time approval is consumed safely.**
   - `analyze` checks `confirmed is True` and readiness, then calls `_PREVIEWS.pop(token)`.
     This happens before the payload is rebuilt, before the fingerprint check, before `analyses.json` is checked, and before any send.
   - Any later failure leaves the token spent (preview again). There are no retries.
   - The server is a single-threaded `HTTPServer`, so duplicate requests are processed one at a time.
     Even in a 20-thread test with one token (a mock transport), exactly 1 send happened and 19 were refused.
     This works because `dict.pop` is atomic in CPython.
   - Caveat: if the server ever becomes multi-threaded, the expired-token cleanup loop in `preview()` could race with a `pop`.
     That could raise an error, but it would never cause a double send.

**Findings and proposed smallest fixes (NOT implemented; awaiting user approval):**
- **A. Web search (must resolve before the first live call).**
  1. With the user's approval for one external read, consult Poe's documentation for the chosen model's parameters.
     If it documents a switch that disables search, add it as a fixed field in `request_body()`, so it appears in the preview.
  2. In `call_provider`, reject and don't save replies that carry citations or annotations, or a non-null `tool_calls`.
     This is detection, not prevention.
  3. Until step 1 is done, prefer a model the user knows has no search capability.
- **B. Truncated replies.** If `finish_reason == "length"`, report "reply cut off by max_tokens" rather than a generic
  "malformed". This is about one line. Reasoning models might use up the 2000 tokens, which spends points while saving nothing.
- **C. Threading caveat** (low priority; only matters if the server is made multi-threaded).
  Use `_PREVIEWS.pop(t, None)` in the cleanup loop.

**Next safe action (as of this inspection):** ask the user to approve fixes A and B.
*Superseded: the user approved them, and A to C are implemented. See section 12.*

---

## 12. Search-off safety fix (2026-10-19, 03:41–03:48; mocked tests only; live AI still disabled)

**Pre-edit checkpoint:** `checkpoint-20261019-034131`. **Post-change checkpoint:** the first one created after 03:48:48 (see section 0).

**Research (no project data, key, or inference sent):**
- Read Poe's OpenAI-compatible page, the List models reference, the Client SDKs page, and the API bots overview.
- Fetched the public catalog `GET https://api.poe.com/v1/models` without auth: 03:42:36, 336 models, sha256 prefix `3ab10c1d567f4eee`.
  The copy is saved outside the project, in the session scratchpad `poe_catalog\models.json`.
- Found 24 different search-related parameter names across models, with different defaults. Many are on by default.
- **Documentation insufficient:**
  - The OpenAI-compatible page says to pass custom bot parameters via `extra_body`.
  - The Client SDKs page says the OpenAI-compatible API has "No custom parameter support".
  - No page documents the raw HTTP placement.
  - **So every model is BLOCKED.**

**Reviewed configuration** (`ai_analysis.REVIEWED_MODELS`, exact IDs, all `"status": "blocked"`):

| Model | Search-off fields (top level of the JSON body) | Catalog default |
|---|---|---|
| claude-sonnet-4.6 | `"web_search": false` | true |
| claude-opus-4.8 | `"web_search": false` | true |
| gpt-5.4 | `"web_search": false` | false |
| gpt-5.4-mini | `"web_search": false` | false |
| gemini-3.1-pro | `"web_search": false` | false |

- Excluded: `assistant` (auto-routing) and `o1-pro` (it has web search with no off parameter). All other models are unreviewed and blocked.
- Model IDs must match exactly, so a case variant like `Claude-Sonnet-4.6` is blocked.

**Code changes:**
- `ai_analysis.py`:
  - `REVIEWED_MODELS`, `EXCLUDED_MODELS`, and the `config()` model checks.
  - `request_body(payload, cfg)` merges the search-off fields.
  - The preview token binds `request_fingerprint`, the hash of the full body.
  - `_PREVIEWS_LOCK` guards issue, cleanup, and consume.
  - `call_provider` rejects tool calls and search/citation metadata, checks `finish_reason` before parsing,
    and returns `(content, usage, finish)`.
  - `analyze` compares the full-body fingerprint and stores `search_off` and `request_fingerprint`.
- `dashboard.html`: the preview shows the search-off fields, the review status, and the approval scope.
  The analysis card shows the fields used.
- `test_ai_analysis.py`: uses a test-only approved fixture model, and expects `web_search: false` in the body and `finish_reason: "stop"` in replies.
- `test_ai_safety.py`: **new**.

**Concurrency, as documented:**
- The supported configuration is the single-threaded `HTTPServer` in one process, which handles requests one at a time.
  The lock also makes token consumption atomic if threads are ever added.
  A 20-thread test sent once and refused 19.
- **Remaining limits:**
  - Tokens are per process and in memory, so a restart voids them.
  - Two separately approved previews can each send once, by design.
  - A second server process would have its own token store. Only one can bind port 5000.

**Limits of the response checks:** they catch only tool use or search that the reply *reports*.
They cannot prove that the provider did no search internally.

**Tests (mocked; network blocked; temporary data):**
- `test_ai_safety.py` PASS. It checks:
  - the search-off field appears in the actual serialized bytes, and the bytes equal the previewed body
  - per-model parameter names (`enable_web_search` for a second fixture)
  - unreviewed, case-variant, excluded, and blocked-real models are blocked, and nothing is sent
  - a changed model, settings, payload, or withdrawn approval each voids the approval, and nothing is sent
  - 7 tool and search metadata shapes are rejected, while empty metadata is accepted
  - `length` (including valid JSON) gives a "truncated" error with no retry, `content_filter` is rejected,
    a missing finish_reason gives a warning, and `MAX_TOKENS` is unchanged at 2000
  - 20 concurrent sends give 1
  - production files are unchanged
- Mutation check: removing the search-off field or the metadata check makes it fail.
- `test_ai_analysis.py` PASS (updated).
- Full suite on a fresh copy: all 9 scripts exit 0. (`test_marketing.py` showed -1 only because the pipe was truncated; rerun alone, it exits 0.)
  `node --check` passes, 16 root `.py` files compile, and the production data files are byte-identical to the pre-edit checkpoint.

**No live AI call was made.** No key exists on this machine. The only external requests were documentation pages
and the public model catalog (no auth, no body).

**User browser check (recorded 12:02):** the disabled preview works with no model set (no Send button, `model: "(model not configured)"`,
no `web_search` field). That does not exercise the search-off lines.

**Browser checks still needed:**
- the new preview lines (search-off fields, review status, approval scope), with a reviewed model name set and AI still disabled
- "AI not configured", which now also lists the model review problem when a model is set
- the analysis card's "sent with" line (only shows after a send, so it can't be checked yet)

**Next safe action:** the user decides how to resolve the documentation conflict, for example by asking Poe
whether `web_search: false` in a Chat Completions body is honored. Only then, with explicit approval, change one entry to `"approved"`
and authorize one live DEMO analysis.

---

## 13. Draft-only marketing workflow (2026-10-19, after 12:04; local templates only)

**Pre-edit checkpoint:** `checkpoint-20261019-120418`. **Post-change:** see section 0.

**Agent inventory (from the code, not the dashboard labels):**

| Agent | Entry point | In → out | Classification | Credentials / external / cost | Tests |
|---|---|---|---|---|---|
| Lead Engine | `src\lead_engine.py` `LeadEngine.find_match`; `POST /api/run/lead` | service + ZIP → first demo contractor with exact match | Functional on **sample data only** (`data\contractors.json`); `generate_pitch` unused by the app | none | `test_engine.py` (prints only, always exits 0), `test_dashboard.py` |
| Marketing Agent | `src\marketing_agent.py`; `POST /api/run/marketing` | service + theme → headline/body/CTA + caption | Functional, **fixed templates**; output not saved | none | `test_marketing.py` (prints only), `test_dashboard.py` |
| Trend Engine | `src\trend_engine.py`; `POST /api/run/trend` | service → keywords | **Partial**: 2 hand-entered entries, else 4 hard-coded defaults; `save_trend` not wired (non-atomic write if ever used) | none | `test_dashboard.py` |
| Overlord | `src\overlord.py`; `/api/run/overlord`, `/api/run/diagnostic` | service + ZIP → match + trend + ad | Functional **chain on sample data**; runs once per click; not a scheduler | none | `test_dashboard.py` |
| Campaign workflow (new) | `campaigns.py`; `/api/campaigns/*` | operator brief → template drafts + flags → checklist review | **Functional, local, draft-only** | none | `test_campaigns.py` |
| AI analysis | `ai_analysis.py`; `/api/ai/*` | brief + selected prospects → structured suggestions | **Blocked** (every model) | Poe key + model + enable flag; paid points | `test_ai_analysis.py`, `test_ai_safety.py` |
| `auto_gen.py` (dev script, not an agent) | CLI | instruction → writes `src\<module>.py` | Not wired to the app; needs the `anthropic` package and `ANTHROPIC_API_KEY`; old model id; **overwrites source files** | paid API | none. Left untouched; do not run |
| `run_agent.py` (dev script) | CLI | pasted text → writes `src\<file>` | Manual helper; overwrites files | none | none |

No scheduler: no project task in Windows Task Scheduler; nothing runs in the background.

**Audience decision:** the project did not define a campaign audience. So the workflow **requires the operator to pick one audience
per campaign** (contractors or homeowners; never defaulted, never both) and supply the offer, CTA, sender and supported claims.
No campaign record was created by the agent; `data\campaigns.json` does not exist until the user saves one.

**What was built:**
- `campaigns.py`: brief (name, audience, who, area, objective, offer, CTA, sender, supported claims, notes) → `generate` fills fixed
  templates (social post, email subject/body, flyer) using only those fields (objective and notes stay internal) → automated
  keyword flags (pricing, superlatives, credentials, testimonials, partnership/availability, other-audience wording, provisional brand,
  no claims) → `review`: approve only with all 6 checklist items ticked; request changes needs a note.
  States: `brief` → `in_review` → `approved` / `changes_requested`. Editing the brief discards drafts and approval.
  Duplicate-run protection: generate is refused unless the status is `brief`. Contact details refused. Atomic writes, pre-write backups
  in `data\campaign_backups`, malformed file never overwritten. No delete.
- `app.py`: 4 entries in `RECORD_ROUTES` (reuses `save_record`: Activity logs only the id), `campaigns` in `/api/state`, 2 paths.
- `dashboard.html`: Marketing page campaign workflow (review queue count, AI drafting BLOCKED line, task tags, copy buttons only after
  approval); Agents page "What each agent really is" table. The old quick test draft remains below.
- No runner was introduced (generation is one synchronous, bounded call), so there is no stop/pause control to add.

**Tests:** `test_campaigns.py` PASS (temp data; `urlopen` and `socket.create_connection` blocked). Mutation check: removing the
duplicate guard, the audience requirement, the checklist gate or the reset-on-edit each makes it fail. Full suite on a fresh copy:
all 10 scripts exit 0 (`test_dashboard.py` against the copy on port 5055); `node --check` passes. Production data byte-identical to 120418.

**Not browser-verified.** Restart the server (it was started before this code). Browser test: Marketing → New campaign brief.

**Later activation would need:** an audience + offer decision, cleared brand/sender name, evidence for each claim, a publishing channel
and account (user-connected), and, for AI drafting, the Poe search-off question resolved plus explicit approval.

---

## 14. Research workflow (2026-10-19, after 16:17; LOCAL sources only; no external run made)

**Pre-edit checkpoint:** `checkpoint-20261019-161739`. **Post-change:** see section 0.

**Agent inventory (re-checked from code):**

| Agent | Classification | Reason / evidence |
|---|---|---|
| Lead Engine | Working and tested **on sample data only** | Exact service+ZIP match over `data\contractors.json` (demo). Not a research tool. `test_engine.py` prints only (cannot fail); `test_dashboard.py` asserts the route |
| Marketing Agent | Working and tested (fixed templates) | `test_dashboard.py`; `test_marketing.py` prints only |
| Trend Engine | Partially implemented | 2 hand-entered keywords + 4 defaults; `save_trend` unwired; no data source |
| Overlord | Working and tested on sample data | chains the three above once per click |
| Campaign workflow | Working and tested locally (templates) | `test_campaigns.py` |
| **Research runs** (new) | **Working and tested on LOCAL TEST DATA**; also run end-to-end over HTTP on a *copy* of the real prospects (3 scanned, 3 saved, every claim "unknown", because the records hold only names/sites) | `test_research.py` |
| Research source `wa_lni_contractors` | **Blocked**: proposed only, adapter not written, no external run approved | shown as BLOCKED in the source list |
| AI analysis | Blocked: every model blocked (Poe search-off documentation conflict) | `test_ai_*.py` mocked |
| `auto_gen.py` / `run_agent.py` | Dev scripts, not agents; `auto_gen.py` needs a paid Anthropic key and overwrites `src` | untouched |
| Scheduler | None. No project task in Task Scheduler; nothing runs unattended | |

**Integrations:** local records: `prospects.json`, `contractors.json` (sample), `projects.json`, `campaigns.json`, `research.json`.
Public external databases: **none connected**. Authenticated/paid: Poe (`ai_analysis.py`, blocked, no key on machine) and
Anthropic (`auto_gen.py`, unused, no key). No credential values were read or displayed.

**What was built (`research.py`, `data\research.json`, backups in `data\research_backups`):**
- Criteria: source, keyword, area, max results (1–25). Contact details refused in criteria.
- Retrieve (local source, one retry of a transient `OSError` only; malformed data fails without retry) → normalize into bounded text
  fields (no `public_contact`, no notes copied) → deduplicate (website host+path, else normalized name; within the run and against
  earlier runs of the same source; earlier hits listed as "already found") → save findings with source, retrieval time, criteria,
  source record id, record source URL/date ("unknown" if none) and per-claim evidence (value, basis, status).
- Human review per finding: pending / relevant / not relevant / needs more evidence + note. **Never writes `prospects.json`.**
- Controls: Run once, Stop (honoured between records), states running/completed/stopped/failed/blocked (+ "interrupted" if the
  server stopped mid-run), one run at a time (duplicate-run protection), limits 25 saved / 500 scanned / 30 s / 2 attempts.
  The run executes in one background worker thread; the HTTP server stays single-threaded. Activity gets run id, status and
  error text only.
- Dashboard: Contractors → **Research** tab; Agents table row added.

**Tests (LOCAL TEST DATA):** `test_research.py` uses temp files, fixture sources and blocked network. Mutation check: disabling
in-run dedup, cross-run dedup, Stop, the one-run guard, the retry bound or the blocked-source guard each makes it fail.
Full suite on a fresh copy: 11 scripts exit 0; `node --check` passes; production data byte-identical to 161739.
**No live-source verification exists**: no external source has ever been queried.

**Proposed first external run (NOT approved, NOT run, adapter NOT written):**
- Source: Washington State Department of Labor & Industries contractor registration data, published as open data on data.wa.gov
  (Socrata API). The exact dataset ID and field names were **not looked up** (no external requests this milestone); confirming
  them from the dataset's public metadata would be request 1.
- Geography: business city = Lacey, WA.
- Query: registered contractors in Lacey; select only business name, registration/UBI number, registration type/specialty,
  status, expiration date and city. **Not** phone, street address or principal/owner names.
- Data sent: the query parameters only (city, field list, limit). No project, prospect or homeowner data; no key or account.
- Access: public open-data API, anonymous (rate-limited); no scraping of the interactive L&I lookup.
- Maximum: 2 requests (1 metadata, 1 query with limit 50); cost $0.
- Caveat: registration is a licensing record, not evidence of quality or landscaping capability; maintenance-only landscapers may
  not be registered.

---

## 15. WA L&I source connected and live-verified (2026-10-19, 16:40–16:43)

**Approval:** user message "allow all make them operational" after the section 14 proposal. Applied to that bounded run and to keeping
the source available for **manual** runs. Not applied to Poe/paid AI, outreach, publishing or ad spend (still blocked/not built).
**Pre-edit checkpoint:** `checkpoint-20261019-164029`.

**External requests made (the only ones):**
1. 16:40:41 `GET https://api.us.socrata.com/api/catalog/v1?domains=data.wa.gov&q=contractor%20license&limit=10` (public catalog;
   sent only the search words). Confirmed dataset `m8qx-ubtq` "L&I Contractor License Data - General" and its field names.
2. 16:42:27 `GET https://data.wa.gov/resource/m8qx-ubtq.json` with `$select` (11 fields), `$where=upper(city)='LACEY' AND name/specialty
   like '%LANDSCAP%'`, `$order=businessname`, `$limit=50`. No key, no account, $0.

**Live result:** run `research-5c041fb9c387` completed (1 attempt, 0.5 s): 26 rows read, 1 duplicate name, **25 findings saved**
(the run's 25-result limit; rows after "JO'EFFIES INC" alphabetically were not saved, and Lacey may have more than 50 matches).
Statuses as published include ACTIVE, EXPIRED, SUSPENDED and RE-LICENSED. All 25 are review **pending**. `data\research.json` holds no
phone, street address, ZIP or principal-name fields (checked). Nothing was written to `prospects.json`.

**Code:** `research.py` adds `http_get` (size cap 1 MB, 20 s socket timeout), `lni_query` (city required; city/keyword limited to
letters, numbers, space, & . ' -; quotes escaped), `_fetch_lni`, `_from_lni` (each claim "as published by L&I; not independently
verified"; capability/quality always "unknown"). The L&I source is limited to **1 attempt (no retry) = 1 request per run**.
`fetch` now receives the criteria. Tests: `test_research.py` covers the adapter OFFLINE with a fake transport (excluded fields
ignored, query shape, HTTP 429 without retry, non-JSON reply, unsafe input refused before sending).

**Operational now:** each "Run once" on this source sends one free request. Nothing is scheduled. Limitations: no pagination past 50
rows; city match is exact on the registered business address city (businesses serving Lacey from elsewhere are missed); dedup is by
name (no website in this data); findings are not linked to existing prospects automatically.

---

## 16. n8n integration contract + Agent Library (2026-10-20, after 20:59; MOCKED n8n only; no external requests)

**Discovery (read-only):**
- **n8n: not installed.** `Get-Command n8n` found nothing. There is no global npm package (only `@anthropic-ai/claude-code`)
  and no `~/.n8n` folder, nothing listens on port 5678, there is no Docker, and `wsl -l` reports WSL not installed. Node is
  v24.19.0.
- **Claude subagents: none installed.** Neither `~/.claude/agents` nor `C:\generational_run\.claude\agents` exists.
- **Agency repo:** `C:\Users\relli\Downloads\agency-agents-main\agency-agents-main`, extracted from
  `Downloads\agency-agents-main.zip`. It is MIT licensed ("AgentLand Contributors") and has no `.git` folder.
  - 282 definitions in 18 divisions.
  - 17 declare tools; 4 declare services, including Xquik, which is paid.
  - No installer and none of its scripts were run, and nothing was copied into any Claude folder.

**Built:** `n8n.py`, `catalog.py`, `workflows/research_lni.json`, research source `wa_lni_via_n8n`, `app.py` routes
(`GET /api/catalog`, `POST /api/n8n/health`, `POST /api/research/reconcile`), dashboard Workflows and Agent Library pages,
`test_n8n.py`, and three docs: `docs/ADR-001-n8n-integration.md`, `docs/IMPLEMENTATION_CHECKLIST.md`, `docs/AGENT_ROSTER.md`.
- **Small fix:** a run's recorded `limits.max_attempts` now shows the source's real value (1 for L&I) instead of the global 2.

**Catalog import:** `python catalog.py <repo>` ran once and wrote `data/agent_catalog.json` (282 entries). The categories are:
- 11 workflow_reference
- 5 build_reference
- 266 catalog_only

All 282 are not installed, not connected, not tested and never executed.

**Tests (fresh copy):** all 12 `test_*.py` scripts pass, plus `test_dashboard.py` against a copy server on :5055.
- `node --check` passes and every Python file compiles.
- `test_n8n.py` uses a **fake n8n** on 127.0.0.1 and fails on any other connection. It covers:
  - Disconnected, bad URL and missing-secret cases are blocked and send nothing.
  - Health check.
  - End to end: route, webhook, saved findings, review.
  - Dedup, a duplicate run while one is in flight, and Stop.
  - Bad responses, each failing with 1 request and no retry: wrong correlation id, missing execution id, non-JSON, HTTP 500,
    a refused redirect, a timeout, and a wrong secret (403).
  - Unsafe input refused before anything is sent.
  - Reconciliation: no key gives 400, a wrong key gives 502, and a bad id is refused.
  - Secret values absent from state, data and Activity.
  - The export's contract matches the code.
  - The catalog built from the real repo, read-only (hashes are unchanged afterwards).
- **Mutations detected:**
  - The correlation check removed.
  - The local-host check removed.
  - The no-redirect handler removed.
  - The secret requirement removed.
  - The row filtering removed.
- **Copy server (`/api/state`):** the n8n source shows the BLOCKED reason. The health check answers "N8N_BASE_URL is not set",
  and a run is recorded as blocked.

**Not done / blocked:**
- No real n8n execution exists.
- Workflows B to E are specified only.
- Nothing has been browser-checked.

**Minimal setup decision needed:** approve installing n8n locally (for example `npm install -g n8n`, bound to 127.0.0.1),
or name another existing n8n instance. Without it, workflow A stays BLOCKED.

---

## 17. Real local n8n installed + first real diagnostic (2026-10-20, 21:14–21:30)

**Approval:** the user approved installing pinned n8n 2.44.4 in C:\n8n_local, including the downloads and package install scripts.
- Not approved: external research, Workflow A runs, schedules, paid services.
- Pre-install checkpoint: `checkpoint-20261020-211456`.

**Install**
- Command: `npm install --prefix C:\n8n_local n8n@2.44.4`. Exit 0, 2342 packages, about 6 minutes.
- Requirements: the package needs Node `>=24.0.0`, and the installed Node is v24.19.0.
- `n8n --version` reports 2.44.4.
- No global install, PATH, service, firewall or tunnel changes.

**Startup incident (fixed)**
- The first two starts bound to `::`, which means all interfaces, and used `%USERPROFILE%\.n8n`.
- Cause: the npm `.cmd` shim runs ENDLOCAL, which dropped the launch script's `set` variables.
- Each time it was stopped within about a minute. Pre-existing Windows firewall rules block node.exe inbound on the Public profile;
  other profiles were not checked.
- Fix: `start_n8n.cmd` and `n8n_cli.cmd` now call `node ...\n8n\bin\n8n` directly.
- Verified afterwards: `Get-NetTCPConnection` shows 127.0.0.1:5678 and 127.0.0.1:5679 only.

**Data folders and keys**
- The first start's data and key were moved, unchanged and together, to `C:\n8n_local\data\.n8n`. That is the store in use, and no
  key was regenerated afterwards.
- The second bad start created another `%USERPROFILE%\.n8n` with its own key and no user data. It is **left in place** and needs the
  user's decision before it is deleted.

**Configuration (no secret values in any file listed here)**
- `C:\n8n_local\start_n8n.cmd` and `n8n_cli.cmd` set: listen address 127.0.0.1, port 5678, user folder `C:\n8n_local\data`,
  telemetry, version notifications and templates off.
- `C:\n8n_local\README.txt` explains how to back up and restore the database and the key together.
- `C:\generational_run\start_havenwright.cmd` reads secrets from `C:\n8n_local\secrets` (outside the project, access restricted to the
  user) and starts app.py.
- Webhook secret:
  - Generated locally and never printed.
  - Imported as credential `HvnwrightToken01` (Header Auth) through the CLI; the temporary import file was deleted.
  - An export check confirmed it is stored encrypted.

**n8n workflows**
- Imported through the CLI:
  - `1HB6dkX12OiJWNME` "Havenwright diagnostic - echo (v1)": **published/active**.
  - `kJ0i1ANzv0YWzUAj` "Havenwright A - research L&I (v1)": **inactive, never run**.
- Wrong token and missing token both get HTTP 403.

**Real diagnostic** (Havenwright code path `app.n8n_request`, from a script process; correlation id and timestamp only)
- `diag-67a9a8fc040d` sent at 21:25:34. n8n replied with execution **1**, and the echo matched.
- A repeat with the same request_id returned the saved record and sent nothing.
- n8n's own execution record, read **read-only from its SQLite database, not through the API**: execution 1, workflow
  1HB6dkX12OiJWNME, status `success`, finished, mode webhook, 04:25:34.499 to 04:25:34.567 UTC.
- The saved Havenwright record has status `replied`, because the API check is UNVERIFIED: no API key exists until the user creates
  the owner account.
- Saved in `data/n8n_diagnostics.json`, kept apart from research. research.json was unchanged.

**Code**
- `n8n.py`: `run_diagnostic` (request-id idempotency, one diagnostic at a time, the record saved before sending), `readiness()` with
  five separate states, `find_workflow`, `check_enabled`, and polling of the execution status.
- `app.py`: `POST /api/n8n/diagnostic`.
- Dashboard: the readiness states, a diagnostic table, and the Run diagnostic button.
- `workflows/diagnostic_echo.json`.
- Tests: `test_n8n.py` adds mocked diagnostic, duplicate, concurrent-diagnostic and concurrent review-write tests. All 12 test scripts
  and test_dashboard pass on a fresh copy.

**Next**
1. The user creates the owner account at http://127.0.0.1:5678.
2. The user creates an API key and saves it in `C:\n8n_local\secrets\api_key.txt`.
3. Restart Havenwright with `start_havenwright.cmd`, then use Workflows → Run diagnostic, which verifies the execution through the API.

---

## 18. Havenwright HQ admin, first slice (2026-10-20, 22:08–22:20)

- **Pre-change checkpoint:** `checkpoint-20261020-220854`.
- **Post-change checkpoint:** the first `checkpoint-*` folder created after this section was written.

**Baseline before any edits**
- Port 5000 was serving the current code. The process started at 21:34 with `python app.py`.
- n8n was listening on 127.0.0.1 only.
- `api_key.txt` existed.

**n8n API verification: DONE.** Real diagnostic `diag-461b868b5c6c` (22:16:55, run through the Havenwright code path from a script)
was verified through the n8n API.
- n8n execution **2**, workflow `1HB6dkX12OiJWNME`.
- Status `success`, finished, 05:16:55.178–05:16:55.249 UTC.
- A repeat with the same request_id was deduplicated.
- All 5 readiness states read "yes".
- No external requests were made.

**Stack (reused, no new packages):** stdlib `app.py`, plain HTML/JS, and JSON written through `store.py`.
- `/` is still the operator console. **`/hq` is the new admin interface.**

**Built**
- `hq.py`: collections, each stored in its own file in `data/hq/`:
  - organizations (contractor or agency)
  - users
  - memberships (owner, admin, staff or viewer)
  - offerings (`price` and `internal_cost` kept separate; `public_offering()` excludes cost)
  - leads (homeowner_inquiry or contractor_recruitment)
  - projects (installation or agency)
- Preferences are stored separately in `data/hq_preferences.json`.
- The rules are listed in `docs/ACCESS_CONTROL.md`.
- `app.py` additions:
  - `GET /hq`
  - `GET /api/hq/state?org=` (the company switcher's scope is applied on the server)
  - `POST /api/hq/add`, `/api/hq/update`, `/api/hq/preferences`, logged to Activity by record id only
- `hq.html` sections:
  - Overview, Companies (with company detail), Leads, Projects and Catalog are working.
  - Marketing shows real campaign counts and a link to the existing workflow. The HQ campaign planner is marked "Coming later".
  - Automations shows the real readiness states and a Run diagnostic button.
  - Settings has appearance, access records (marked "Sign-in not configured") and data locations.
- The operator console links to `/hq`.

**Tests**
- **Automatic:** `test_hq.py` runs on test fixtures in temporary folders. It covers:
  - The full workflow and switcher scope.
  - Relationship rules and useful error messages.
  - Users and memberships.
  - Preferences kept separate.
  - Persistence, and an Activity log that holds ids only.
  - A malformed file is never overwritten.
  - Production files are unchanged.
- All 13 test scripts pass on a fresh copy, and `node --check` passes on the HQ script.
- **On a copy server (port 5055), over HTTP, with TEST FIXTURE records:**
  - The workflow ran end to end.
  - A company mismatch was refused with HTTP 400.
  - **The records persisted after the copy server was restarted.**
- **Screenshots** (headless Edge, copy server) are in `docs/screenshots/hq-2026-10-20/`. A layout bug at 390 px was found, fixed and
  shot again.
- **Manual testing by the user:** none yet.
- **Unverified:** keyboard-only navigation and screen readers have not been checked in a real browser.

**Production data:** `data/hq/` does not exist yet. No HQ records were created in the live project.

---

## 19. HQ dashboard redesign + Market Map (2026-10-20, 23:18 to about 23:50)

- **Pre-change checkpoint:** `checkpoint-20261020-231857`.
- **Post-change checkpoint:** the first checkpoint created after this section was written.

**Baseline**
- Port 5000 is running code from 21:34, older than the HQ files.
- Live `data/hq` does not exist: there are no HQ records and no preferences.
- The Design Studio (5077) and n8n (5678) were not touched.

**Built**
- Purple dashboard shell.
- Customizable Overview.
- Market Map with Leaflet 1.9.4 (served locally) and an OpenStreetMap basemap that can be switched off.
- Census population and density, using ACS 5-year 2020-2024 table B01003 from the summary file. The Census API now
  needs a key, so it was not used.
- TIGERweb ACS2024 tract boundaries for Thurston County (62 tracts, total 299,067).
- Derived customers.
- Manual locations.
- Territories and notes.
- Server-side company scope on reads and writes.
- Origin and Sec-Fetch-Site checks.
- Content-Security-Policy (CSP).

Details: `docs/HQ_MARKET_MAP.md`.

**External requests made (public data only):**
1. TIGERweb MapServer metadata.
2. Two Census Data API probes. These returned "Missing Key" and no data was used.
3. The ACS summary file `acsdt5y2024-b01003.dat` (about 18 MB, streamed; only Thurston tract rows kept).
4. Two TIGERweb queries.
5. OSM tile policy page.
6. `npm pack leaflet@1.9.4`.

No business data was sent anywhere.

**Tests (fresh copies)**
- All 12 Python test scripts pass, including the new `test_hq_map.py` and the updated `test_hq.py`.
- `test_dashboard.py` passes.
- `tests/hq_browser_test.mjs` passes 42 of 42 checks. It runs real headless Edge on an isolated copy with TEST FIXTURE
  records, and OSM tiles are blocked.
- Screenshots are in `docs/screenshots/hq-map-2026-10-20/`. All are from copies; the populated ones use labelled
  fixtures. The empty state matches live, which has no HQ records.
- Live business data was unchanged (hash check against the pre-change checkpoint).

**Not done**
- Screen-reader pass.
- A browser review by the user.
- The live server still needs a restart to serve the new code.
