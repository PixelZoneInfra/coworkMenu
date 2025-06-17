import os
import sqlite3
import threading
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

DB_PATH = 'order_queue.db'
ANTISPAM_LIMIT = 2  # max zamówień
ANTISPAM_WINDOW = timedelta(minutes=5)

app = Flask(__name__)
CORS(app)
lock = threading.Lock()

# Inicjalizacja bazy
with lock:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            desk TEXT,
            items TEXT,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()

# Sprawdzenie anty-spam
def can_order(desk):
    now = datetime.utcnow()
    window_start = now - ANTISPAM_WINDOW
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*) FROM orders
        WHERE desk = ? AND timestamp >= ?
    """, (desk, window_start))
    count = c.fetchone()[0]
    conn.close()
    return count < ANTISPAM_LIMIT

@app.route('/api/order', methods=['POST'])
def api_order():
    data = request.json
    desk = data.get('desk')
    items = data.get('items')
    if not desk or not items:
        return jsonify({'error': 'Brak danych'}), 400
    if not can_order(desk):
        return jsonify({'error': 'Limit zamówień osiągnięty. Poczekaj chwilę.'}), 429
    with lock:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO orders (desk, items, timestamp) VALUES (?, ?, ?)"
                  , (desk, str(items), datetime.utcnow()))
        conn.commit()
        order_id = c.lastrowid
        conn.close()
    return jsonify({'order_id': order_id}), 201

@app.route('/api/orders', methods=['GET'])
def api_orders():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, desk, items FROM orders ORDER BY id")
    rows = c.fetchall()
    conn.close()
    orders = [{'id': r[0], 'desk': r[1], 'items': r[2]} for r in rows]
    return jsonify(orders)

@app.route('/api/order/<int:order_id>', methods=['DELETE'])
def api_delete(order_id):
    with lock:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        conn.commit()
        conn.close()
    return '', 204

@app.route('/menu')
def menu_page():
    desk = request.args.get('desk', 'unknown')
    return render_template('menu.html', desk=desk)

@app.route('/panel')
def panel_page():
    return render_template('panel.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
