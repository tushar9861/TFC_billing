import threading
from flask import Flask, jsonify, request, render_template, send_from_directory
from PyQt5.QtCore import QObject, pyqtSignal
import sqlite3
import json

app = Flask(__name__, template_folder="templates")

# PyQt signals to communicate with the main GUI thread safely
class WebServerSignals(QObject):
    new_order = pyqtSignal(dict)

signals = WebServerSignals()

def get_db_connection():
    conn = sqlite3.connect('tfc_outlet.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/menu', methods=['GET'])
def get_menu():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, name, category, price_online as price, inventory_type as type FROM products ORDER BY category, name")
        products = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify({"success": True, "products": products})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/order', methods=['POST'])
def place_order():
    try:
        data = request.json
        customer_name = data.get('customer_name', 'Walk-in')
        customer_phone = data.get('customer_phone', '')
        items = data.get('items', [])
        total_amount = data.get('total_amount', 0.0)
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO web_orders (customer_name, customer_phone, items, total_amount, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (customer_name, customer_phone, json.dumps(items), total_amount, 'pending'))
        order_id = c.lastrowid
        conn.commit()
        conn.close()
        
        order_data = {
            'id': order_id,
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'items': items,
            'total_amount': total_amount
        }
        # Emit signal to notify PyQt UI
        signals.new_order.emit(order_data)
        
        return jsonify({"success": True, "order_id": order_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    try:
        phone = request.args.get('phone', '').strip()
        notifications = []
        
        # 1. Global Offers
        notifications.append({
            "id": "offer_50off",
            "type": "offer",
            "title": "New Offer Available! 🎉",
            "message": "Get 50% OFF on your first combo! Order now.",
            "timestamp": "now"
        })
        
        # 2. Order Status
        if phone:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT id, status FROM web_orders WHERE customer_phone = ? ORDER BY id DESC LIMIT 5", (phone,))
            orders = c.fetchall()
            conn.close()
            
            for o in orders:
                status = o['status'].lower()
                status_msg = ""
                if status == 'accepted':
                    status_msg = f"Your order #{o['id']} has been accepted and is being prepared!"
                elif status == 'ready':
                    status_msg = f"Your order #{o['id']} is ready for pickup!"
                elif status == 'completed':
                    status_msg = f"Your order #{o['id']} is completed. Enjoy your meal!"
                elif status == 'rejected' or status == 'cancelled':
                    status_msg = f"Sorry, your order #{o['id']} was cancelled."
                
                if status_msg:
                    notifications.append({
                        "id": f"order_{o['id']}_{status}",
                        "type": "order",
                        "order_id": o['id'],
                        "status": status,
                        "title": f"Order #{o['id']} Update",
                        "message": status_msg,
                        "timestamp": "now"
                    })
                    
        return jsonify({"success": True, "notifications": notifications})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def run_server(host='0.0.0.0', port=5000):
    # Disable flask output to avoid cluttering terminal
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    try:
        from pyngrok import ngrok
        import os
        public_url = ngrok.connect(port).public_url
        print(f"Ngrok Tunnel URL: {public_url}")
        with open('ngrok_url.txt', 'w') as f:
            f.write(public_url)
    except Exception as e:
        print(f"Ngrok failed to start: {e}")
        
    app.run(host=host, port=port, debug=False, use_reloader=False)

class FlaskThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        
    def run(self):
        run_server()
