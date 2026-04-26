# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Collaboration style

- **Mae owns the backend; Claude owns the frontend.** Mae is focused on learning Python/FastAPI and wants to do the server-side work herself. Default to writing HTML/CSS/JS yourself, but for `main.py`, `cards.py`, `ai_resources.py`, `config.py` — pair with Mae rather than driving.
- **Teach, don't solve.** When Mae asks for help on a backend problem ("how do I…", "why isn't this working", "I'm stuck"), guide her through it: ask what she's tried, point at the area to investigate, name the concept she might be missing, and let her write the fix. Only show the full solution if she explicitly asks for it after attempting, or is clearly stuck after a couple of nudges. This rule does not apply to frontend work or to tasks she explicitly delegates.

## Run / dev commands

```bash
pip install -r requirements.txt
fastapi dev main.py          # auto-reload, http://127.0.0.1:8000/
# or:
uvicorn main:app --reload
```

The website is served at `/` and the API docs at `/docs`.

There is no test suite, linter, or build step configured in this repo.

## Architecture

This is a small FastAPI app (`main.py`) that performs a 3-card tarot reading and an AI interpretation, with a single-page static frontend served from the same app.

**Request flow** (one full reading):
1. `GET /get_id` → returns a fresh UUID; the frontend stores it in `sessionStorage`.
2. `POST /reason` with `{uuid, reason}` → seeds `reason_data[uuid]` and initializes `card_list[uuid] = []`.
3. `GET /get_card?uuid=…` (called up to 3 times) → appends a random card from `cards.tarot_cards` to `card_list[uuid]` and returns the full list so far.
4. `GET /overview?uuid=…` → calls `ai_message()` in `ai_resources.py`, which sends the cards + reason to an OpenAI-compatible endpoint (configured in `config.py`) using the "Caine" system prompt and returns the formatted reading.

**State model.** `card_list` and `reason_data` in `main.py` are module-level dicts keyed by UUID. This is the multi-user mechanism: each browser session gets its own UUID so concurrent readings don't collide. State is in-memory only — restarting the server wipes all sessions. Anything that needs per-session state must go through these two dicts.

**Frontend ↔ backend wiring.** `static/index.html` + `static/app.js` + `static/style.css` are served via `app.mount("/static", ...)` and `GET /` returns `static/index.html` via `FileResponse`. The frontend talks to the same-origin endpoints listed above; no CORS config is needed because everything is served by the one FastAPI app.

**AI client.** `ai_resources.py` constructs an `OpenAI` client pointed at `BASE_URL` from `config.py` (currently a Synthetic API endpoint, not openai.com). The `AI_DESCRIPTION` system prompt defines card position semantics (situation / challenge / outcome, plus reversals for cards 4-6) and the exact output format Caine must follow.

**Card data.** `cards.py` is a flat list of all 78 tarot card name strings (Major Arcana + four Minor Arcana suits). Cards are drawn with `random.choice` — duplicates within a single reading are possible by design.

## Notes from `steps.txt`

`steps.txt` is Mae's working notebook for the project (the original 10-step UX sketch and HTTP request/response anatomy notes). It's not a spec — treat it as design intent rather than authoritative requirements.
