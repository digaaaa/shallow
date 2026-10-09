"""YourTurn entry point. Start the app with: python app.py"""

import os

from flask import Flask

from db import init_db

app = Flask(__name__)


@app.route("/")
def home():
    return "YourTurn is running"


if __name__ == "__main__":
    # Create the tables and load seed data before the server starts.
    init_db()
    # The port comes from the PORT environment variable (default 8000).
    port = int(os.environ.get("PORT", "8000"))
    # 0.0.0.0 means "accept connections from outside this machine",
    # which the container needs. localhost would only accept local ones.
    app.run(host="0.0.0.0", port=port)
