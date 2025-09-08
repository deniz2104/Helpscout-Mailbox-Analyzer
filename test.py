import os
import json
from flask import Flask, render_template_string, request, redirect, url_for

DATA_FILE = "config.json"

app = Flask(__name__)
app.secret_key = "supersecret"

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
            }
        }
        save_data(default_data)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def credentials_exist(data):
    return data["HELPSCOUT_CLIENT_ID"] and data["HELPSCOUT_CLIENT_SECRET"]

form_template = """
<h2>Set HELPSCOUT Credentials (One-time setup)</h2>
<form method="post">
    <label>HELPSCOUT_CLIENT_ID:</label><br>
    <input type="text" name="client_id" required><br><br>
    
    <label>HELPSCOUT_CLIENT_SECRET:</label><br>
    <input type="text" name="client_secret" required><br><br>
    
    <button type="submit">Save</button>
</form>
"""

dashboard_template = """

<h3>Add New Team Member</h3>
<form method="post" action="{{ url_for('add_member') }}">
    <label>Name:</label><br>
    <input type="text" name="name" required><br><br>

    <label>WP.org Username:</label><br>
    <input type="text" name="wp_username" required><br><br>
    
    <label>HelpScout Name:</label><br>
    <input type="text" name="hs_name" required><br><br>
    
    <button type="submit">Add</button>
</form>
"""

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

    return render_template_string(form_template)

@app.route("/dashboard")
def dashboard():
    data = load_data()
    return render_template_string(
        dashboard_template,
        members=data["TEAM_MEMBERS"],
        wp_users=data["WP_ORG_USERNAMES"]
    )

@app.route("/add_member", methods=["POST"])
def add_member():
    data = load_data()
    name = request.form.get("name")
    hs_name = request.form.get("hs_name")
    wp_username = request.form.get("wp_username")

    data["TEAM_MEMBERS"][name] = hs_name
    data["WP_ORG_USERNAMES"][wp_username] = name
    save_data(data)

    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
