# Architecture Decision Records

## 1. Python + Flask as the backend language and framework
Date: 2026-10-09
Status: Decided
Context: YourTurn needs a small web backend that serves HTML pages and reads/writes SQLite, runs as one process in one container, and that I can explain line by line in a closed-book check. Python is the language I am most comfortable in.
Decision: Use Python with Flask, Jinja templates for the pages, and the standard-library `sqlite3` module for storage (no ORM).
Alternatives considered: Django, rejected because it brings an ORM, admin panel and project structure the app does not need, which would mean more code I did not write and must still explain. FastAPI, rejected because its main strengths (async, automatic JSON API docs) do not help an app that renders HTML pages for a single flat.
Consequences: The app stays small and every line is mine to explain; the cost is that I write the SQL and table setup by hand instead of getting them from an ORM.

## 2. Each domain owns its own rules, repository, service and routes
Date: 2026-10-11
Status: Decided
Context: Chores and supplies both answer "whose turn is it?", so it is tempting to share one turns module. But they must be splittable into separate services in Assignment 2, and their rules already differ (chores care about time, supplies about money).
Decision: Each domain is its own package (`chores/`, `supplies/`) with its own `rules.py` (Strategy classes + `factory_map`), `repository.py` (only SQL), `service.py` (logic, receives a repository) and `routes.py` (a Flask Blueprint). The only thing they share is the `roommates` table, which is the seam where they would be split.
Alternatives considered: A shared `turns/` module used by both domains, rejected because both domains would depend on it, so changing a chore rule could break supplies and the two could not be deployed separately without copying or extracting it first.
Consequences: Splitting later means moving one package plus its tables into a new service; the cost is some deliberate duplication (both domains have a `TakeTurns` rule).

## 3. Both domains reference one shared roommates table, and nothing else crosses between them
Date: 2026-10-09
Status: Decided
Context: Chores and supplies both need to know who the flatmates are, but in Assignment 2 they should be splittable into separate services, so their tables must not depend on each other.
Decision: Five tables: `roommates` is shared; `chores` + `chore_log` belong only to the chores domain and `supplies` + `purchases` only to the supplies domain. Each domain's log table points at `roommates.id`, and no chores table references a supplies table or the other way round. Dates are stored as ISO text (`YYYY-MM-DD`) and each item's "who's next" rule is stored as a text name (e.g. `take_turns`).
Alternatives considered: One generic `turns` table holding both chore completions and purchases with a `type` column, rejected because it would mix the two domains in one table (and purchases need a price that chores don't), making them impossible to split later.
Consequences: Splitting later only means giving each service its own copy (or API) of the roommates list; the cost is that a few queries are similar in both domains instead of shared.
