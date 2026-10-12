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

## 4. Test the rules as pure functions and the services against a real in-memory SQLite database
Date: 2026-10-12
Status: Decided
Context: The brief requires at least 70% coverage of the core business logic of both domains, and the logic that matters most is "whose turn is next" plus overdue days and monthly totals, which all depend on dates.
Decision: The "who's next" rules take plain lists (no database), so they get many small unit tests covering edge cases (nobody did it yet, wrap-around, ties, someone moved out). Services are tested against an in-memory SQLite database built from the real `SCHEMA` (a fake, not mocks), `today` is always passed in as a parameter so tests never depend on the real date, and the routes plus startup contract (`PORT`, `DATA_DIR`, seeding twice) get a few tests with Flask's test client and `monkeypatch`.
Alternatives considered: Mocking the repository in service tests, rejected because the SQL queries (`GROUP BY`, `SUM`, date filters) are where real bugs would hide, and an in-memory database tests them for real while still being fast.
Consequences: Coverage of `chores/`, `supplies/` and `db.py` is 100% and the suite runs in about a second; left thinner on purpose: how the HTML looks and real browser (end-to-end) tests, since they are slow and the logic underneath is already covered.

## 5. Deliberately not building a third "Borrowing" domain
Date: 2026-10-12
Status: Decided
Context: Flatmates also borrow each other's things ("took your boots" → "put them back"), and I planned Borrowing as an optional third domain. The brief says a third domain is only worth a small amount and should not take time away from testing and the process documents.
Decision: Do not build Borrowing. YourTurn ships with exactly two domains, Chores and Supplies, each fully tested.
Alternatives considered: Building Borrowing as a third blueprint with its own `borrowings` table, rejected because with a three-day schedule it would have meant thinner tests and a rushed README and ADR log, which are worth far more of the grade than an extra domain.
Consequences: The app does less for flatmates today, but because domains share only the `roommates` table, Borrowing can be added later as a new `borrowing/` package and table that points at `roommates`, without changing chores or supplies at all.
