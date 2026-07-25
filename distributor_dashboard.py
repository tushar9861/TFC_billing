import sys
import os
import random
import string
import datetime
import sqlite3
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

try:
    from firestore_rest import firestore as db
except ImportError:
    db = None

# ─────────────────────────────────────────────
#  PRESET SQL QUERIES
# ─────────────────────────────────────────────
PRESET_QUERIES = [
    ("Today's Total Sales", "SELECT SUM(total_amount) AS today_sales FROM global_bills WHERE DATE(created_at) = DATE('now');"),
    ("Top 10 Selling Items", "SELECT item_name, SUM(quantity) AS total_qty FROM global_bill_items GROUP BY item_name ORDER BY total_qty DESC LIMIT 10;"),
    ("Revenue by Shop", "SELECT shop_id, shop_name, SUM(total_amount) AS revenue FROM global_bills GROUP BY shop_id ORDER BY revenue DESC;"),
    ("Monthly Revenue Trend", "SELECT strftime('%Y-%m', created_at) AS month, SUM(total_amount) AS revenue FROM global_bills GROUP BY month ORDER BY month DESC;"),
    ("Active Shops (Last 7 Days)", "SELECT DISTINCT shop_id, shop_name FROM global_bills WHERE created_at >= datetime('now', '-7 days');"),
    ("License Key Usage", "SELECT license_key, email, used_at, used_by_shop FROM license_keys WHERE is_used = 1 ORDER BY used_at DESC;"),
    ("Unused License Keys", "SELECT license_key, email_intended, created_at FROM license_keys WHERE is_used = 0 OR is_used IS NULL;"),
    ("All Registered Shops", "SELECT shop_id, shop_name, city, region, created_at FROM registered_shops ORDER BY created_at DESC;"),
    ("Refunds Overview", "SELECT shop_id, COUNT(*) AS refund_count, SUM(amount) AS total_refunded FROM global_refunds GROUP BY shop_id;"),
    ("Average Bill Value by Shop", "SELECT shop_id, shop_name, ROUND(AVG(total_amount), 2) AS avg_bill FROM global_bills GROUP BY shop_id ORDER BY avg_bill DESC;"),
]

# ─────────────────────────────────────────────
#  REAL-TIME DATA FETCHER
# ─────────────────────────────────────────────
class DataFetcherThread(QThread):
    data_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def run(self):
        import time
        while True:
            try:
                if db:
                    licenses = list(db.collection('license_keys').stream())
                    shops = list(db.collection('registered_shops').stream())

                    lic_data = [d.to_dict() for d in licenses]
                    shop_data = [d.to_dict() for d in shops]

                    # Build distributor map from license keys (distributor_id field)
                    distributor_ids = set()
                    for lic in lic_data:
                        did = lic.get('distributor_id', '')
                        if did and did != 'direct':
                            distributor_ids.add(did)

                    # Group shops under their distributor
                    distributor_shops = {}
                    direct_shops = []
                    for s in shop_data:
                        did = s.get('distributor_id', 'direct')
                        if did and did != 'direct':
                            distributor_shops.setdefault(did, []).append(s)
                        else:
                            direct_shops.append(s)

                    self.data_ready.emit({
                        'licenses': lic_data,
                        'shops': shop_data,
                        'distributor_ids': list(distributor_ids),
                        'distributor_shops': distributor_shops,
                        'direct_shops': direct_shops,
                    })
            except Exception as e:
                self.error_occurred.emit(str(e))
            time.sleep(8)

