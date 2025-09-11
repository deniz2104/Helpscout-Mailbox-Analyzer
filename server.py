import os
import json
import webbrowser
from threading import Timer
from flask import Flask, request, redirect, url_for

DATA_FILE = "config.json"
DB_FILE = "app.db"

def load_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "HELPSCOUT_CLIENT_ID": "",
            "HELPSCOUT_CLIENT_SECRET": "",
            "TEAM_MEMBERS": {
                "Rodica": "Rodica Irodiu",
                "Kush": "Kush Namdev",
                "Poonam": "Poonam Namdev",
                "Stefan": "Stefan Cotitosu"
            },
            "WP_ORG_USERNAMES": {
                "rodicaelena": "Rodica",
                "Kush": "Kush",
                "Poonam Namdev": "Poonam",
                "Stefan Cotitosu": "Stefan",
            },
            "MAILBOX_PRO_ID": 21530,
            "MAILBOX_FREE_ID": 77254,
            "MAILBOX_OPTIMOLE_ID": 160661
        }
        save_data(default_data)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def credentials_exist(data):
    return data["HELPSCOUT_CLIENT_ID"] and data["HELPSCOUT_CLIENT_SECRET"]

from flask import Flask, render_template, request, redirect, url_for
# keep the rest of your imports...

def create_flask_app():    
    app = Flask(__name__)
    app.secret_key = "supersecret"
    
    @app.route("/", methods=["GET", "POST"])
    def index():
        data = load_data()

        if credentials_exist(data):
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            client_id = request.form.get("client_id")
            client_secret = request.form.get("client_secret")

            data["HELPSCOUT_CLIENT_ID"] = client_id
            data["HELPSCOUT_CLIENT_SECRET"] = client_secret
            save_data(data)

            return redirect(url_for("dashboard"))

        return render_template("form.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    return app

if __name__ == "__main__":
    port = 5001
    url = f"http://127.0.0.1:{port}/"

    def open_browser():
        webbrowser.open(url)

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        Timer(1, open_browser).start()

    app = create_flask_app()
    app.run(debug=True, host="0.0.0.0", port=port)