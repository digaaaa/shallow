# Architecture Decision Records

## 1. Python + Flask as the backend language and framework
Date: 2026-10-09
Status: Decided
Context: YourTurn needs a small web backend that serves HTML pages and reads/writes SQLite, runs as one process in one container, and that I can explain line by line in a closed-book check. Python is the language I am most comfortable in.
Decision: Use Python with Flask, Jinja templates for the pages, and the standard-library `sqlite3` module for storage (no ORM).
Alternatives considered: Django, rejected because it brings an ORM, admin panel and project structure the app does not need, which would mean more code I did not write and must still explain. FastAPI, rejected because its main strengths (async, automatic JSON API docs) do not help an app that renders HTML pages for a single flat.
Consequences: The app stays small and every line is mine to explain; the cost is that I write the SQL and table setup by hand instead of getting them from an ORM.