# ─────────────────────────────────────────────
#  DISTRIBUTOR DETAIL MODAL
# ─────────────────────────────────────────────
class DistributorDetailModal(QDialog):
    def __init__(self, distributor_id, shops, licenses, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Distributor: {distributor_id}")
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setMinimumSize(900, 650)
        self.setStyleSheet("""
            QDialog {
                background-color: #0D1321;
                color: white;
                font-family: 'Segoe UI';
            }
            QLabel { color: white; }
            QTableWidget {
                background: #161d2e;
                color: white;
                border: 1px solid #2a3450;
                gridline-color: #2a3450;
                font-size: 12pt;
            }
            QHeaderView::section {
                background: #1e2a45;
                color: #00D26A;
                padding: 10px;
                border: 1px solid #2a3450;
                font-size: 12pt;
                font-weight: bold;
            }
            QTabWidget::pane { border: 1px solid #2a3450; }
            QTabBar::tab {
                background: #1a2235;
                color: #aaa;
                padding: 12px 24px;
                font-size: 12pt;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected { background: #00D26A; color: #000; font-weight: bold; }
        """)
        self.distributor_id = distributor_id
        self.shops = shops
        self.licenses = licenses
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        hdr = QLabel(f"📦 Distributor ID: {self.distributor_id}")
        hdr.setStyleSheet("font-size: 22pt; font-weight: bold; color: #00D26A;")
        layout.addWidget(hdr)

        # KPI row
        kpi_row = QHBoxLayout()
        shop_count = len(self.shops)
        my_licenses = [l for l in self.licenses if l.get('distributor_id') == self.distributor_id]
        total_vol = sum(1 for l in my_licenses if l.get('is_used'))

        for label, val, color in [
            ("Total Shops", str(shop_count), "#3b82f6"),
            ("Licenses Issued", str(len(my_licenses)), "#8b5cf6"),
            ("Licenses Used", str(total_vol), "#00D26A"),
            ("Unused Keys", str(len(my_licenses) - total_vol), "#f59e0b"),
        ]:
            card = QFrame()
            card.setStyleSheet(f"background: #1a2235; border: 1px solid {color}; border-radius: 10px;")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(20, 15, 20, 15)
            v = QLabel(val)
            v.setStyleSheet(f"color: {color}; font-size: 26pt; font-weight: bold;")
            t = QLabel(label)
            t.setStyleSheet("color: #aaa; font-size: 11pt;")
            cl.addWidget(v)
            cl.addWidget(t)
            kpi_row.addWidget(card)
        layout.addLayout(kpi_row)

        # Tab widget
        tabs = QTabWidget()

        # Shops tab
        shops_tab = QWidget()
        stl = QVBoxLayout(shops_tab)
        shop_table = QTableWidget(0, 6)
        shop_table.setHorizontalHeaderLabels(["Shop Name", "Email", "City", "Region", "Address", "Registered"])
        shop_table.horizontalHeader().setStretchLastSection(True)
        shop_table.setAlternatingRowColors(True)
        shop_table.setSelectionBehavior(QTableWidget.SelectRows)
        for s in self.shops:
            r = shop_table.rowCount()
            shop_table.insertRow(r)
            shop_table.setItem(r, 0, QTableWidgetItem(s.get('shop_name', 'N/A')))
            shop_table.setItem(r, 1, QTableWidgetItem(s.get('email', 'N/A')))
            shop_table.setItem(r, 2, QTableWidgetItem(s.get('city', 'N/A')))
            shop_table.setItem(r, 3, QTableWidgetItem(s.get('region', 'N/A')))
            shop_table.setItem(r, 4, QTableWidgetItem(s.get('business_address', 'N/A')))
            created = s.get('created_at', '')[:10] if s.get('created_at') else 'N/A'
            shop_table.setItem(r, 5, QTableWidgetItem(created))
        stl.addWidget(shop_table)
        tabs.addTab(shops_tab, "🏪 Shops")

        # Licenses tab
        lic_tab = QWidget()
        ltl = QVBoxLayout(lic_tab)
        lic_table = QTableWidget(0, 5)
        lic_table.setHorizontalHeaderLabels(["License Key", "Intended Email", "Used", "Used By Shop", "Issued At"])
        lic_table.horizontalHeader().setStretchLastSection(True)
        lic_table.setAlternatingRowColors(True)
        for l in self.licenses:
            if l.get('distributor_id') != self.distributor_id:
                continue
            r = lic_table.rowCount()
            lic_table.insertRow(r)
            lic_table.setItem(r, 0, QTableWidgetItem(l.get('id', l.get('license_key', 'N/A'))))
            lic_table.setItem(r, 1, QTableWidgetItem(l.get('email_intended', l.get('email', 'N/A'))))
            used = "✅ Yes" if l.get('is_used') else "⬜ No"
            lic_table.setItem(r, 2, QTableWidgetItem(used))
            lic_table.setItem(r, 3, QTableWidgetItem(l.get('used_by_shop', 'N/A')))
            claimed = l.get('claimed_at', l.get('used_at', ''))[:10] if l.get('claimed_at') or l.get('used_at') else 'N/A'
            lic_table.setItem(r, 4, QTableWidgetItem(claimed))
        ltl.addWidget(lic_table)
        tabs.addTab(lic_tab, "🔑 Licenses")

        layout.addWidget(tabs)

        btn_close = QPushButton("Close")
        btn_close.setStyleSheet("background: #2a3450; color: white; padding: 12px 30px; font-size: 13pt; border-radius: 6px;")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignRight)

