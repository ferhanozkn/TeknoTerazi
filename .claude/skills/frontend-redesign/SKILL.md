---
name: frontend-redesign
description: Orchestration guide for TeknoTerazi's experimental migration off Django templates onto a React/Next.js frontend. Sequences the frontend-design, ui-ux-pro-max, and web-design-guidelines skills. Branch-scoped — do not apply on main.
---

# TeknoTerazi Frontend Redesign (experimental)

## Scope and status

This skill only applies on the `experiment/react-frontend-redesign` branch. `main` still follows `docs/PROJE_PLANI.md` rule #5 and `CLAUDE.md`'s "Stack and hard constraints": Django templates + vanilla HTML/CSS/JS, no separate frontend framework. This branch exists to test whether replacing that with React/Next.js is worth doing — see Karar Günlüğü #30 in `docs/PROJE_PLANI.md` for why and what was installed.

Do not port this decision back to `main` (rule #5, CLAUDE.md) until the experiment is reviewed and explicitly accepted by the user.

## What must not change, even on this branch

- **Language rule still applies**: all user-facing text (labels, errors, empty states) stays in **Turkish**; all code/component/file names and comments stay in **English**.
- The product domain is unchanged: polls (`Poll`) with 2–5 products (`Product`), member + anonymous voting, owner-only close/delete. Read `docs/PROJE_PLANI.md` sections on the data model and the voting endpoint contract before designing any screen — don't invent fields or flows that aren't there.
- The existing design system tokens in `static/css/main.css` (colors, spacing, type scale already validated in Faz 6) are the starting brand reference, not a blank slate — ground new design decisions in what already exists unless there's a specific reason to change it.
- Django remains the backend. This experiment is about the *rendering layer*; it does not by itself decide whether Django starts serving JSON from DRF-style endpoints, stays template-based with an API layer bolted on, or something else — that's still open and should be logged in the Karar Günlüğü when decided, not silently assumed.

## Installed skills and when to use each

Three skills are installed under `.claude/skills/` for this effort:

1. **`ui-ux-pro-max`** — use first, to establish or confirm the design system (palette, type pairing, spacing scale) for the new frontend. Ground its output in the poll/voting domain and the existing brand reference above, not a generic default.
2. **`frontend-design`** — use second, per screen/component, for the actual visual composition and self-critique pass (hero treatment, typography, restraint). Follow its plan → review-against-brief → build → critique process.
3. **`web-design-guidelines`** — use last, as a gate before calling any page/component done. It fetches Vercel's Web Interface Guidelines live and checks the produced code against ~100 accessibility/UX rules (ARIA, focus states, keyboard nav, WCAG). Don't skip this step just because the visual pass looked good.

React-specific Vercel skills (React Best Practices, Composition Patterns, React Native) were deliberately **not** installed yet — there's no React code to apply them to until this experiment actually starts producing components. Install them at that point rather than now.

## Workflow for a new screen

1. Confirm the screen's real data and business rules against `docs/PROJE_PLANI.md` (URL map, form validation, voting contract).
2. Run the `ui-ux-pro-max` design-system step if the token set isn't settled yet for this screen's context.
3. Build the screen using the `frontend-design` process.
4. Audit with `web-design-guidelines` and fix findings before moving on.
5. If any decision isn't covered by the plan (e.g., API shape, auth flow under React), apply the simplest solution and log it in `docs/PROJE_PLANI.md`'s Karar Günlüğü — same rule as the rest of the project, not just a code comment.
