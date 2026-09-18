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

## Current architecture (resolved — see Karar Günlüğü #31)

- **No DRF.** `polls/api.py` + `polls/api_urls.py` (mounted at `/api/` in `config/urls.py`) are plain `JsonResponse` views that call the exact same functions `views.py` uses (`get_poll_with_stats`, `get_trending_polls`, `cast_vote`, `get_voter`/`attach_voter_cookie`, etc.). Keep it that way — never duplicate business logic into `api.py`; import and reuse from `services.py`/`voter.py`.
- **Proxy, not CORS.** `frontend/next.config.ts` rewrites `/api/:path*` to Django (`BACKEND_URL`, default `http://127.0.0.1:8000`) so the browser only ever talks to the Next.js origin — this is what makes the anon voter cookie (`tt_voter`) and Django's `csrftoken` work with zero CORS/`SameSite` configuration. Server Components fetch Django directly (`frontend/src/lib/api.ts`, forwarding the incoming request's cookies via `next/headers`); the vote button is a Client Component that calls the relative `/api/...` path (`frontend/src/lib/vote-client.ts`) so the real browser cookie jar is used.
- The rewrite destination has `/` appended manually after `:path*` — Next's route-segment reconstruction drops the trailing slash Django's URLconf requires, which otherwise causes an infinite `APPEND_SLASH` redirect loop. `skipTrailingSlashRedirect: true` is also required, or Next's own slash redirect fires before the rewrite ever runs.

## Two silent-failure environment gotchas (don't relearn these)

Both of these break voting/interactivity with **no error in the browser console** — the only symptom is "nothing happens when I click."

1. **Always open the app at `http://localhost:3000`, never `http://127.0.0.1:3000`.** Next's dev server blocks HMR/RSC dev-resource requests from origins other than `localhost` by default (visible only in the `next dev` terminal log as `⚠ Blocked cross-origin request to Next.js dev resource /_next/hmr`), which silently breaks all client-side hydration — every `onClick` becomes a no-op. `allowedDevOrigins: ["127.0.0.1", "localhost"]` is already set in `next.config.ts` as a second line of defense, but prefer `localhost` in the browser regardless. (Curling the Django backend directly via `127.0.0.1:8000` is fine and unrelated — that's only to dodge an unrelated Docker container also listening on `*:8000`.)
2. **`CSRF_TRUSTED_ORIGINS` in `.env`/`.env.example` must include `http://localhost:3000`.** Django's CSRF middleware checks the browser's `Origin` header (sent on every fetch/XHR POST, but never sent by curl — which is why curl-based testing of the vote endpoint can pass while the real browser flow 403s) against this list, not against `request.get_host()`. Without it every vote silently 403s with Django's default HTML CSRF-failure page; since `vote-client.ts` does `res.json()` on the response, this surfaces as a confusing `Unexpected token '<'` error rather than anything CSRF-shaped.

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
