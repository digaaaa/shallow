# YourTurn

YourTurn answers the question every shared flat argues about: **"whose turn is it?"** Roommates pick their name (no login) and the app keeps track of two things:

- **Chores**: chores repeat on a schedule (e.g. dishes daily, bathroom weekly). When someone presses "I did it", the app logs it and shows whose turn is next. It also flags overdue chores ("bins not done for 3 days") and shows who did the most chores this month.
- **Shared supplies**: shared items like eggs, coffee pods or toilet paper. When someone presses "I bought it" and enters the price, the app shows whose turn it is to buy next and how much each roommate has spent this month.

This is a single-process monolithic app (Python + Flask + SQLite), built for Individual Assignment 1.

## Architecture

```
                    app.py  (Flask app, registers both blueprints)
                 /                                        \
     chores/  (Domain 1: time)                 supplies/  (Domain 2: money)
       routes.py      Flask Blueprint /chores    routes.py      Flask Blueprint /supplies
       service.py     logic                      service.py     logic
       rules.py       TakeTurns, LeastRecent     rules.py       TakeTurns, LeastSpent
       repository.py  SQL only                   repository.py  SQL only
            |                                         |
     chores, chore_log  ---->  roommates  <----  supplies, purchases
                          (the only shared table = the seam)
```

Each domain owns its own rules, logic, SQL and pages. They share **only** the `roommates` table, so in Assignment 2 they can be split into two services along that seam. The reasons are in [ADR.md](ADR.md).

- **Strategy pattern**: each "who's next" rule (`TakeTurns`, `LeastRecent`, `LeastSpent`) is a class with a `next_person(...)` method, so a chore or supply can use any rule.
- **`factory_map`**: the rule name stored in the database (e.g. `"least_spent"`) is turned into the right rule object by a small dictionary.
- **Service receives its repository**: the logic never writes SQL itself, which keeps it easy to test.

## Run it locally

Requires Python 3.10 or newer.

```bash
git clone https://github.com/digaaaa/yourturn.git
cd yourturn
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

Install and start:

```bash
pip install -r requirements.txt
python app.py
```

Then open http://localhost:8000. There is no setup step: on first start the app creates the database tables and loads the demo data from `seed.json` by itself.

## Configuration

Everything is configured with environment variables. None are required and no `.env` file is needed.

| Variable | Default | What it does |
|---|---|---|
| `PORT` | `8000` | Port the web server listens on. The server always binds to `0.0.0.0`. |
| `DATA_DIR` | `./data` | Folder where the SQLite database is stored. Created automatically if missing. |

**SQLite path:** `<DATA_DIR>/yourturn.db`, so `./data/yourturn.db` by default (for example `/data/yourturn.db` when `DATA_DIR=/data`).

Example with custom settings:

```bash
# Windows PowerShell
$env:PORT="9000"; $env:DATA_DIR="C:\temp\yourturn"; python app.py
# macOS / Linux
PORT=9000 DATA_DIR=/tmp/yourturn python app.py
```

**Startup behaviour:**
- Tables are created with `CREATE TABLE IF NOT EXISTS`, so restarting never deletes data.
- `seed.json` is only loaded into tables that are still empty, so starting the app twice never duplicates rows.

## Tests and coverage

Coverage command:

```bash
python -m pytest --cov=chores --cov=supplies --cov=db --cov-report=term-missing
```

Result:

```
Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
chores\__init__.py           0      0   100%
chores\repository.py        16      0   100%
chores\routes.py            28      0   100%
chores\rules.py             29      0   100%
chores\service.py           43      0   100%
db.py                       35      0   100%
supplies\__init__.py         0      0   100%
supplies\repository.py      16      0   100%
supplies\routes.py          28      0   100%
supplies\rules.py           26      0   100%
supplies\service.py         40      0   100%
------------------------------------------------------
TOTAL                      261      0   100%

71 passed in 1.00s
```

What is tested (details in ADR 4):
- **Rules**: every "who's next" rule with edge cases (nobody did it yet, wrap-around, ties, someone moved out).
- **Services**: against a real in-memory SQLite database. `today` is passed in so date logic (overdue days, "this month") is tested with fixed dates.
- **Routes**: the pages and forms through Flask's test client, including rejected bad input.
- **Startup contract**: `PORT` and `DATA_DIR` handling, booting twice without duplicate rows, foreign keys switched on.

## Project layout

```
app.py            Flask app and entry point (python app.py)
db.py             SQLite path, tables and seeding
seed.json         demo roommates, chores and supplies
requirements.txt  pinned dependencies (the only manifest)
pytest.ini        pytest settings
chores/           Domain 1: repository, rules, service, routes
supplies/         Domain 2: repository, rules, service, routes
templates/        Jinja HTML pages
tests/            pytest test suite
ADR.md            architecture decision records
AI_USAGE.md       log of how AI was used
```
