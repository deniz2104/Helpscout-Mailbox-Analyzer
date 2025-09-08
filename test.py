import os
import json
import subprocess
import sys

DATA_FILE = "config.json"
VENV_DIR = "env"
REQUIREMENTS_FILE = "requirements.txt"

def get_venv_python():
    """Get the path to the Python executable in the virtual environment."""
    if os.name == 'nt':  # Windows
        return os.path.join(VENV_DIR, "Scripts", "python")
    else:  # macOS/Linux
        return os.path.join(VENV_DIR, "bin", "python")

def get_venv_pip():
    """Get the path to the pip executable in the virtual environment."""
    if os.name == 'nt':  # Windows
        return os.path.join(VENV_DIR, "Scripts", "pip")
    else:  # macOS/Linux
        return os.path.join(VENV_DIR, "bin", "pip")

def setup_virtual_environment_sync():
    """Set up virtual environment and install requirements synchronously."""
    try:
        # Check if virtual environment already exists
        if not os.path.exists(VENV_DIR):
            print("Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
            print("Virtual environment created successfully!")
        
        pip_path = get_venv_pip()
        
        # Install requirements if requirements.txt exists
        if os.path.exists(REQUIREMENTS_FILE):
            print("Installing/updating requirements...")
            subprocess.run([pip_path, "install", "-r", REQUIREMENTS_FILE], check=True)
            print("Requirements installed successfully!")
        else:
            print("No requirements.txt found, skipping package installation.")
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting up virtual environment: {e}")
        return False
    except (OSError, FileNotFoundError) as e:
        print(f"Error during environment setup: {e}")
        return False

def is_running_in_venv():
    """Check if we're already running in the virtual environment."""
    return (hasattr(sys, 'real_prefix') or 
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
            sys.executable.endswith(os.path.join(VENV_DIR, "bin", "python")) or
            sys.executable.endswith(os.path.join(VENV_DIR, "Scripts", "python.exe")))

def restart_in_venv():
    """Restart the application using the virtual environment's Python."""
    venv_python = get_venv_python()
    if os.path.exists(venv_python):
        print(f"Restarting application with virtual environment Python: {venv_python}")
        # Re-run this script with the virtual environment's Python
        subprocess.run([venv_python] + sys.argv, check=False)
        sys.exit(0)
    else:
        print("Virtual environment Python not found!")
        return False

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

def create_flask_app():
    """Create and configure the Flask application."""
    try:
        from flask import Flask, render_template_string, request, redirect, url_for
    except ImportError:
        print("Flask not found. Please ensure the virtual environment is set up correctly.")
        sys.exit(1)
    
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

        return render_template_string(form_template)

    @app.route("/dashboard")
    def dashboard():
        data = load_data()
        return render_template_string(
            dashboard_template, 
            team_members=data["TEAM_MEMBERS"], 
            wp_usernames=data["WP_ORG_USERNAMES"]
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
    
    return app

if __name__ == "__main__":
    print("Starting HelpScout Mailbox Analyzer...")
    
    # Check if we're running in the virtual environment
    if not is_running_in_venv():
        print("Setting up virtual environment...")
        if setup_virtual_environment_sync():
            print("Virtual environment ready. Restarting in virtual environment...")
            restart_in_venv()
        else:
            print("Failed to set up virtual environment. Exiting.")
            sys.exit(1)
    else:
        print("Running in virtual environment. Starting Flask application...")
    
    app = create_flask_app()
    app.run(debug=True, host='0.0.0.0', port=5001)
