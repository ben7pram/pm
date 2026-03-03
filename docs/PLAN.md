# High level steps for project

> This document is the master checklist; each Part should be broken into concrete sub‑tasks, with associated tests and success criteria. The agent will update these sections as work proceeds and seek approval from the user before moving on.

## Part 1: Plan ✅
- [ ] Read and understand the business requirements in `AGENTS.md`.
- [ ] Review existing frontend code and tests.
- [ ] Write `frontend/AGENTS.md` summarizing current architecture, key components, and testing tools.
- [ ] Expand each subsequent part below into detailed sub‑steps, including:
  - Implementation tasks
  - Required tests (unit, integration, e2e)
  - Success criteria (observable outcomes or verification steps).
- [ ] Present the expanded plan to the user and obtain explicit approval before proceeding with Part 2.

**Tests / Success criteria for Part 1:**
- The expanded plan document exists with checklists for all parts.
- `frontend/AGENTS.md` has been created and accurately describes the current frontend state.
- User confirms the plan is acceptable (via a message in the conversation).

## Part 2: Scaffolding ⚙️
- [x] Initialize `backend/` directory with a FastAPI project.
- [x] Add minimal `main.py` returning JSON on `/api/hello` and serve static files at `/`.
- [x] Create Dockerfile and optionally `docker-compose.yaml` for single container.
- [x] Add start/stop scripts in `scripts/` for Mac, Windows, Linux.
- [x] Confirm container builds and runs; hitting `http://localhost:8000` returns sample HTML, `/api/hello` returns JSON.
- [x] Add basic backend tests verifying the `/api/hello` endpoint.

**Tests / Success criteria:** container builds and serves endpoints, tests pass.  ✅ All checks completed.

## Part 3: Add in Frontend 💻
- [x] Update NextJS `package.json` and build settings to produce static output.
- [x] Modify backend to serve the built frontend from `frontend/.next` (or `out`).
- [x] Ensure when running locally via Docker, the Kanban board demo loads at `/`.
- [x] Add tests to verify the static build is present and served (unit/integration).

**Tests / Success criteria:** rebuilding the project results in a working Kanban board in the container; automated tests exercise static serving. ✅ All checks completed.

## Part 4: Fake user sign‑in 🔐
- [ ] Implement frontend login page with hard‑coded credentials (`user`/`password`).
- [ ] Add backend session handling or simple cookie check.
- [ ] Redirect to login if unauthenticated and allow logout.
- [ ] Write tests covering login flow (Vitest/Playwright for e2e).

**Tests / Success criteria:** user cannot see board until they log in; credentials enforced; logout works.

## Part 5: Database modeling 🗄️
- [ ] Design SQLite schema for users and kanban boards (JSON stored for simplicity).
- [ ] Document schema and reasoning in a new file under `docs/`.
- [ ] Review schema with user and update per feedback.

**Tests / Success criteria:** schema document exists and is approved; migrations or init code can create the database.

## Part 6: Backend APIs 🔌
- [ ] Add endpoints to get/set the kanban for the current user.
- [ ] Ensure database creation if not present.
- [ ] Write backend unit tests for these endpoints and data logic.

**Tests / Success criteria:** API returns/updates data correctly; tests exercise edge cases.

## Part 7: Frontend + Backend integration 🔄
- [ ] Change frontend to fetch board data from the API and post updates (renames, moves, add/remove).
- [ ] Ensure state remains consistent; handle loading and error states.
- [ ] Add integration tests simulating user actions with real API (could run container in test mode).

**Tests / Success criteria:** persistent board state across page reloads; actions reflect in DB.

## Part 8: AI connectivity 🤖
- [ ] Add server-side code to call OpenRouter using `OPENROUTER_API_KEY`.
- [ ] Create a test endpoint that sends prompt "2+2" and returns AI reply.
- [ ] Write tests verifying the call succeeds and response is sensible.

**Tests / Success criteria:** backend can communicate with OpenRouter, tests mock or hit real API.

## Part 9: Kanban‑aware AI call 🧠
- [ ] Extend AI call wrapper to include current board JSON and conversation history.
- [ ] Define structured output schema: `{response: string, update?: {cards?, columns?}}` or similar.
- [ ] Update backend route to parse and return both message and optional board modifications.
- [ ] Add unit tests ensuring parsing and handling works correctly.

**Tests / Success criteria:** backend interprets structured outputs and returns them appropriately.

## Part 10: AI chat sidebar 🎨
- [ ] Design and implement a sidebar chat UI component in the frontend.
- [ ] Allow users to send messages; display AI responses.
- [ ] When AI returns kanban updates, apply them to the board and refresh UI automatically.
- [ ] Write end‑to‑end tests verifying full chat flow and board updates.

**Tests / Success criteria:** chat works, AI messages appear, and board updates happen when AI suggests changes.

---

Once Part 1 is approved, the agent will start executing the checklist sequentially, marking items off as they are completed.