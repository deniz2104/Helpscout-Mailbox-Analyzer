import os
import json
import csv
import webbrowser
import calendar
from threading import Timer
from flask import Flask, render_template, request, redirect, url_for, send_file
from CredentialsAndJsonManager.config_loader import load_config
from HelperFiles.helper_file_to_get_last_month import get_last_month

DATA_FILE = "config.json"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_FILE = os.path.join(PROJECT_ROOT, "config.json")
CSV_FOLDER = os.path.join(PROJECT_ROOT, "CSVs")

def load_data() -> dict:
    """Load configuration data from config.json, creating it with default values if it doesn't exist."""
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
                "rodicaelena": "Rodica Irodiu",
                "Kush": "Kush Namdev",
                "Poonam Namdev": "Poonam Namdev",
                "Stefan Cotitosu": "Stefan Cotitosu",
            },
            "MAILBOX_PRO_ID": 21530,
            "MAILBOX_FREE_ID": 77254,
            "MAILBOX_OPTIMOLE_ID": 160661
        }
        save_data(default_data)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data: dict) -> None:
    """Save configuration data to config.json."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def credentials_exist(data: dict) -> bool:
    """Check if Helpscout credentials exist in the provided data dictionary."""
    return data["HELPSCOUT_CLIENT_ID"] and data["HELPSCOUT_CLIENT_SECRET"]

def json_exist() -> bool:
    """Check if the required JSON files exist in the CSVs directory to make the final CSV."""
    csv_folder = CSV_FOLDER
    if not os.path.exists(csv_folder):
        return False
    json_files = [f for f in os.listdir(csv_folder) if f.endswith('.json')]
    return len(json_files) == 3

def create_csv_from_json_files() -> list[list[str]]:
    """CreateCSV data list from existing JSON files."""
    if not json_exist():
        return []

    csv_folder = CSV_FOLDER
    json_files :list[str] = [f for f in os.listdir(csv_folder) if f.endswith('.json')]

    all_data = {}
    
    for json_file in json_files:
        file_path = os.path.join(csv_folder, json_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            data :dict = json.load(f)

        for category, team_data in data.items():
            if category in all_data:
                for member, count in team_data.items():
                    if member in all_data[category]:
                        all_data[category][member] += count
                    else:
                        all_data[category][member] = count
            else:
                all_data[category] = team_data.copy()

    config=load_config()
    sorted_team_members :list[str] = sorted(list(config.get("TEAM_MEMBERS", {}).values()))

    csv_data = []
    header :list[str] = ["Product"] + sorted_team_members
    csv_data.append(header)

    for product in sorted(all_data.keys()):
        row = [product]
        team_data = all_data[product]

        for member in sorted_team_members:
            count = team_data.get(member, 0)
            row.append(count)
        
        csv_data.append(row)
    
    return csv_data


def create_flask_app():
    base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    templates_dir = os.path.join(base_directory, "templates")
    static_dir = os.path.join(base_directory, "static")
    app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir, static_url_path='/static')
    app.secret_key = "supersecret"
    
    @app.route("/", methods=["GET", "POST"])
    def index():
        """Handle the index route for displaying and submitting Helpscout credentials."""
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

    @app.route("/check_json_files")
    def check_json_files():
        """Check if JSON files exist and return status."""
        return {"json_files_exist": json_exist()}

    @app.route("/export")
    def export_data():
        """Export data from JSON files to a CSV and provide it for download."""
        try:
            csv_data = create_csv_from_json_files()

            last_month = get_last_month()
            csv_filename = f"cost_allocation_for_{calendar.month_name[last_month].lower()}.csv"
            os.makedirs(CSV_FOLDER, exist_ok=True)
            csv_path = os.path.join(CSV_FOLDER, csv_filename)

            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                for row in csv_data:
                    writer.writerow(row)
            
            return send_file(csv_path, as_attachment=True, download_name=csv_filename)
            
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            return f"Error exporting data: {str(e)}", 500

    return app

if __name__ == "__main__":
    port = 5001
    url = f"http://127.0.0.1:{port}/"

    """Open the default web browser to the Flask app URL after a short delay."""
    def open_browser():
        webbrowser.open(url)

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        Timer(1, open_browser).start()

    app = create_flask_app()
    app.run(debug=True, host="0.0.0.0", port=port)