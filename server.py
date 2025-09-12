import os
import json
import csv
import webbrowser
import calendar
from threading import Timer
from flask import Flask, render_template, request, redirect, url_for, send_file
from config_loader import load_config
from helper_file_to_get_last_month import get_last_month

DATA_FILE = "config.json"
config = load_config()

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

def json_exist():
    csv_folder = "CSVs"
    json_files = [f for f in os.listdir(csv_folder) if f.endswith('.json')]
    return len(json_files) == 3

def create_csv_from_json_files():
    if not json_exist():
        return []

    csv_folder = "CSVs"
    json_files = [f for f in os.listdir(csv_folder) if f.endswith('.json')]

    all_data = {}
    
    for json_file in json_files:
        file_path = os.path.join(csv_folder, json_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for category, team_data in data.items():
            if category in all_data:
                for member, count in team_data.items():
                    if member in all_data[category]:
                        all_data[category][member] += count
                    else:
                        all_data[category][member] = count
            else:
                all_data[category] = team_data.copy()

    sorted_team_members = sorted(list(config.get("TEAM_MEMBERS", {}).values()))

    csv_data = []

    header = ["Product"] + sorted_team_members
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

    @app.route("/export")
    def export_data():
        try:
            csv_data = create_csv_from_json_files()

            last_month = get_last_month()
            csv_filename = f"cost_allocation_for_{calendar.month_name[last_month]}.csv"
            csv_path = os.path.join("CSVs", csv_filename)
            
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

    def open_browser():
        webbrowser.open(url)

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        Timer(1, open_browser).start()

    app = create_flask_app()
    app.run(debug=True, host="0.0.0.0", port=port)