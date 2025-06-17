import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, url_for
from flask_cors import CORS

app = Flask(
    __name__,
    static_folder='static',
    template_folder='templates'
)
CORS(app)

DB_PATH = 'orders.db'
ANTISPAM_LIMIT = 2
ANTISPAM_WINDOW_MINUTES = 5

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            desk INTEGER,
            items TEXT,
            timestamp DATETIME
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return "<h1>Serwis działa. <a href='/panel.html'>Przejdź do panelu</a></h1>"

@app.route('/menu.html')
def menu_page():
    # linki do CSS/JS będą generowane przez url_for
    return render_template('menu.html')

@app.route('/panel.html')
def panel_page():
    return render_template('panel.html')

@app.route('/api/orders', methods=['GET'])
def get_orders():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, desk, items FROM orders ORDER BY timestamp ASC")
    rows = c.fetchall()
    conn.close()
    orders = [{'id': r[0], 'desk': r[1], 'items': r[2]} for r in rows]
    return jsonify(orders)

@app.route('/api/order', methods=['POST'])
def create_order():
    data = request.get_json()
    desk = data.get('desk')
    items = data.get('items')
    timestamp = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO orders (desk, items, timestamp) VALUES (?, ?, ?)",
        (desk, items, timestamp)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Order created'}), 201

@app.route('/api/order/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Order deleted'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
