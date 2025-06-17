import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

DB = 'orders.db'
LIMIT = int(os.environ.get('ANTISPAM_LIMIT', 2))
WINDOW_MIN = int(os.environ.get('ANTISPAM_WINDOW_MINUTES', 5))

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
      CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        desk INTEGER, items TEXT, timestamp DATETIME, done INTEGER DEFAULT 0
      )
    """)
    conn.commit(); conn.close()
init_db()

def count_recent(desk):
    cutoff = datetime.utcnow() - timedelta(minutes=WINDOW_MIN)
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM orders WHERE desk=? AND timestamp>=? AND done=0",
              (desk, cutoff.isoformat()))
    cnt = c.fetchone()[0]
    conn.close()
    return cnt

@app.route('/')
def index():
    return "<h1>OK – <a href='/panel.html'>Panel</a></h1>"

@app.route('/menu.html')
def menu_page():
    return render_template('menu.html')

@app.route('/panel.html')
def panel_page():
    return render_template('panel.html')

@app.route('/api/orders', methods=['GET'])
def api_orders():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # aktywne
    c.execute("SELECT id,desk,items FROM orders WHERE done=0 ORDER BY timestamp")
    active = c.fetchall()
    # zakończone jako stos (ORDER BY timestamp DESC)
    c.execute("SELECT id,desk,items FROM orders WHERE done=1 ORDER BY timestamp DESC")
    done = c.fetchall()
    conn.close()
    return jsonify({
      'active': [{'id':r[0],'desk':r[1],'items':r[2]} for r in active],
      'done':   [{'id':r[0],'desk':r[1],'items':r[2]} for r in done]
    })

@app.route('/api/order', methods=['POST'])
def api_order():
    data = request.get_json()
    desk = data.get('desk'); items = data.get('items')
    # antyspam
    if count_recent(desk) >= LIMIT:
        return jsonify({'error':'Limit zamówień przekroczony'}), 429
    ts = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO orders (desk,items,timestamp) VALUES (?,?,?)",
              (desk,','.join(items), ts))
    conn.commit(); conn.close()
    return jsonify({'message':'OK'}), 201

@app.route('/api/order/<int:order_id>', methods=['PATCH'])
def api_toggle(order_id):
    # toggle done status: aktywne->done, done->active
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT done FROM orders WHERE id=?", (order_id,))
    cur = c.fetchone()
    if not cur: return jsonify({}),404
    new = 0 if cur[0]==1 else 1
    c.execute("UPDATE orders SET done=? WHERE id=?", (new,order_id))
    conn.commit(); conn.close()
    return jsonify({'done': new})

@app.route('/api/limit/<int:desk>', methods=['GET'])
def api_limit(desk):
    used = count_recent(desk)
    return jsonify({
      'limit': LIMIT,
      'used': used,
      'remaining': max(0, LIMIT-used),
      'reset_in_sec': max(0,
        int(( (datetime.utcnow() - (datetime.utcnow()-timedelta(minutes=WINDOW_MIN))).total_seconds() ))
      )
    })

if __name__=='__main__':
    port = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0', port=port)
