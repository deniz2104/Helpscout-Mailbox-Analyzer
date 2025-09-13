import sqlite3
from Database.database_schema import get_connection

def make_database_predefined_values():
    """Populate the database with predefined products and tags if empty."""
    connection :sqlite3.Connection=get_connection()
    cursor : sqlite3.Cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]

    if product_count == 0:
        predefined : list[tuple[str, list[str]]] =[
            ("Neve",["neve", "neve-pro","neve pro (plugin)"]),
            ("Hestia",["hestia","hestia-pro"]),
            ("Feedzy",["feedzy"]),
            ("Church FSE",["church-fse"]),
            ("Fork",["fork"]),
            ("FSE Themes",["fse-themes","fse design pack"]),
            ("Hyve",["hyve"]),
            ("Jaxon",["jaxon"]),
            ("Lightstart",["lightstart"]),
            ("Masteriyo",["masteriyo"]),
            ("Menu Icons",["menu-icons"]),
            ("MPG",["mpg","multiple pages generator"]),
            ("Neve FSE",["neve fse"]),
            ("Optionistics",["optionistics"]),
            ("Orbit Fox",["orbit fox"]),
            ("Otter Blocks",["otter","otter pro"]),
            ("PPOM",["ppom","ppom-account","ppom pro"]),
            ("Raft",["raft"]),
            ("Redirection for CF7",["redirection-cf7","redirection for cf7","wpcf7"]),
            ("Revive Social",["revive social","revive-old-post"]),
            ("Riverbank",["riverbank"]),
            ("Sparks",["sparks for woocommerce"]),
            ("Super Page Cache",["super-page-cache","super page cache pro"]),
            ("Templates Cloud",["templates-cloud"]),
            ("Visualizer",["visualizer","visualizer plugin","visualizer: tables and charts manager"]),
            ("WP Full Pay",["wp full members bundle","wp full pay","wp full pay bundle"]),
            ("WP Landing Kit",["wp landing kit","wplandingkit"]),
            ("WP Media Library",["wp-media-library"]),
            ("Zelle Pro",["zelle-pro"]),
            ("Zerif Pro",["zerif-pro"]),
            ("Bundles",["themeisle-bundle","essential","business","vip","treasure chest lite","treasure chest","treasure chest plus","pirate club"]),
            ("ShopIsle",["shopisle-pro","shop-isle-pro"]),
            ("ROP",["rop-new-features","rop-new-feature-skip","rop-linkedin-403","rop-instagram","rop-api-issue","rop"])
        ]
        
        """ Insert predefined products and tags into the database """
        for name, tags in predefined:
            cursor.execute("INSERT INTO products (name) VALUES (?)", (name,))
            product_id = cursor.lastrowid
            for tag in tags:
                cursor.execute("INSERT INTO tags (name, product_id) VALUES (?, ?)", (tag, product_id))

        connection.commit()
    connection.close()