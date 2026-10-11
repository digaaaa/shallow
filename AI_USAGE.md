# AI Usage Log

| Date/commit | Tool | Prompt | Disposition (Accepted/Modified/Rejected) | What changed & why (if modified) | In my own words, how this works |
|---|---|---|---|---|---|
| 2026-10-09 / 338c54c | Claude Code | "change the readme and gitignore because I changed the concept of my project" | Accepted | README rewritten from Shallow to YourTurn; removed `node_modules/` from `.gitignore` | TODO |
| 2026-10-09 / (this commit) | Claude Code | "let's move on to the second commit" (project skeleton: Flask app, pinned requirements, ADR #1) | Accepted | Created `app.py`, `requirements.txt`, `ADR.md` | TODO |
| 2026-10-09 / (this commit) | Claude Code | "let's do commit 3" (database setup: tables, seed data, ADR #3) | Accepted | Created `db.py` and `seed.json`, `app.py` now calls `init_db()` before starting, added ADR #3 | TODO |
| 2026-10-09 / (this commit) | Claude Code | "let's do commit 4" (chore "who's next" rules with the Strategy pattern, plus tests) | Accepted | Created `chores/rules.py` (`ChoreRule`, `TakeTurns`, `LeastRecent`, `factory_map`, `get_rule`), `tests/test_chore_rules.py` and `pytest.ini` | TODO |
| 2026-10-11 / (this commit) | Claude Code | "commit 5" (chores repository + service: I did it, who's next, overdue) | Accepted | Created `chores/repository.py` (SQL only), `chores/service.py` (`ChoreService`, `days_overdue`), `tests/conftest.py` (in-memory DB fixture) and `tests/test_chore_service.py` | TODO |
| 2026-10-11 / (this commit) | Claude Code | "let's do commit 6" (chores page: routes, templates, I did it button) | Accepted | Created `chores/routes.py` (Blueprint with page + POST route), `templates/` (base, index, chores), route tests; `app.py` registers the blueprint; service got `roommates()` and `next_person_id` | TODO |
| 2026-10-11 / (this commit) | Claude Code | "let's do commit 7" (chore stats this month + ADR #2) | Accepted | Added `count_done_since` (repository), `monthly_stats` (service), a "This month" table on the chores page, a test, and ADR #2 | TODO |
| 2026-10-11 / (this commit) | Claude Code | "ok let's do commit 8" (supplies rules, repository and service) | Accepted | Created `supplies/rules.py` (`SupplyRule`, `TakeTurns`, `LeastSpent`, `factory_map`), `supplies/repository.py`, `supplies/service.py` (`record_purchase`, `next_person`, `overview`, `monthly_spending`) and their tests | TODO |
