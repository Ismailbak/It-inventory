import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QDialog, QFormLayout, QFrame, QSpacerItem, QSizePolicy, QComboBox, QToolButton, QFileDialog

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor, QPixmap

DB_NAME = 'inventory.db'

# Database setup

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    # Inventory table
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_name TEXT NOT NULL,
        serial_number TEXT,
        location TEXT,
        status TEXT,
        assigned_to TEXT
    )''')
    # Insert default user if not exists
    c.execute("SELECT * FROM users WHERE username=?", ("admin",))
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin"))
    conn.commit()
    conn.close()

# Login Window
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IT Inventory Login")
        self.setGeometry(600, 300, 300, 160)
        self.setWindowIcon(QIcon())
        layout = QVBoxLayout()
        self.user_label = QLabel("Username:")
        self.user_input = QLineEdit()
        self.pass_label = QLabel("Password:")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.user_label)
        layout.addWidget(self.user_input)
        layout.addWidget(self.pass_label)
        layout.addWidget(self.pass_input)
        layout.addWidget(self.login_btn)
        self.setLayout(layout)

    def handle_login(self):
        username = self.user_input.text()
        password = self.pass_input.text()
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        if c.fetchone():
            self.accept_login()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
        conn.close()

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
        self.conn = sqlite3.connect(DB_NAME)
        self.theme = 'light'
        self.setStyleSheet(self.get_stylesheet())
        self.init_ui()
        self.load_data()

    def get_stylesheet(self):
        if self.theme == 'dark':
            return """
            QWidget { background: #22272e; color: #e6e6e6; font-family: 'Segoe UI', Arial, sans-serif; font-size: 15px; }
            QFrame#HeaderBar { background: #23272f; border-radius: 12px; padding: 18px 32px; margin-bottom: 18px; border: 1px solid #2c313a; }
            QLabel#HeaderTitle { font-size: 26px; font-weight: bold; color: #fff; letter-spacing: 1px; }
            QTableWidget { background: #23272f; border-radius: 10px; border: 1px solid #2c313a; gridline-color: #2c313a; selection-background-color: #2d3b55; font-size: 14px; }
            QTableWidget::item:selected { background: #2d3b55; }
            QHeaderView::section { background: #242933; border: none; border-bottom: 2px solid #2c313a; font-weight: 500; font-size: 15px; color: #e6e6e6; padding: 8px; }
            QPushButton, QToolButton { background: #4F8FF9; color: #fff; border-radius: 7px; padding: 8px 20px; font-size: 15px; margin: 0 5px; }
            QPushButton:hover, QToolButton:hover { background: #356fd6; }
            QPushButton:pressed, QToolButton:pressed { background: #274e96; }
            QDialog { background: #23272f; }
            QLineEdit { background: #2c313a; border: 1px solid #23272f; border-radius: 6px; padding: 6px; color: #e6e6e6; }
            QMessageBox { font-size: 15px; }
            """
        else:
            return """
            QWidget { background: #F6F8FB; font-family: 'Segoe UI', Arial, sans-serif; font-size: 15px; }
            QFrame#HeaderBar { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f8fbff, stop:1 #eaf1fa); border-radius: 18px; padding: 28px 48px 28px 48px; margin-bottom: 24px; border: 1.5px solid #e0e4ea; box-shadow: 0 6px 32px rgba(79,143,249,0.09); }
            QLabel#HeaderTitle { font-size: 36px; font-weight: 700; color: #1d2636; letter-spacing: 1.5px; text-align: center; margin-bottom: 0px; }
            QToolButton#ThemeToggle { background: #4F8FF9; color: #fff; border-radius: 22px; padding: 0px; min-width: 44px; min-height: 44px; max-width: 44px; max-height: 44px; font-size: 22px; margin-left: 18px; box-shadow: 0 2px 8px rgba(79,143,249,0.08); }
            QToolButton#ThemeToggle:hover { background: #356fd6; }
            QToolButton#ThemeToggle:pressed { background: #274e96; }
            QTableWidget { background: #fff; border-radius: 10px; border: 1px solid #e0e4ea; gridline-color: #e0e4ea; selection-background-color: #e6f7ff; font-size: 14px; alternate-background-color: #f3f6fa; }
            QTableWidget::item:selected { background: #d0ebff; }
            QTableWidget::item:hover { background: #e0e4ea; }
            QHeaderView::section { background: #f3f6fa; border: none; border-bottom: 2px solid #e0e4ea; font-weight: 500; font-size: 15px; color: #333; padding: 8px; }
            QPushButton#AddBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5fa8ff, stop:1 #4F8FF9);
                color: #fff;
                border-radius: 22px;
                padding: 10px 36px;
                font-size: 17px;
                font-weight: 600;
                margin: 0 8px;
                min-width: 120px;
                border: none;
                box-shadow: 0 2px 8px rgba(79,143,249,0.10);
            }
            QPushButton#AddBtn:hover { background: #356fd6; }
            QPushButton#AddBtn:pressed { background: #274e96; }
            QPushButton#EditBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F8FF9, stop:1 #5fa8ff);
                color: #fff;
                border-radius: 22px;
                padding: 10px 36px;
                font-size: 17px;
                font-weight: 600;
                margin: 0 8px;
                min-width: 120px;
                border: none;
                box-shadow: 0 2px 8px rgba(79,143,249,0.10);
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
                box-shadow: 0 2px 8px rgba(224,111,108,0.10);
            }
            QPushButton#DeleteBtn:hover { background: #b94c3f; }
            QPushButton#DeleteBtn:pressed { background: #a13c2d; }
            QDialog { background: #fff; }
            QLineEdit { background: #f3f6fa; border: 1px solid #e0e4ea; border-radius: 6px; padding: 6px; }
            QMessageBox { font-size: 15px; }
            /* Dashboard widgets */
            QFrame#DashboardWidget { background: #fff; border-radius: 12px; border: 1px solid #e0e4ea; font-size: 17px; font-weight: 600; padding: 12px 20px; color: #222; margin: 0 7px; min-width:120px; }
            """

    def toggle_theme(self):
        self.theme = 'dark' if self.theme == 'light' else 'light'
        self.setStyleSheet(self.get_stylesheet())
        # Update theme button icon
        self.theme_btn.setText("🌙" if self.theme == 'light' else "☀️")
        self.refresh_stats()
        self.filter_table()

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
        # Theme toggle button (top right)
        theme_row = QHBoxLayout()
        theme_row.addStretch()
        self.theme_btn = QToolButton()
        self.theme_btn.setObjectName("ThemeToggle")
        self.theme_btn.setText("🌙" if self.theme == 'light' else "☀️")
        self.theme_btn.setToolTip("Toggle Light/Dark Mode")
        self.theme_btn.clicked.connect(self.toggle_theme)
        theme_row.addWidget(self.theme_btn)
        header_layout.addLayout(theme_row)
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
            w.setStyleSheet("font-size:18px;font-weight:bold;background:#fff;border-radius:8px;padding:16px 28px;margin:0 12px;border:1px solid #e0e4ea;color:#222;")
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
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(QLabel("🔍"))
        search_layout.addWidget(self.search_input)
        self.export_btn = QToolButton()
        self.export_btn.setText("Export CSV")
        self.export_btn.setIcon(QIcon.fromTheme("document-save"))
        self.export_btn.setToolTip("Export inventory to CSV")
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
        main_layout.addWidget(self.table)

        # Action Buttons with icons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.add_btn = QPushButton("Add")
        self.add_btn.setObjectName("AddBtn")
        self.add_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_btn.clicked.connect(self.add_item)
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setObjectName("EditBtn")
        self.edit_btn.setIcon(QIcon.fromTheme("document-edit"))
        self.edit_btn.clicked.connect(self.edit_item)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("DeleteBtn")
        self.delete_btn.setIcon(QIcon.fromTheme("edit-delete"))
        self.delete_btn.clicked.connect(self.delete_item)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        self.all_data = []

    def load_data(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM inventory")
        self.all_data = c.fetchall()
        self.refresh_stats()
        self.filter_table()
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

    def refresh_stats(self):
        total = len(self.all_data)
        inuse = sum(1 for row in self.all_data if row[4].strip().lower() == 'in use')
        available = sum(1 for row in self.all_data if row[4].strip().lower() == 'available')
        retired = sum(1 for row in self.all_data if row[4].strip().lower() == 'retired')
        self.total_label.setText(f"Total Items: <b>{total}</b>")
        self.inuse_label.setText(f"In Use: <b style='color:#4F8FF9'>{inuse}</b>")
        self.available_label.setText(f"Available: <b style='color:#44b37f'>{available}</b>")
        self.retired_label.setText(f"Retired: <b style='color:#e06f6c'>{retired}</b>")

    def filter_table(self):
        query = self.search_input.text().strip().lower()
        self.table.setRowCount(0)
        dark_mode = self.theme == 'dark'
        for row in self.all_data:
            if query:
                row_str = ' '.join(str(x).lower() for x in row[1:])
                if query not in row_str:
                    continue
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(row[1:]):
                if col_idx == 3:  # Status column
                    status = str(value).strip().lower()
                    if status == 'in use':
                        color = QColor('#4F8FF9'); text = '● In Use'
                    elif status == 'available':
                        color = QColor('#44b37f'); text = '● Available'
                    elif status == 'retired':
                        color = QColor('#e06f6c'); text = '● Retired'
                    else:
                        color = QColor('#b0b0b0'); text = f'● {value}'
                    item = QTableWidgetItem(text)
                    item.setForeground(QColor('#fff'))
                    item.setBackground(color)
                    item.setTextAlignment(Qt.AlignCenter)
                    font = item.font(); font.setBold(True)
                    item.setFont(font)
                else:
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                    # Fix dark mode cell background/foreground
                    if dark_mode:
                        item.setBackground(QColor('#23272f'))
                        item.setForeground(QColor('#e6e6e6'))
                self.table.setItem(row_idx, col_idx, item)

    def add_item(self):
        dialog = InventoryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            c = self.conn.cursor()
            c.execute(
                "INSERT INTO inventory (device_name, serial_number, location, status, assigned_to) VALUES (?, ?, ?, ?, ?)",
                (data["device_name"], data["serial_number"], data["location"], data["status"], data["assigned_to"])
            )
            self.conn.commit()
            self.load_data()
            QMessageBox.information(self, "Item Added", "Inventory item added successfully!")

    def edit_item(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to edit.")
            return
        c = self.conn.cursor()
        c.execute("SELECT id, device_name, serial_number, location, status, assigned_to FROM inventory")
        rows = c.fetchall()
        row_data = rows[selected]
        dialog = InventoryDialog(self, row_data)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            c.execute(
                "UPDATE inventory SET device_name=?, serial_number=?, location=?, status=?, assigned_to=? WHERE id=?",
                (data["device_name"], data["serial_number"], data["location"], data["status"], data["assigned_to"], row_data[0])
            )
            self.conn.commit()
            self.load_data()
            QMessageBox.information(self, "Item Updated", "Inventory item updated successfully!")

    def delete_item(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to delete.")
            return
        confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this item?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            c = self.conn.cursor()
            c.execute("SELECT id FROM inventory")
            ids = [row[0] for row in c.fetchall()]
            item_id = ids[selected]
            c.execute("DELETE FROM inventory WHERE id=?", (item_id,))
            self.conn.commit()
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
                    writer.writerow(row[1:])
            QMessageBox.information(self, "Export Complete", f"Inventory exported to {path}")

from PyQt5.QtWidgets import QComboBox

class InventoryDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Inventory Item")
        self.resize(350, 220)
        layout = QFormLayout()
        self.device_name = QLineEdit()
        self.serial_number = QLineEdit()
        self.location = QLineEdit()
        self.status = QComboBox()
        self.status.addItems(["In Use", "Available", "Retired"])
        self.assigned_to = QLineEdit()
        layout.addRow("Device Name:", self.device_name)
        layout.addRow("Serial Number:", self.serial_number)
        layout.addRow("Location:", self.location)
        layout.addRow("Status:", self.status)
        layout.addRow("Assigned To:", self.assigned_to)
        self.setLayout(layout)
        self.buttons = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.buttons.addWidget(self.ok_btn)
        self.buttons.addWidget(self.cancel_btn)
        layout.addRow(self.buttons)
        if data:
            # data: (id, device_name, serial_number, location, status, assigned_to)
            self.device_name.setText(str(data[1]))
            self.serial_number.setText(str(data[2]))
            self.location.setText(str(data[3]))
            idx = self.status.findText(str(data[4]), Qt.MatchFixedString)
            if idx >= 0:
                self.status.setCurrentIndex(idx)
            self.assigned_to.setText(str(data[5]))

    def get_data(self):
        return {
            "device_name": self.device_name.text(),
            "serial_number": self.serial_number.text(),
            "location": self.location.text(),
            "status": self.status.currentText(),
            "assigned_to": self.assigned_to.text(),
        }

def populate_sample_inventory():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM inventory")
    if c.fetchone()[0] == 0:
        sample_data = [
            ("Dell Latitude 5420", "SN1234567", "IT Office", "In Use", "Ahmed"),
            ("HP EliteBook 840", "SN9876543", "Reception", "Available", ""),
            ("Cisco Switch 2960", "SW001122", "Server Room", "In Use", "IT Team"),
            ("Logitech MX Master 3S", "MXM2025", "IT Office", "Available", ""),
            ("Apple MacBook Pro", "MBP2022", "CEO Office", "In Use", "Mr. Smith"),
            ("Ubiquiti AP AC Pro", "UBIAP01", "Lobby", "Retired", ""),
            ("Lenovo ThinkPad X1", "THINKX1", "HR", "Available", ""),
            ("Brother HL-L2370DN", "PRT9988", "Finance", "In Use", "Finance Team"),
            ("Samsung SSD 1TB", "SSD1TB22", "Storage", "Available", ""),
            ("Epson Projector", "PROJ2023", "Meeting Room", "In Use", "All Staff"),
        ]
        c.executemany(
            "INSERT INTO inventory (device_name, serial_number, location, status, assigned_to) VALUES (?, ?, ?, ?, ?)",
            sample_data
        )
    conn.commit()
    conn.close()

# ... (rest of code unchanged)

if __name__ == "__main__":
    init_db()
    populate_sample_inventory()
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
