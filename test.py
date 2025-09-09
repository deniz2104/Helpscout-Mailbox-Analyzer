import os
import json
import sqlite3
import webbrowser
from threading import Timer
from flask import Flask, render_template_string, request, redirect, url_for

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

def get_connection():
    return sqlite3.connect(DB_FILE)

form_template = """
<h2>Set HELPSCOUT Credentials</h2>
<form method="post">
    <label>HELPSCOUT_CLIENT_ID:</label><br>
    <input type="text" name="client_id" required><br><br>
    
    <label>HELPSCOUT_CLIENT_SECRET:</label><br>
    <input type="text" name="client_secret" required><br><br>
    
    <button type="submit">Save</button>
</form>
"""

dashboard_template = """
<h2>Dashboard</h2>

<a href="{{ url_for('products') }}">➡ Manage Products</a><br><br>
<a href="{{ url_for('add_member_page') }}">➡ Add Team Member</a>
"""

add_member_template = """
<h2>Add New Team Member</h2>
<form method="post" action="{{ url_for('add_member') }}">
    <label>Name:</label><br>
    <input type="text" name="name" required><br><br>

    <label>WP.org Username:</label><br>
    <input type="text" name="wp_username" required><br><br>
    
    <label>HelpScout Name:</label><br>
    <input type="text" name="hs_name" required><br><br>
    
    <button type="submit">Add</button>
</form>

<br>
<a href="{{ url_for('dashboard') }}">⬅ Back to Dashboard</a>
"""

products_template = """
<h2>Products</h2>
<ul>
{% for pid, name, tags in products %}
    <li>
        <b>{{ name }}</b><br>
        Tags: {{ ", ".join(tags) if tags else "No tags" }}
        <br>
        <form method="post" action="{{ url_for('edit_tags', product_id=pid) }}">
            <input type="text" name="tags" placeholder="comma,separated,tags" value="{{ ','.join(tags) }}">
            <button type="submit">Update Tags</button>
        </form>
    </li>
{% endfor %}
</ul>

<hr>
<h3>Add New Product</h3>
<form method="post" action="{{ url_for('add_product') }}">
    <label>Name:</label><br>
    <input type="text" name="name" required><br><br>

    <label>Tags (comma separated):</label><br>
    <input type="text" name="tags"><br><br>

    <button type="submit">Add</button>
</form>

<br>
<a href="{{ url_for('dashboard') }}">⬅ Back to Dashboard</a>
"""

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

        return render_template_string(form_template)

    @app.route("/dashboard")
    def dashboard():
        return render_template_string(dashboard_template)

    @app.route("/add_member_page")
    def add_member_page():
        return render_template_string(add_member_template)

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

    @app.route("/products")
    def products():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name FROM products")
        products = cursor.fetchall()

        product_list = []
        for pid, name in products:
            cursor.execute("SELECT name FROM tags WHERE product_id=?", (pid,))
            tags = [row[0] for row in cursor.fetchall()]
            product_list.append((pid, name, tags))

        conn.close()
        return render_template_string(products_template, products=product_list)

    @app.route("/add_product", methods=["POST"])
    def add_product():
        name = request.form.get("name")
        tags_input = request.form.get("tags", "")
        tags = [t.strip() for t in tags_input.split(",") if t.strip()]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name) VALUES (?)", (name,))
        product_id = cursor.lastrowid

        for tag in tags:
            cursor.execute("INSERT INTO tags (name, product_id) VALUES (?, ?)", (tag, product_id))

        conn.commit()
        conn.close()

        return redirect(url_for("products"))

    @app.route("/edit_tags/<int:product_id>", methods=["POST"])
    def edit_tags(product_id):
        tags_input = request.form.get("tags", "")
        tags = [t.strip() for t in tags_input.split(",") if t.strip()]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM tags WHERE product_id=?", (product_id,))

        for tag in tags:
            cursor.execute("INSERT INTO tags (name, product_id) VALUES (?, ?)", (tag, product_id))

        conn.commit()
        conn.close()

        return redirect(url_for("products"))

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
