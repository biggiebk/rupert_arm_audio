from flask import Flask
from markupsafe import escape

# Rupert Modules
from rupert.shared.synapse import Synapse

app = Flask(__name__)

@app.route("/audio/<room>/<file>")
def bedroom(room, file):
    return f"Room: {escape(room)} File: {escape(file)}"
