# Frontend AGENTS

This document describes the current state of the frontend workspace as of the MVP demo.

## Structure

- **Next.js 13** app using the `app/` directory (no `pages/`).
- Styled with Tailwind CSS; global styles in `src/app/globals.css`.
- Uses TypeScript with strict types where practical.
- Testing setup:
  - **Vitest** for unit/component tests (configuration in `vitest.config.ts`).
  - **@testing-library/react** and `user-event` for DOM interaction tests.
  - Playwright configuration present (`playwright.config.ts`) for future e2e tests.

## Key components

- `KanbanBoard.tsx` – top‑level client component that holds board state, DnD context, and orchestrates column/card actions.
- `KanbanColumn.tsx` – renders a column, its cards, rename input, add‑card form, and handles deletion.
- `KanbanCard.tsx` & `KanbanCardPreview.tsx` – card display and drag preview.
- `NewCardForm.tsx` – form used within a column to add a card.

## Utilities

- `src/lib/kanban.ts` contains the data model types (`Card`, `Column`, `BoardData`), the `initialData` fixture, and helper functions (`moveCard`, `createId`).
- Associated unit tests exercise the drag logic.

## Tests

- Component tests in `src/components/KanbanBoard.test.tsx` cover rendering of columns, renaming, adding/removing cards.
- Unit tests in `src/lib/kanban.test.ts` verify card movement logic.
- Test helpers and Vitest setup live in `src/test/`.

## Running the frontend

- `npm install` (or `pnpm` depending on chosen package manager) sets up deps.
- `npm run dev` starts the front‑end on port 3000; board loads immediately at `/`.
- Build outputs are created under `.next`.

## Notes

- The current code is entirely client‑side with no backend integration – the board data lives in component state and resets on reload.
- Drag‑and‑drop is implemented with `@dnd-kit/core`.
- No authentication, API calls, or server components are present yet.

This file should be updated whenever the frontend architecture or major components change.
