import sys
from pymongo import MongoClient
from bson.objectid import ObjectId
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QDialog, QFormLayout, QFrame, QSpacerItem, QSizePolicy, QComboBox, QToolButton, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor, QPixmap

# --- MongoDB Connection ---
import os
from urllib.parse import quote_plus

def read_mongo_uri():
    config_path = os.path.join(os.path.dirname(__file__), 'config.txt')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            for line in f:
                if line.startswith('MONGO_URI='):
                    return line.strip().split('=', 1)[1].strip()
    # Default fallback
    return 'mongodb://localhost:27017/'

try:
    MONGO_URI = read_mongo_uri()
    MONGO_DB = 'inventory_app'
    
    # Test the connection
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  # Test the connection
    db = client[MONGO_DB]
    print("✅ Successfully connected to MongoDB!")
except Exception as e:
    print(f"❌ Error connecting to MongoDB: {e}")
    print("Falling back to local database...")
    client = MongoClient('mongodb://localhost:27017/')
    db = client['inventory_app']

# Helper to get collections
def get_users_col():
    return db['users']
def get_inventory_col():
    return db['inventory']

# Database setup (ensure tables exist)
def init_db():
    users_col = get_users_col()
    # Desired users and passwords
    allowed_users = [
        {'username': 'admin', 'password': 'admin'},
        {'username': 'aziz taifour', 'password': 'aziz'},
        {'username': 'mohcine elhaddad asoufi', 'password': 'mohcine'},
    ]
    # Remove any user not in allowed_users
    existing_usernames = set(u['username'] for u in users_col.find({}, {'username': 1}))
    allowed_usernames = set(u['username'] for u in allowed_users)
    for username in existing_usernames - allowed_usernames:
        users_col.delete_many({'username': username})
    # Add any missing allowed users
    for user in allowed_users:
        if users_col.count_documents({'username': user['username']}) == 0:
            users_col.insert_one(user)
    # Inventory collection will be empty unless populated

