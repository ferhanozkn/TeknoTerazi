# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Source of truth

**`docs/PROJE_PLANI.md` is the single source of truth for this project.** It contains the full technical spec: data model, business rules, URL map, form validation, the voting endpoint contract, the design system, and a 9-phase build plan (Faz 0–9) with checkboxes and per-phase acceptance criteria.

Before doing any work:
1. Read `docs/PROJE_PLANI.md`, section "İlerleme Durumu" (progress table), to see which phase is current.
2. Work through that phase's tasks in order; check off `- [ ]` → `- [x]` as you complete them.
3. Do not start a phase's tasks until the previous phase's acceptance criteria are met.
4. If you hit a decision not covered by the plan, apply the simplest solution and log it in the "Açık Sorular / Karar Günlüğü" table at the bottom of the file, not just in code comments.
5. At the end of a phase: run the test suite, verify every acceptance criterion, then make a commit.

The plan is written in Turkish and is authoritative over anything in this file if they ever disagree — update this file to match it, not the other way around.

## Language rule (from the plan, load-bearing)

All **user-facing text** (UI strings, form/validation error messages, emails) must be in **Turkish**. All **code** — variable/function/model/file names, comments — must be in **English**. This split is intentional and applies everywhere, including new templates and error messages.

## Stack and hard constraints

- Python 3.12 (pinned for Vercel compatibility — `.venv` must be created with `python3.12`, not a newer interpreter).
- Django 5.2 (LTS) + `psycopg[binary]` v3 + `dj-database-url` + `python-dotenv` + `whitenoise`. No other dependencies without updating `requirements.txt` and the plan's Bölüm 2.
- **No separate frontend framework.** Django templates + plain HTML/CSS/vanilla JS only — no React/Vue/Tailwind build step/HTMX.
- Database is **Supabase Postgres**, in local dev too — never fall back to SQLite. Some model constraints (partial unique indexes, `CheckConstraint`) are Postgres-specific.
- `AUTH_USER_MODEL = "accounts.CustomUser"` (set in Faz 1, before the first `migrate` — Django cannot swap the user model after tables exist). Any custom user model field needing a Turkish label needs an explicit `verbose_name` — it does not inherit one from Django's translation catalog since it's our own field, not a built-in one (bit us once: signup form showed "Username"/"Email" until fixed in Faz 6).

## Commands

```bash
source .venv/bin/activate

python manage.py check              # system checks, no DB connection required
python manage.py runserver

# Migrations use the session pooler (DIRECT_DATABASE_URL), not the transaction
# pooler used at runtime — PgBouncer transaction mode doesn't support the DDL
# Django's migrations need.
USE_DIRECT_DB=1 python manage.py migrate

USE_DIRECT_DB=1 python manage.py test --keepdb                                   # full suite
USE_DIRECT_DB=1 python manage.py test polls --keepdb                              # one app
USE_DIRECT_DB=1 python manage.py test polls.tests.test_models.SomeTest --keepdb   # one test case/method
```

**Always pass `--keepdb`.** Supabase only exposes pooler connections (Supavisor) to this project — there is no reachable non-pooler "direct connection" (it's IPv6-only and doesn't resolve on this network). Supavisor keeps a background connection to every database it has touched, so Django's normal `DROP DATABASE` teardown after a test run reliably fails with `database "test_postgres" is being accessed by other users`, which then blocks the *next* run too (`--noinput` doesn't help — recreation fails the same way). `--keepdb` sidesteps this by never dropping the test database. Tests also need `USE_DIRECT_DB=1` since the transaction-mode pooler (port 6543) can't run the DDL `manage.py test` needs.

If a stray `test_postgres` is ever left over and `--keepdb` still errors, connect with `DIRECT_DATABASE_URL` and run `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='test_postgres';` then `DROP DATABASE test_postgres;` — this can take one or two tries since Supavisor may reopen a connection immediately.

`config/settings.py` loads config from `.env` via `python-dotenv` (see `.env.example` for the full list of keys). `.env` itself is gitignored and holds real secrets/credentials — never commit it or print its contents.

## Environment gotchas already hit once — don't relearn these

- **Supabase connection string passwords must be URL-encoded** if they contain characters like `#`, `@`, `%`, `/`, `?`, `&`, `+`. An un-encoded `#` truncates the URL at the fragment marker and silently drops the rest of the string (looked like a wrong password, was actually a mangled URL). Encode with `urllib.parse.quote(password, safe='')`.
- **Vercel deploys this project zero-config.** It auto-detects Django from `requirements.txt` + `manage.py` and builds a single function from `config/wsgi.py` (which exports `app = application` for this reason — see the bottom of that file). **Do not add a `vercel.json` with a custom rewrite/route to `wsgi.py`** — doing so once broke routing entirely (real routes started 404ing) because Vercel's own internal rewrite for backend frameworks conflicted with a hand-written one. If `vercel.json` is ever needed (e.g. for `maxDuration`), scope it narrowly with the `functions` key targeting `config/wsgi.py`, not `rewrites`/`routes`/`builds`.
- `DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True` is required for compatibility with Supabase's transaction-mode pooler (PgBouncer) — don't remove it.

## Current state

Faz 0–7 are complete (setup, data model/admin, auth, poll creation, listing/detail, voting, design system, security/demo-data hardening). The full MVP feature set is live locally: signup/login/logout, poll creation with 2–5 products, home feed with search/filter/sort/pagination, poll detail with member+anonymous voting (AJAX with a no-JS form fallback), owner-only close/delete, a full design system (`static/css/main.css`), and a `seed_demo` management command. Remaining phases per `docs/PROJE_PLANI.md`: Faz 8 (Vercel deploy — the project itself was already deploy-verified in Faz 0, but production env vars are still placeholders and need real values before going live) and Faz 9 (post-MVP backlog, not started by design).

A `VoteAttempt` model (added Faz 7) backs a simple DB-based rate limit (60 vote requests/minute per voter) — see `polls/services.enforce_vote_rate_limit`.