# ─────────────────────────────────────────────
#  SQL TERMINAL
# ─────────────────────────────────────────────
class SQLTerminal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._query_library = list(PRESET_QUERIES)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("💻 SQL Data Explorer")
        title.setStyleSheet("color: white; font-size: 20pt; font-weight: bold;")
        layout.addWidget(title)

        # Preset selector row
        preset_row = QHBoxLayout()
        lbl = QLabel("Preset Queries:")
        lbl.setStyleSheet("color: #aaa; font-size: 13pt;")
        self.preset_combo = QComboBox()
        self.preset_combo.setStyleSheet("background: #1a2235; color: white; font-size: 12pt; padding: 6px; border: 1px solid #2a3450;")
        self._populate_presets()
        self.preset_combo.currentIndexChanged.connect(self._load_preset)

        btn_add = QPushButton("➕ Save to Library")
        btn_add.setStyleSheet("background: #0f3460; color: white; padding: 8px 16px; font-size: 12pt; border-radius: 5px;")
        btn_add.clicked.connect(self._save_to_library)

        preset_row.addWidget(lbl)
        preset_row.addWidget(self.preset_combo, stretch=1)
        preset_row.addWidget(btn_add)
        layout.addLayout(preset_row)

        # SQL Editor
        self.editor = QTextEdit()
        self.editor.setStyleSheet("background: #0d1117; color: #58a6ff; font-family: Consolas, monospace; font-size: 14pt; border: 1px solid #30363d; border-radius: 6px;")
        self.editor.setPlaceholderText("SELECT * FROM global_bills LIMIT 10;")
        self.editor.setFixedHeight(160)
        layout.addWidget(self.editor)

        btn_row = QHBoxLayout()
        btn_run = QPushButton("▶  Run Query")
        btn_run.setStyleSheet("background-color: #238636; color: white; padding: 12px 24px; font-weight: bold; font-size: 13pt; border-radius: 6px;")
        btn_run.clicked.connect(self.run_query)
        self.status_lbl = QLabel("Ready.")
        self.status_lbl.setStyleSheet("color: #aaa; font-size: 12pt;")
        btn_row.addWidget(self.status_lbl)
        btn_row.addStretch()
        btn_row.addWidget(btn_run)
        layout.addLayout(btn_row)

        # Result table
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget { background: #161b22; color: #c9d1d9; border: none; font-size: 12pt; }
            QHeaderView::section { background: #21262d; color: #00D26A; padding: 8px; border: 1px solid #30363d; font-size: 12pt; font-weight: bold; }
            QTableWidget::item:alternate { background: #1c2128; }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def _populate_presets(self):
        self.preset_combo.clear()
        self.preset_combo.addItem("-- Select a preset query --")
        for name, _ in self._query_library:
            self.preset_combo.addItem(name)

    def _load_preset(self, index):
        if index <= 0:
            return
        _, sql = self._query_library[index - 1]
        self.editor.setPlainText(sql)

    def _save_to_library(self):
        sql = self.editor.toPlainText().strip()
        if not sql:
            QMessageBox.warning(self, "Empty Query", "Write a query first before saving.")
            return
        name, ok = QInputDialog.getText(self, "Save Query", "Enter a name for this query:")
        if ok and name.strip():
            self._query_library.append((name.strip(), sql))
            self._populate_presets()
            QMessageBox.information(self, "Saved", f"Query '{name}' added to library.")

    def run_query(self):
        query = self.editor.toPlainText().strip()
        if not query:
            return
        self.status_lbl.setText("Running...")
        QApplication.processEvents()
        try:
            conn = sqlite3.connect(":memory:")
            # Build mock tables for demonstration
            self._seed_mock_data(conn)
            cur = conn.execute(query)
            cols = [desc[0] for desc in cur.description] if cur.description else []
            rows = cur.fetchall()
            conn.close()

            self.table.setRowCount(0)
            self.table.setColumnCount(len(cols))
            self.table.setHorizontalHeaderLabels(cols)
            for row in rows:
                r = self.table.rowCount()
                self.table.insertRow(r)
                for c, val in enumerate(row):
                    self.table.setItem(r, c, QTableWidgetItem(str(val) if val is not None else "NULL"))
            self.status_lbl.setText(f"✅ {len(rows)} rows returned.")
        except Exception as e:
            self.status_lbl.setText(f"❌ Error: {str(e)[:80]}")
            self.table.setRowCount(0)

    def _seed_mock_data(self, conn):
        conn.execute("""CREATE TABLE IF NOT EXISTS global_bills (
            id TEXT, shop_id TEXT, shop_name TEXT, total_amount REAL, created_at TEXT)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS global_bill_items (
            id TEXT, shop_id TEXT, item_name TEXT, quantity INTEGER, price REAL, created_at TEXT)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS registered_shops (
            shop_id TEXT, shop_name TEXT, city TEXT, region TEXT, created_at TEXT)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS license_keys (
            license_key TEXT, email_intended TEXT, is_used INTEGER, used_by_shop TEXT, claimed_at TEXT, used_at TEXT, created_at TEXT)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS global_refunds (
            id TEXT, shop_id TEXT, amount REAL, created_at TEXT)""")
        conn.commit()

# ─────────────────────────────────────────────
#  MODERN KPI CARD
# ─────────────────────────────────────────────
class KPICard(QFrame):
    def __init__(self, title, value, icon, color, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255,255,255,0.06), stop:1 rgba(255,255,255,0.02));
                border: 1px solid {color}55;
                border-radius: 14px;
            }}
            QFrame:hover {{
                border: 1px solid {color};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255,255,255,0.1), stop:1 rgba(255,255,255,0.04));
            }}
        """)
        self.setMinimumHeight(130)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)

        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"color: {color}; font-size: 26pt; background: transparent; border: none;")
        top.addWidget(icon_lbl)
        top.addStretch()
        layout.addLayout(top)

        t = QLabel(title)
        t.setStyleSheet("color: #9ca3af; font-size: 13pt; background: transparent; border: none;")
        layout.addWidget(t)

        self.val_lbl = QLabel(str(value))
        self.val_lbl.setStyleSheet(f"color: white; font-size: 28pt; font-weight: bold; background: transparent; border: none;")
        layout.addWidget(self.val_lbl)

# ─────────────────────────────────────────────
#  MAIN DASHBOARD
# ─────────────────────────────────────────────
class DistributorDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Distributor's Admin Dashboard — AdminOS")
        self._all_data = {}

        screen = QApplication.primaryScreen().geometry()
        w = int(screen.width() * 0.82)
        h = int(screen.height() * 0.84)
        self.resize(w, h)
        self.move((screen.width() - w) // 2, (screen.height() - h) // 2)
        self.setStyleSheet("background-color: #0A0F1E; color: white; font-family: 'Segoe UI';")
        self._init_ui()
        self._start_fetcher()

    # ── UI SKELETON ──────────────────────────
    def _init_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_sidebar())
        layout.addWidget(self._build_content())

    def _build_sidebar(self):
        sb = QWidget()
        sb.setFixedWidth(260)
        sb.setStyleSheet("background-color: #0E1628; border-right: 1px solid #1e2a45;")
        sl = QVBoxLayout(sb)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(0)

        logo_area = QWidget()
        logo_area.setStyleSheet("background: #0a1020; padding: 0;")
        la = QVBoxLayout(logo_area)
        la.setContentsMargins(24, 24, 24, 24)
        logo = QLabel("AdminOS")
        logo.setStyleSheet("font-size: 22pt; font-weight: bold; color: #00D26A;")
        sub = QLabel("Distributor Dashboard")
        sub.setStyleSheet("font-size: 10pt; color: #4a5568;")
        la.addWidget(logo)
        la.addWidget(sub)
        sl.addWidget(logo_area)

        self.nav = QListWidget()
        self.nav.setStyleSheet("""
            QListWidget { border: none; background: transparent; outline: none; padding: 8px 0; }
            QListWidget::item {
                color: #9ca3af; padding: 16px 28px; font-size: 14pt;
                border-left: 4px solid transparent; margin: 2px 0;
            }
            QListWidget::item:hover { background: rgba(255,255,255,0.04); color: #e5e7eb; }
            QListWidget::item:selected {
                background: rgba(0,210,106,0.1); color: #00D26A;
                border-left: 4px solid #00D26A;
            }
        """)
        for item in ["📊  Overview", "🌐  Network Tree", "🔑  License Manager", "🏪  Shops Monitor", "💻  SQL Explorer", "🚀  Update Manager"]:
            self.nav.addItem(item)
        self.nav.setCurrentRow(0)
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex if hasattr(self, 'stack') else lambda i: None)
        sl.addWidget(self.nav)
        sl.addStretch()

        self.sync_status = QLabel("⏳ Syncing...")
        self.sync_status.setStyleSheet("color: #4a5568; font-size: 10pt; padding: 12px 24px;")
        sl.addWidget(self.sync_status)
        return sb

    def _build_content(self):
        self.stack = QStackedWidget()
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.stack.setStyleSheet("background: transparent;")
        self._build_overview()
        self._build_tree_tab()
        self._build_license_tab()
        self._build_shops_tab()
        self._build_sql_tab()
        self._build_updater_tab()
        return self.stack

    # ── TAB BUILDERS ─────────────────────────
    def _build_overview(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 40)
        l.setSpacing(24)

        hdr = QLabel("Platform Overview")
        hdr.setStyleSheet("font-size: 26pt; font-weight: bold;")
        l.addWidget(hdr)

        cards = QHBoxLayout()
        cards.setSpacing(20)
        self.card_shops = KPICard("Active Shops", "—", "🏪", "#3b82f6")
        self.card_licenses = KPICard("Licenses Issued", "—", "🔑", "#8b5cf6")
        self.card_used = KPICard("Licenses Used", "—", "✅", "#00D26A")
        self.card_dists = KPICard("Distributors", "—", "👥", "#f59e0b")
        for c in [self.card_shops, self.card_licenses, self.card_used, self.card_dists]:
            cards.addWidget(c)
        l.addLayout(cards)

        # Recent shops preview
        preview_lbl = QLabel("Recently Registered Shops")
        preview_lbl.setStyleSheet("font-size: 16pt; font-weight: bold; margin-top: 20px;")
        l.addWidget(preview_lbl)

        self.recent_table = QTableWidget(0, 4)
        self.recent_table.setHorizontalHeaderLabels(["Shop Name", "City", "Region", "Registered"])
        self.recent_table.setStyleSheet("""
            QTableWidget { background: #0e1628; color: white; border: 1px solid #1e2a45; font-size: 13pt; }
            QHeaderView::section { background: #1e2a45; color: #00D26A; padding: 10px; font-size: 13pt; font-weight: bold; }
        """)
        self.recent_table.horizontalHeader().setStretchLastSection(True)
        self.recent_table.setAlternatingRowColors(True)
        self.recent_table.setMinimumHeight(200)
        l.addWidget(self.recent_table)
        l.addStretch()
        self.stack.addWidget(w)

    def _build_tree_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 40)
        l.setSpacing(16)

        hdr = QLabel("📡 Distributor Network Tree")
        hdr.setStyleSheet("font-size: 26pt; font-weight: bold;")
        l.addWidget(hdr)

        info = QLabel("Click any distributor or shop node to view full details.")
        info.setStyleSheet("color: #6b7280; font-size: 13pt;")
        l.addWidget(info)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(["Name / ID", "Role", "Region / City", "Info"])
        self.tree.setStyleSheet("""
            QTreeWidget {
                background: #0e1628;
                color: white;
                border: 1px solid #1e2a45;
                font-size: 14pt;
            }
            QTreeWidget::item { padding: 10px 8px; border-bottom: 1px solid #1e2a45; }
            QTreeWidget::item:hover { background: #1a2540; }
            QTreeWidget::item:selected { background: rgba(0,210,106,0.15); color: #00D26A; }
            QHeaderView::section {
                background: #1a2235; color: #00D26A; padding: 10px;
                font-size: 14pt; font-weight: bold; border: 1px solid #2a3450;
            }
        """)
        self.tree.header().setStretchLastSection(True)
        self.tree.itemDoubleClicked.connect(self._on_tree_double_click)
        l.addWidget(self.tree)

        hint = QLabel("💡 Double-click a distributor to open their full dashboard")
        hint.setStyleSheet("color: #4a5568; font-size: 12pt;")
        l.addWidget(hint)
        self.stack.addWidget(w)

    def _build_license_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 40)
        l.setSpacing(20)

        hdr = QLabel("🔑 License Generator")
        hdr.setStyleSheet("font-size: 26pt; font-weight: bold;")
        l.addWidget(hdr)

        form_card = QFrame()
        form_card.setStyleSheet("background: #0e1628; border: 1px solid #1e2a45; border-radius: 12px;")
        fc_layout = QVBoxLayout(form_card)
        fc_layout.setContentsMargins(30, 30, 30, 30)
        fc_layout.setSpacing(18)

        field_style = "background: #1a2235; color: white; padding: 12px; border: 1px solid #2a3450; border-radius: 6px; font-size: 14pt;"
        label_style = "color: #9ca3af; font-size: 13pt;"

        fc_layout.addWidget(self._lbl("Intended Email (who will use this key)", label_style))
        self.lic_email = QLineEdit()
        self.lic_email.setStyleSheet(field_style)
        self.lic_email.setPlaceholderText("e.g. shopowner@email.com")
        fc_layout.addWidget(self.lic_email)

        fc_layout.addWidget(self._lbl("Package Type", label_style))
        self.lic_pkg = QComboBox()
        self.lic_pkg.addItems(["Basic", "Pro", "Enterprise", "Trial"])
        self.lic_pkg.setStyleSheet(field_style)
        fc_layout.addWidget(self.lic_pkg)

        fc_layout.addWidget(self._lbl("Assign to Distributor ID (leave blank for direct)", label_style))
        self.lic_dist = QLineEdit()
        self.lic_dist.setStyleSheet(field_style)
        self.lic_dist.setPlaceholderText("Distributor ID or blank for direct")
        fc_layout.addWidget(self.lic_dist)

        btn_gen = QPushButton("⚡ Generate & Save License Key")
        btn_gen.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #00D26A, stop:1 #00a854);
                color: #000; padding: 16px; font-weight: bold; font-size: 16pt;
                border-radius: 8px; border: none;
            }
            QPushButton:hover { background: #00e075; }
            QPushButton:pressed { background: #009944; }
        """)
        btn_gen.clicked.connect(self._generate_license)
        fc_layout.addWidget(btn_gen)

        self.gen_result = QLabel("")
        self.gen_result.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px;")
        self.gen_result.setWordWrap(True)
        fc_layout.addWidget(self.gen_result)

        l.addWidget(form_card)

        # License list
        l.addWidget(self._lbl("All Generated Licenses", "font-size: 16pt; font-weight: bold; margin-top: 10px;"))
        self.lic_table = QTableWidget(0, 6)
        self.lic_table.setHorizontalHeaderLabels(["License Key", "Email", "Package", "Distributor", "Used", "Date"])
        self.lic_table.setStyleSheet("""
            QTableWidget { background: #0e1628; color: white; border: 1px solid #1e2a45; font-size: 13pt; }
            QHeaderView::section { background: #1e2a45; color: #00D26A; padding: 10px; font-size: 13pt; font-weight: bold; }
        """)
        self.lic_table.horizontalHeader().setStretchLastSection(True)
        self.lic_table.setAlternatingRowColors(True)
        l.addWidget(self.lic_table)
        self.stack.addWidget(w)

    def _build_shops_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 40)
        l.setSpacing(16)

        hdr = QLabel("🏪 All Shops Monitor")
        hdr.setStyleSheet("font-size: 26pt; font-weight: bold;")
        l.addWidget(hdr)

        self.shop_table = QTableWidget(0, 7)
        self.shop_table.setHorizontalHeaderLabels(["Shop Name", "Email", "City", "Region", "Address", "Distributor", "Registered"])
        self.shop_table.setStyleSheet("""
            QTableWidget { background: #0e1628; color: white; border: 1px solid #1e2a45; font-size: 13pt; }
            QHeaderView::section { background: #1e2a45; color: #00D26A; padding: 10px; font-size: 13pt; font-weight: bold; }
        """)
        self.shop_table.horizontalHeader().setStretchLastSection(True)
        self.shop_table.setAlternatingRowColors(True)
        l.addWidget(self.shop_table)
        self.stack.addWidget(w)

    def _build_updater_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 40)
        l.setSpacing(24)

        header = QLabel("Publish App Update")
        header.setStyleSheet("font-size: 24pt; font-weight: bold; color: #111827;")
        l.addWidget(header)

        desc = QLabel("Publish a new version of SmartPOS by pasting the exact URL to the compiled .exe file.\nAll clients will receive this update silently.")
        desc.setStyleSheet("color: #6b7280; font-size: 11pt;")
        desc.setWordWrap(True)
        l.addWidget(desc)

        form = QFormLayout()
        form.setSpacing(20)
        form.setVerticalSpacing(20)

        self.upd_version_input = QLineEdit()
        self.upd_version_input.setPlaceholderText("e.g. 1.2.5")
        form.addRow("New Version:", self.upd_version_input)

        self.upd_url_input = QLineEdit()
        self.upd_url_input.setPlaceholderText("https://github.com/tushar9861/TFC_billing/releases/download/.../SmartPOS.exe")
        form.addRow("Download URL:", self.upd_url_input)

        l.addLayout(form)

        btn = QPushButton("Publish Update")
        btn.setStyleSheet("""
            QPushButton {
                background: #00D26A; color: white; font-weight: bold; font-size: 12pt;
                padding: 12px 24px; border-radius: 8px; border: none;
            }
            QPushButton:hover { background: #00b35a; }
        """)
        btn.setFixedWidth(200)
        btn.clicked.connect(self._publish_update)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn)
        btn_layout.addStretch()
        l.addLayout(btn_layout)
        l.addStretch()
        self.stack.addWidget(w)
        
    def _publish_update(self):
        v = self.upd_version_input.text().strip()
        u = self.upd_url_input.text().strip()
        if not v or not u:
            QMessageBox.warning(self, "Error", "Both fields are required!")
            return
            
        reply = QMessageBox.question(self, "Confirm Publish", f"Are you sure you want to push version {v} to all clients?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                import firebase_admin
                from firebase_admin import firestore
                db = firestore.client()
                db.collection("app_config").document("updater").set({
                    "latest_version": v,
                    "download_url": u
                }, merge=True)
                QMessageBox.information(self, "Success", "Update published successfully!")
                self.upd_version_input.clear()
                self.upd_url_input.clear()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to publish: {e}")

    def _build_sql_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 40)
        terminal = SQLTerminal()
        l.addWidget(terminal)
        self.stack.addWidget(w)

    # ── HELPERS ──────────────────────────────
    def _lbl(self, text, style):
        lbl = QLabel(text)
        lbl.setStyleSheet(style)
        return lbl

    # ── REAL-TIME FETCHER ─────────────────────
    def _start_fetcher(self):
        self.fetcher = DataFetcherThread()
        self.fetcher.data_ready.connect(self._on_data)
        self.fetcher.error_occurred.connect(lambda e: self.sync_status.setText(f"⚠️ Sync error: {e[:40]}"))
        self.fetcher.start()

    def _on_data(self, data):
        self._all_data = data
        licenses = data.get('licenses', [])
        shops = data.get('shops', [])
        dists = data.get('distributor_ids', [])
        used = [l for l in licenses if l.get('is_used')]

        # KPI cards
        self.card_shops.val_lbl.setText(str(len(shops)))
        self.card_licenses.val_lbl.setText(str(len(licenses)))
        self.card_used.val_lbl.setText(str(len(used)))
        self.card_dists.val_lbl.setText(str(max(1, len(dists))))

        # Recent shops
        self.recent_table.setRowCount(0)
        sorted_shops = sorted(shops, key=lambda s: s.get('created_at', ''), reverse=True)
        for s in sorted_shops[:10]:
            r = self.recent_table.rowCount()
            self.recent_table.insertRow(r)
            self.recent_table.setItem(r, 0, QTableWidgetItem(s.get('shop_name', 'N/A')))
            self.recent_table.setItem(r, 1, QTableWidgetItem(s.get('city', 'N/A')))
            self.recent_table.setItem(r, 2, QTableWidgetItem(s.get('region', 'N/A')))
            created = s.get('created_at', '')[:10] if s.get('created_at') else 'N/A'
            self.recent_table.setItem(r, 3, QTableWidgetItem(created))

        # Network tree
        self._rebuild_tree(data)

        # License table
        self.lic_table.setRowCount(0)
        for lic in licenses:
            r = self.lic_table.rowCount()
            self.lic_table.insertRow(r)
            self.lic_table.setItem(r, 0, QTableWidgetItem(lic.get('id', lic.get('license_key', 'N/A'))))
            self.lic_table.setItem(r, 1, QTableWidgetItem(lic.get('email_intended', lic.get('email', 'N/A'))))
            self.lic_table.setItem(r, 2, QTableWidgetItem(lic.get('package_type', 'N/A')))
            self.lic_table.setItem(r, 3, QTableWidgetItem(lic.get('distributor_id', 'direct')))
            used_v = "✅ Yes" if lic.get('is_used') else "⬜ No"
            self.lic_table.setItem(r, 4, QTableWidgetItem(used_v))
            claimed = lic.get('claimed_at', lic.get('used_at', lic.get('created_at', '')))
            self.lic_table.setItem(r, 5, QTableWidgetItem(claimed[:10] if claimed else 'N/A'))

        # Shops monitor
        self.shop_table.setRowCount(0)
        for s in sorted_shops:
            r = self.shop_table.rowCount()
            self.shop_table.insertRow(r)
            self.shop_table.setItem(r, 0, QTableWidgetItem(s.get('shop_name', 'N/A')))
            self.shop_table.setItem(r, 1, QTableWidgetItem(s.get('email', 'N/A')))
            self.shop_table.setItem(r, 2, QTableWidgetItem(s.get('city', 'N/A')))
            self.shop_table.setItem(r, 3, QTableWidgetItem(s.get('region', 'N/A')))
            self.shop_table.setItem(r, 4, QTableWidgetItem(s.get('business_address', 'N/A')))
            self.shop_table.setItem(r, 5, QTableWidgetItem(s.get('distributor_id', 'direct')))
            created = s.get('created_at', '')[:10] if s.get('created_at') else 'N/A'
            self.shop_table.setItem(r, 6, QTableWidgetItem(created))

        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.sync_status.setText(f"🟢 Live — {now}")

    def _rebuild_tree(self, data):
        self.tree.clear()
        shops = data.get('shops', [])
        dists = data.get('distributor_ids', [])
        dist_shops = data.get('distributor_shops', {})
        direct_shops = data.get('direct_shops', [])

        # Root: Master Owner
        root = QTreeWidgetItem(self.tree)
        root.setText(0, "👑  Master Owner (You)")
        root.setText(1, "Owner")
        root.setText(2, "Global")
        root.setText(3, f"{len(shops)} shops total")
        root.setForeground(0, QBrush(QColor("#00D26A")))
        font = QFont("Segoe UI", 13, QFont.Bold)
        root.setFont(0, font)

        # Distributor nodes
        for dist_id in dists:
            d_shops = dist_shops.get(dist_id, [])
            d_node = QTreeWidgetItem(root)
            d_node.setText(0, f"📦  {dist_id}")
            d_node.setText(1, "Distributor")
            regions = set(s.get('region', '') for s in d_shops if s.get('region'))
            d_node.setText(2, ", ".join(list(regions)[:2]) or "N/A")
            d_node.setText(3, f"{len(d_shops)} shops")
            d_node.setForeground(0, QBrush(QColor("#f59e0b")))
            d_node.setFont(0, QFont("Segoe UI", 13))
            d_node.setData(0, Qt.UserRole, {"type": "distributor", "id": dist_id})

            for s in d_shops:
                s_node = QTreeWidgetItem(d_node)
                s_node.setText(0, f"🏪  {s.get('shop_name', s.get('shop_id', 'Unknown'))}")
                s_node.setText(1, "Shop")
                s_node.setText(2, f"{s.get('city', '')} {s.get('region', '')}".strip() or "N/A")
                s_node.setText(3, s.get('email', 'N/A'))
                s_node.setFont(0, QFont("Segoe UI", 12))

        # Direct shops (no distributor)
        if direct_shops:
            direct_node = QTreeWidgetItem(root)
            direct_node.setText(0, "📋  Direct Registrations")
            direct_node.setText(1, "Group")
            direct_node.setText(2, "Various")
            direct_node.setText(3, f"{len(direct_shops)} shops")
            direct_node.setForeground(0, QBrush(QColor("#3b82f6")))
            direct_node.setFont(0, QFont("Segoe UI", 13))
            for s in direct_shops:
                s_node = QTreeWidgetItem(direct_node)
                s_node.setText(0, f"🏪  {s.get('shop_name', 'Unknown')}")
                s_node.setText(1, "Shop")
                s_node.setText(2, f"{s.get('city', '')} {s.get('region', '')}".strip() or "N/A")
                s_node.setText(3, s.get('email', 'N/A'))

        self.tree.expandAll()
        for i in range(4):
            self.tree.resizeColumnToContents(i)

    def _on_tree_double_click(self, item, col):
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        if data.get('type') == 'distributor':
            dist_id = data['id']
            dist_shops = self._all_data.get('distributor_shops', {}).get(dist_id, [])
            licenses = self._all_data.get('licenses', [])
            modal = DistributorDetailModal(dist_id, dist_shops, licenses, self)
            modal.exec_()

    # ── LICENSE GENERATION ────────────────────
    def _generate_license(self):
        email = self.lic_email.text().strip()
        pkg = self.lic_pkg.currentText()
        dist_id = self.lic_dist.text().strip()

        if not email:
            self.gen_result.setText("❌ Please enter an intended email.")
            self.gen_result.setStyleSheet("color: #ef4444; font-size: 14pt; font-weight: bold;")
            return

        # Generate secure key
        key_parts = [
            ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            for _ in range(4)
        ]
        license_key = '-'.join(key_parts)
        now = datetime.datetime.now().isoformat()

        payload = {
            "license_key": license_key,
            "email_intended": email,
            "package_type": pkg,
            "distributor_id": dist_id if dist_id else "direct",
            "is_used": False,
            "created_at": now
        }

        success = False
        last_error = ""

        # Strategy 1: Firebase Admin SDK (serviceAccountKey.json) - bypasses rules, most reliable
        try:
            from firebase_admin_write import write_license_key
            write_license_key(license_key, payload)
            success = True
        except Exception as e1:
            last_error = f"Admin SDK: {str(e1)[:120]}"

        # Strategy 2: REST API with user auth token
        if not success and db:
            try:
                db.set_document(f"license_keys/{license_key}", payload)
                success = True
            except Exception as e2:
                if hasattr(e2, 'response'):
                    last_error += f" | REST: HTTP {e2.response.status_code} {e2.response.text[:120]}"
                else:
                    last_error += f" | REST: {str(e2)[:120]}"

        # Strategy 3: REST API without auth token (open rules)
        if not success and db:
            saved_token = db.id_token
            db.id_token = None
            try:
                db.set_document(f"license_keys/{license_key}", payload)
                success = True
            except Exception as e3:
                if hasattr(e3, 'response'):
                    last_error += f" | Open: HTTP {e3.response.status_code}"
                else:
                    last_error += f" | Open: {str(e3)[:60]}"
            finally:
                db.id_token = saved_token

        QApplication.clipboard().setText(license_key)

        if success:
            self.gen_result.setText(
                f"License Key Generated & Saved!\n\n"
                f"Key: {license_key}\n"
                f"Email: {email}\n"
                f"Package: {pkg}\n"
                f"Distributor: {dist_id or 'direct'}\n\n"
                f"Key copied to clipboard. Share it with the client."
            )
            self.gen_result.setStyleSheet("color: #00D26A; font-size: 14pt; font-weight: bold;")
        else:
            self.gen_result.setText(
                f"CLOUD SAVE FAILED - Key is copied to clipboard.\n\n"
                f"Key: {license_key}\n\n"
                f"Manually add it to Firebase or check Firestore rules.\n\n"
                f"Errors tried:\n{last_error}"
            )
            self.gen_result.setStyleSheet("color: #ef4444; font-size: 12pt;")


# ─────────────────────────────────────────────
#  ADMIN LOGIN DIALOG
# ─────────────────────────────────────────────
ADMIN_CREDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".admin_creds")

class AdminLoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self._is_register_mode = False
        self.setWindowTitle("AdminOS — Owner Login")
        self.setFixedSize(480, 520)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #0A0F1E;
                color: white;
                font-family: 'Segoe UI';
            }
            QLabel { color: white; }
            QLineEdit {
                background: #1a2235;
                color: white;
                border: 1px solid #2a3450;
                border-radius: 8px;
                padding: 14px;
                font-size: 14pt;
            }
            QLineEdit:focus { border: 1px solid #00D26A; }
            QPushButton#mainBtn {
                background: #00D26A;
                color: #000;
                padding: 14px;
                font-size: 15pt;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }
            QPushButton#mainBtn:hover { background: #00e075; }
            QPushButton#toggleBtn {
                background: transparent;
                color: #6b7280;
                font-size: 12pt;
                border: 1px solid #2a3450;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton#toggleBtn:hover { color: #00D26A; border-color: #00D26A; }
            QCheckBox { color: #9ca3af; font-size: 12pt; }
        """)
        self._build_ui()
        self._try_auto_login()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 36, 40, 36)
        layout.setSpacing(14)

        logo = QLabel("AdminOS")
        logo.setStyleSheet("font-size: 28pt; font-weight: bold; color: #00D26A;")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        self.mode_lbl = QLabel("Owner / Distributor Sign In")
        self.mode_lbl.setStyleSheet("color: #6b7280; font-size: 13pt;")
        self.mode_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.mode_lbl)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Admin Email")
        layout.addWidget(self.email_input)

        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("Password (min 6 characters)")
        self.pwd_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pwd_input)

        self.confirm_pwd_input = QLineEdit()
        self.confirm_pwd_input.setPlaceholderText("Confirm Password")
        self.confirm_pwd_input.setEchoMode(QLineEdit.Password)
        self.confirm_pwd_input.hide()
        layout.addWidget(self.confirm_pwd_input)

        self.remember_cb = QCheckBox("Remember credentials on this device")
        layout.addWidget(self.remember_cb)

        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color: #ef4444; font-size: 12pt;")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setWordWrap(True)
        self.status_lbl.setMinimumHeight(40)
        layout.addWidget(self.status_lbl)

        self.main_btn = QPushButton("Sign In to Dashboard")
        self.main_btn.setObjectName("mainBtn")
        self.main_btn.clicked.connect(self._do_action)
        self.pwd_input.returnPressed.connect(self._do_action)
        self.confirm_pwd_input.returnPressed.connect(self._do_action)
        layout.addWidget(self.main_btn)

        sep = QLabel("───────────────  or  ───────────────")
        sep.setStyleSheet("color: #2a3450; font-size: 10pt;")
        sep.setAlignment(Qt.AlignCenter)
        layout.addWidget(sep)

        self.toggle_btn = QPushButton("First time? Create your Admin account")
        self.toggle_btn.setObjectName("toggleBtn")
        self.toggle_btn.clicked.connect(self._toggle_mode)
        layout.addWidget(self.toggle_btn)

    def _toggle_mode(self):
        self._is_register_mode = not self._is_register_mode
        self.status_lbl.setText("")
        if self._is_register_mode:
            self.mode_lbl.setText("Create Admin Account")
            self.main_btn.setText("Create Account & Sign In")
            self.toggle_btn.setText("Already have an account? Sign In")
            self.confirm_pwd_input.show()
            self.setFixedSize(480, 570)
        else:
            self.mode_lbl.setText("Owner / Distributor Sign In")
            self.main_btn.setText("Sign In to Dashboard")
            self.toggle_btn.setText("First time? Create your Admin account")
            self.confirm_pwd_input.hide()
            self.setFixedSize(480, 520)

    def _try_auto_login(self):
        if not os.path.exists(ADMIN_CREDS_FILE):
            return
        try:
            import base64
            with open(ADMIN_CREDS_FILE, 'r') as f:
                raw = f.read().strip()
            decoded = base64.b64decode(raw).decode('utf-8')
            parts = decoded.split('\n', 1)
            if len(parts) == 2:
                email, pwd = parts
                self.email_input.setText(email)
                self.pwd_input.setText(pwd)
                self.remember_cb.setChecked(True)
                self._do_login(email, pwd, silent=True)
        except Exception:
            pass

    def _do_action(self):
        email = self.email_input.text().strip()
        pwd = self.pwd_input.text()
        if not email or not pwd:
            self.status_lbl.setText("Please enter email and password.")
            return
        if self._is_register_mode:
            confirm = self.confirm_pwd_input.text()
            if pwd != confirm:
                self.status_lbl.setText("Passwords do not match.")
                self.status_lbl.setStyleSheet("color: #ef4444; font-size: 12pt;")
                return
            if len(pwd) < 6:
                self.status_lbl.setText("Password must be at least 6 characters.")
                self.status_lbl.setStyleSheet("color: #ef4444; font-size: 12pt;")
                return
            self._do_register(email, pwd)
        else:
            self._do_login(email, pwd)

    def _do_login(self, email, pwd, silent=False):
        self.status_lbl.setText("Signing in...")
        self.status_lbl.setStyleSheet("color: #6cb4ee; font-size: 12pt;")
        QApplication.processEvents()
        try:
            import requests
            db.login(email, pwd)
            self._save_creds(email, pwd)
            self.accept()
        except requests.exceptions.HTTPError as e:
            try:
                msg = e.response.json().get('error', {}).get('message', str(e))
            except Exception:
                msg = str(e)
            if any(k in msg for k in ['INVALID_LOGIN_CREDENTIALS', 'INVALID_PASSWORD', 'EMAIL_NOT_FOUND']):
                self.status_lbl.setText(
                    "Incorrect email or password.\n\nNo account yet? Click \'Create your Admin account\' below."
                )
            elif 'TOO_MANY_ATTEMPTS' in msg:
                self.status_lbl.setText("Too many attempts. Please try again later.")
            else:
                self.status_lbl.setText(f"Login error: {msg[:70]}")
            self.status_lbl.setStyleSheet("color: #ef4444; font-size: 12pt;")
            if os.path.exists(ADMIN_CREDS_FILE):
                os.remove(ADMIN_CREDS_FILE)
        except Exception as e:
            self.status_lbl.setText(f"Network error: {str(e)[:60]}")
            self.status_lbl.setStyleSheet("color: #ef4444; font-size: 12pt;")

    def _do_register(self, email, pwd):
        self.status_lbl.setText("Creating admin account...")
        self.status_lbl.setStyleSheet("color: #6cb4ee; font-size: 12pt;")
        QApplication.processEvents()
        try:
            import requests
            db.signup(email, pwd)
            self._save_creds(email, pwd)
            self.status_lbl.setText("Account created! Opening dashboard...")
            self.status_lbl.setStyleSheet("color: #00D26A; font-size: 12pt;")
            QApplication.processEvents()
            self.accept()
        except requests.exceptions.HTTPError as e:
            try:
                msg = e.response.json().get('error', {}).get('message', str(e))
            except Exception:
                msg = str(e)
            if 'EMAIL_EXISTS' in msg:
                self.status_lbl.setText("This email already has an account. Use Sign In mode.")
            elif 'WEAK_PASSWORD' in msg:
                self.status_lbl.setText("Password is too weak. Use at least 6 characters.")
            else:
                self.status_lbl.setText(f"Registration error: {msg[:70]}")
            self.status_lbl.setStyleSheet("color: #ef4444; font-size: 12pt;")
        except Exception as e:
            self.status_lbl.setText(f"Network error: {str(e)[:60]}")
            self.status_lbl.setStyleSheet("color: #ef4444; font-size: 12pt;")

    def _save_creds(self, email, pwd):
        if self.remember_cb.isChecked():
            import base64
            encoded = base64.b64encode(f"{email}\n{pwd}".encode()).decode()
            with open(ADMIN_CREDS_FILE, 'w') as f:
                f.write(encoded)
        elif os.path.exists(ADMIN_CREDS_FILE):
            os.remove(ADMIN_CREDS_FILE)


# ─────────────────────────────────────────────
#  ENTRY POINT

# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 12))

    if db:
        login_dlg = AdminLoginDialog()
        if login_dlg.result() != QDialog.Accepted:
            # Not auto-logged in, show dialog manually
            if login_dlg.exec_() != QDialog.Accepted:
                sys.exit(0)
    
    window = DistributorDashboard()
    window.show()
    sys.exit(app.exec_())