# Login Window
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IT Inventory Login")
        self.setFixedSize(380, 315)
        self.setWindowIcon(QIcon())
        layout = QVBoxLayout()
        layout.setContentsMargins(34, 32, 34, 34)
        layout.setSpacing(10)
        # Title
        title = QLabel("<b style='font-size:23px;color:#4F8FF9;letter-spacing:1px;'>IT Inventory</b>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        # Username
        self.user_label = QLabel("Username:")
        self.user_label.setStyleSheet("font-weight:600;font-size:15px;margin-bottom:2px;")
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Enter your username...")
        self.user_input.setMinimumHeight(36)
        self.user_input.setStyleSheet("QLineEdit {border-radius:8px;border:1.5px solid #d0d6e1;padding:8px 12px;font-size:15px;background:#f8fafc;} QLineEdit:focus {border:2px solid #4F8FF9;background:#fff;}")
        # Password
        self.pass_label = QLabel("Password:")
        self.pass_label.setStyleSheet("font-weight:600;font-size:15px;margin-bottom:2px;")
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Enter your password...")
        self.pass_input.setMinimumHeight(36)
        self.pass_input.setStyleSheet("QLineEdit {border-radius:8px;border:1.5px solid #d0d6e1;padding:8px 12px;font-size:15px;background:#f8fafc;} QLineEdit:focus {border:2px solid #4F8FF9;background:#fff;}")
        self.pass_input.setEchoMode(QLineEdit.Password)
        # Password visibility toggle
        self.show_pass_btn = QToolButton()
        self.show_pass_btn.setText("👁️")
        self.show_pass_btn.setCheckable(True)
        self.show_pass_btn.setCursor(Qt.PointingHandCursor)
        self.show_pass_btn.setToolTip("Show/Hide Password")
        self.show_pass_btn.setStyleSheet("QToolButton {background:transparent;font-size:17px;padding:0 6px;} QToolButton:pressed {color:#4F8FF9;}")
        self.show_pass_btn.clicked.connect(self.toggle_password)
        pass_row = QHBoxLayout()
        pass_row.setSpacing(0)
        pass_row.addWidget(self.pass_input)
        pass_row.addWidget(self.show_pass_btn)
        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.setMinimumHeight(44)
        self.login_btn.setStyleSheet("QPushButton {background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #4F8FF9,stop:1 #44b37f);color:#fff;font-size:18px;font-weight:700;border-radius:10px;} QPushButton:hover {background:#356fd6;} QPushButton:pressed {background:#274e96;}")
        self.login_btn.clicked.connect(self.handle_login)
        # Add widgets to layout
        layout.addSpacing(6)
        layout.addWidget(self.user_label)
        layout.addWidget(self.user_input)
        layout.addSpacing(2)
        layout.addWidget(self.pass_label)
        layout.addLayout(pass_row)
        layout.addSpacing(14)
        layout.addWidget(self.login_btn)
        # Footer
        layout.addSpacing(10)
        footer = QLabel("<span style='color:#bfc6d1;font-size:12px;'>© 2025 IT Dept. Fairmont Tazi Palace</span>")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
        self.setLayout(layout)
    def toggle_password(self):
        self.pass_input.setEchoMode(QLineEdit.Normal if self.show_pass_btn.isChecked() else QLineEdit.Password)

    def handle_login(self):
        username = self.user_input.text()
        password = self.pass_input.text()
        users_col = get_users_col()
        user = users_col.find_one({'username': username, 'password': password})
        if user:
            self.accept_login()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

    def accept_login(self):
        self.close()
        self.main_window = InventoryWindow()
        self.main_window.show()

# Main Inventory Window with CRUD operations
class InventoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IT Inventory - Fairmont Tazi Palace Tanger")
        self.setGeometry(500, 200, 950, 600)
        self.setWindowIcon(QIcon())
        self.users_col = get_users_col()
        self.inventory_col = get_inventory_col()
        self.setStyleSheet(self.get_stylesheet())
        self.init_ui()
        self.load_data()

    def get_stylesheet(self):
        return """
        QWidget { background: #f4f7fb; color: #222; font-family: 'Segoe UI', Arial, sans-serif; font-size: 15px; }
        QFrame#HeaderBar { background: #fff; border-radius: 12px; padding: 18px 32px; margin-bottom: 18px; border: 1px solid #e0e4ea; }
        QLabel#HeaderTitle { font-size: 26px; font-weight: bold; color: #222; letter-spacing: 1px; }
        QTableWidget { background: #fff; border-radius: 10px; border: 1px solid #e0e4ea; gridline-color: #e0e4ea; selection-background-color: #e8f0fe; font-size: 14px; }
        QTableWidget::item:selected { background: #e8f0fe; }
        QPushButton#AddBtn {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F8FF9, stop:1 #44b37f);
            color: #fff;
            border-radius: 22px;
            padding: 10px 36px;
            font-size: 17px;
            font-weight: 600;
            margin: 0 8px;
            min-width: 120px;
            border: none;
            
        }
        QPushButton#AddBtn:hover { background: #356fd6; }
        QPushButton#AddBtn:pressed { background: #274e96; }
        QPushButton#EditBtn {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F8FF9, stop:1 #44b37f);
            color: #fff;
            border-radius: 22px;
            padding: 10px 36px;
            font-size: 17px;
            font-weight: 600;
            margin: 0 8px;
            min-width: 120px;
            border: none;
            
        }
        QPushButton#EditBtn:hover { background: #356fd6; }
        QPushButton#EditBtn:pressed { background: #274e96; }
        QPushButton#DeleteBtn {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f67272, stop:1 #e06f6c);
            color: #fff;
            border-radius: 22px;
            padding: 10px 36px;
            font-size: 17px;
            font-weight: 600;
            margin: 0 8px;
            min-width: 120px;
            border: none;
            
        }
        QPushButton#DeleteBtn:hover { background: #b94c3f; }
        QPushButton#DeleteBtn:pressed { background: #a13c2d; }
        QDialog { background: #fff; }
        QLineEdit { background: #f3f6fa; border: 1px solid #e0e4ea; border-radius: 6px; padding: 6px; }
        QMessageBox { font-size: 15px; }
        /* Dashboard widgets */
        QFrame#DashboardWidget { background: #fff; border-radius: 12px; border: 1px solid #e0e4ea; font-size: 17px; font-weight: 600; padding: 12px 20px; color: #222; margin: 0 7px; min-width:120px; }
        """

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 24, 30, 24)
        main_layout.setSpacing(16)

        # Header Bar
        header = QFrame()
        header.setObjectName("HeaderBar")
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setAlignment(Qt.AlignCenter)
        # Title only (no logo)
        title = QLabel("IT Inventory Dashboard")
        title.setObjectName("HeaderTitle")
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title, alignment=Qt.AlignCenter)

        header.setLayout(header_layout)
        main_layout.addWidget(header)

        # Dashboard Widgets
        self.widget_frame = QFrame()
        widget_layout = QHBoxLayout()
        self.total_label = QLabel()
        self.inuse_label = QLabel()
        self.available_label = QLabel()
        self.retired_label = QLabel()
        for w in [self.total_label, self.inuse_label, self.available_label, self.retired_label]:
            w.setStyleSheet("font-size:20px;font-weight:600;background:#fff;border-radius:12px;padding:18px 32px;margin:0 14px 0 0;border:1.5px solid #e0e4ea;color:#222;")
        widget_layout.setSpacing(0)
        widget_layout.addWidget(self.total_label)
        widget_layout.addWidget(self.inuse_label)
        widget_layout.addWidget(self.available_label)
        widget_layout.addWidget(self.retired_label)
        self.widget_frame.setLayout(widget_layout)
        main_layout.addWidget(self.widget_frame)

        # Search Bar & Export
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search inventory...")
        self.search_input.setMinimumHeight(34)
        self.search_input.setStyleSheet("border-radius:7px;background:#fff;border:1.5px solid #e0e4ea;padding:8px 14px;font-size:15px;")
        self.search_input.textChanged.connect(self.filter_table)
        search_icon = QLabel("")
        search_icon.setStyleSheet("font-size:18px;margin-right:6px;")
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        self.export_btn = QToolButton()
        self.export_btn.setText("Export CSV")
        self.export_btn.setIcon(QIcon.fromTheme("document-save"))
        self.export_btn.setToolTip("Export inventory to CSV")
        self.export_btn.setStyleSheet("background:#fff;border:1.5px solid #e0e4ea;border-radius:7px;padding:7px 18px;font-size:14px;font-weight:600;color:#4F8FF9;")
        self.export_btn.clicked.connect(self.export_csv)
        search_layout.addWidget(self.export_btn)
        main_layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Device Name", "Serial Number", "Location", "Status", "Assigned To"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setStyleSheet("QTableWidget {background:#fff;border-radius:12px;font-size:15px;} QHeaderView::section {background:#f3f6fa;font-size:16px;font-weight:600;color:#4F8FF9;border:none;border-bottom:2px solid #e0e4ea;padding:10px;} QTableWidget::item:hover {background:#eaf1fa;}")
        main_layout.addWidget(self.table)

        # Action Buttons with icons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.add_btn = QPushButton("+ Add Item")
        self.add_btn.setObjectName("AddBtn")
        self.add_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_btn.setMinimumHeight(46)
        self.add_btn.setMinimumWidth(150)
        self.add_btn.setStyleSheet("QPushButton {background:#22c55e;color:#fff;font-size:18px;font-weight:700;border-radius:10px;margin-right:14px;} QPushButton:hover {background:#16a34a;}")
        self.add_btn.clicked.connect(self.add_item)
        self.edit_btn = QPushButton("✎ Edit")
        self.edit_btn.setObjectName("EditBtn")
        self.edit_btn.setIcon(QIcon.fromTheme("document-edit"))
        self.edit_btn.setMinimumHeight(46)
        self.edit_btn.setMinimumWidth(120)
        self.edit_btn.setStyleSheet("QPushButton {background:#2563eb;color:#fff;font-size:18px;font-weight:700;border-radius:10px;margin-right:14px;} QPushButton:hover {background:#1d4ed8;}")
        self.edit_btn.clicked.connect(self.edit_item)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("DeleteBtn")
        self.delete_btn.setIcon(QIcon.fromTheme("edit-delete"))
        self.delete_btn.setMinimumHeight(38)
        self.delete_btn.setStyleSheet("background:#e06f6c;color:#fff;font-size:16px;font-weight:600;border-radius:8px;")
        self.delete_btn.clicked.connect(self.delete_item)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        self.all_data = []

    def load_data(self):
        self.all_data = list(self.inventory_col.find())
        self.refresh_stats()
        self.filter_table()
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

    def refresh_stats(self):
        total = len(self.all_data)
        inuse = sum(1 for row in self.all_data if str(row.get('status', '')).strip().lower() == 'in use')
        available = sum(1 for row in self.all_data if str(row.get('status', '')).strip().lower() == 'available')
        retired = sum(1 for row in self.all_data if str(row.get('status', '')).strip().lower() == 'retired')
        self.total_label.setText(f"Total Items: <b>{total}</b>")
        self.inuse_label.setText(f"In Use: <b style='color:#4F8FF9'>{inuse}</b>")
        self.available_label.setText(f"Available: <b style='color:#44b37f'>{available}</b>")
        self.retired_label.setText(f"Retired: <b style='color:#e06f6c'>{retired}</b>")

    def filter_table(self):
        query = self.search_input.text().strip().lower()
        self.table.setRowCount(0)
        
        for row in self.all_data:
            # row: MongoDB doc
            row_values = [
                row.get('device_name', ''),
                row.get('serial_number', ''),
                row.get('location', ''),
                row.get('status', ''),
                row.get('assigned_to', '')
            ]
            if query:
                row_str = ' '.join(str(x).lower() for x in row_values)
                if query not in row_str:
                    continue
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(row_values):
                if col_idx == 3:  # Status column
                    status = str(value).strip().lower()
                    if status == 'in use':
                        color = QColor('#4F8FF9')
                    elif status == 'available':
                        color = QColor('#44b37f')
                    elif status == 'retired':
                        color = QColor('#e06f6c')
                    else:
                        color = QColor('#fff')
                    item = QTableWidgetItem(str(value))
                    item.setBackground(color)
                    item.setTextAlignment(Qt.AlignCenter)
                    font = item.font(); font.setBold(True)
                    item.setFont(font)
                else:
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(row_idx, col_idx, item)
    def add_item(self):
        dialog = InventoryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            self.inventory_col.insert_one(data)
            self.load_data()
            QMessageBox.information(self, "Item Added", "Inventory item added successfully!")


    def edit_item(self):
        selected = self.table.currentRow()
        if selected < 0 or selected >= len(self.all_data):
            QMessageBox.warning(self, "No Selection", "Please select an item to edit.")
            return
        row_data = self.all_data[selected]
        dialog = InventoryDialog(self, (
            str(row_data.get('_id', '')),
            row_data.get('device_name', ''),
            row_data.get('serial_number', ''),
            row_data.get('location', ''),
            row_data.get('status', ''),
            row_data.get('assigned_to', '')
        ))
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            self.inventory_col.update_one({'_id': ObjectId(str(row_data['_id']))}, {'$set': data})
            self.load_data()
            QMessageBox.information(self, "Item Updated", "Inventory item updated successfully!")

    def delete_item(self):
        selected = self.table.currentRow()
        if selected < 0 or selected >= len(self.all_data):
            QMessageBox.warning(self, "No Selection", "Please select an item to delete.")
            return
        confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this item?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            row_data = self.all_data[selected]
            self.inventory_col.delete_one({'_id': ObjectId(str(row_data['_id']))})
            self.load_data()
            QMessageBox.information(self, "Item Deleted", "Inventory item deleted successfully!")

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Inventory", "inventory.csv", "CSV Files (*.csv)")
        if path:
            import csv
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Device Name", "Serial Number", "Location", "Status", "Assigned To"])
                for row in self.all_data:
                    writer.writerow([
                        row.get("device_name", ""),
                        row.get("serial_number", ""),
                        row.get("location", ""),
                        row.get("status", ""),
                        row.get("assigned_to", "")
                    ])

from PyQt5.QtWidgets import QComboBox

class InventoryDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Inventory Item")
        self.resize(350, 220)
        layout = QFormLayout()
        layout.setContentsMargins(18, 24, 18, 18)
        layout.setSpacing(14)
        self.device_name = QLineEdit()
        self.device_name.setPlaceholderText("Device Name")
        self.device_name.setMinimumHeight(32)
        self.serial_number = QLineEdit()
        self.serial_number.setPlaceholderText("Serial Number")
        self.serial_number.setMinimumHeight(32)
        self.location = QComboBox()
        self.location.setEditable(False)
        self.location_options = [
            "IT Office", "Reception", "Server Room", "CEO Office", "Lobby", "HR", "Finance", "Storage", "Meeting Room",
            "crudo", "s-lounge", "social kitchen", "parisa", "Other"
        ]
        self.location.addItems(self.location_options)
        self.location_other = QLineEdit()
        self.location_other.setPlaceholderText("Enter custom location...")
        self.location_other.setMinimumHeight(32)
        self.location_other.setVisible(False)
        self.location.currentTextChanged.connect(self.on_location_changed)
        self.status = QComboBox()
        self.status.addItems(["In Use", "Available", "Retired"])
        self.status.setMinimumHeight(32)
        self.assigned_to = QLineEdit()
        self.assigned_to.setPlaceholderText("Assigned To")
        self.assigned_to.setMinimumHeight(32)
        layout.addRow("Device Name:", self.device_name)
        layout.addRow("Serial Number:", self.serial_number)
        location_row = QHBoxLayout()
        location_row.addWidget(self.location)
        location_row.addWidget(self.location_other)
        layout.addRow("Location:", location_row)
        layout.addRow("Status:", self.status)
        layout.addRow("Assigned To:", self.assigned_to)
        self.buttons = QHBoxLayout()
        self.ok_btn = QPushButton("✔ OK")
        self.ok_btn.setMinimumHeight(32)
        self.ok_btn.setStyleSheet("background:#44b37f;color:#fff;font-weight:600;border-radius:7px;font-size:15px;")
        self.cancel_btn = QPushButton("✖ Cancel")
        self.cancel_btn.setMinimumHeight(32)
        self.cancel_btn.setStyleSheet("background:#e06f6c;color:#fff;font-weight:600;border-radius:7px;font-size:15px;")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.buttons.addWidget(self.ok_btn)
        self.buttons.addWidget(self.cancel_btn)
        layout.addRow(self.buttons)
        self.setLayout(layout)
        if data:
            # data: (id, device_name, serial_number, location, status, assigned_to)
            self.device_name.setText(str(data[1]))
            self.serial_number.setText(str(data[2]))
            location_value = str(data[3])
            if location_value in self.location_options:
                idx = self.location.findText(location_value, Qt.MatchFixedString)
                if idx >= 0:
                    self.location.setCurrentIndex(idx)
                self.location_other.setVisible(False)
            else:
                idx = self.location.findText("Other", Qt.MatchFixedString)
                if idx >= 0:
                    self.location.setCurrentIndex(idx)
                self.location_other.setText(location_value)
                self.location_other.setVisible(True)
            idx = self.status.findText(str(data[4]), Qt.MatchFixedString)
            if idx >= 0:
                self.status.setCurrentIndex(idx)
            self.assigned_to.setText(str(data[5]))

    def on_location_changed(self, text):
        if text == "Other":
            self.location_other.setVisible(True)
        else:
            self.location_other.setVisible(False)

    def get_data(self):
        location_val = self.location.currentText()
        if location_val == "Other":
            location_val = self.location_other.text().strip()
        return {
            "device_name": self.device_name.text(),
            "serial_number": self.serial_number.text(),
            "location": location_val,
            "status": self.status.currentText(),
            "assigned_to": self.assigned_to.text(),
        }

def populate_sample_inventory():
    inventory_col = get_inventory_col()
    if inventory_col.count_documents({}) == 0:
        sample_data = [
            {"device_name": "Dell Latitude 5420", "serial_number": "SN1234567", "location": "IT Office", "status": "In Use", "assigned_to": "Ahmed"},
            {"device_name": "HP EliteBook 840", "serial_number": "SN9876543", "location": "Reception", "status": "Available", "assigned_to": ""},
            {"device_name": "Cisco Switch 2960", "serial_number": "SW001122", "location": "Server Room", "status": "In Use", "assigned_to": "IT Team"},
            {"device_name": "Logitech MX Master 3S", "serial_number": "MXM2025", "location": "IT Office", "status": "Available", "assigned_to": ""},
            {"device_name": "Apple MacBook Pro", "serial_number": "MBP2022", "location": "CEO Office", "status": "In Use", "assigned_to": "Mr. Smith"},
            {"device_name": "Ubiquiti AP AC Pro", "serial_number": "UBIAP01", "location": "Lobby", "status": "Retired", "assigned_to": ""},
            {"device_name": "Lenovo ThinkPad X1", "serial_number": "THINKX1", "location": "HR", "status": "Available", "assigned_to": ""},
            {"device_name": "Brother HL-L2370DN", "serial_number": "PRT9988", "location": "Finance", "status": "In Use", "assigned_to": "Finance Team"},
            {"device_name": "Samsung SSD 1TB", "serial_number": "SSD1TB22", "location": "Storage", "status": "Available", "assigned_to": ""},
            {"device_name": "Epson Projector", "serial_number": "PROJ2023", "location": "Meeting Room", "status": "In Use", "assigned_to": "All Staff"}
        ]
        inventory_col.insert_many(sample_data)


# ... (rest of code unchanged)

if __name__ == "__main__":
    init_db()
    populate_sample_inventory()
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
