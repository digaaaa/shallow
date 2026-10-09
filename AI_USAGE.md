# AI Usage Log

| Date/commit | Tool | Prompt | Disposition (Accepted/Modified/Rejected) | What changed & why (if modified) | In my own words, how this works |
|---|---|---|---|---|---|
| 2026-10-09 / 338c54c | Claude Code | "change the readme and gitignore because I changed the concept of my project" | Accepted | README rewritten from Shallow to YourTurn; removed `node_modules/` from `.gitignore` | TODO |
| 2026-10-09 / (this commit) | Claude Code | "let's move on to the second commit" (project skeleton: Flask app, pinned requirements, ADR #1) | Accepted | Created `app.py`, `requirements.txt`, `ADR.md` | TODO |
| 2026-10-09 / (this commit) | Claude Code | "let's do commit 3" (database setup: tables, seed data, ADR #3) | Accepted | Created `db.py` and `seed.json`, `app.py` now calls `init_db()` before starting, added ADR #3 | TODO |
| 2026-10-09 / (this commit) | Claude Code | "let's do commit 4" (chore "who's next" rules with the Strategy pattern, plus tests) | Accepted | Created `chores/rules.py` (`ChoreRule`, `TakeTurns`, `LeastRecent`, `factory_map`, `get_rule`), `tests/test_chore_rules.py` and `pytest.ini` | TODO |
