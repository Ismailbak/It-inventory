# IT Inventory App

A modern, user-friendly Windows desktop application for managing IT inventory, built with Python and PyQt5.

## Features
- **Elegant UI**: Light/Dark mode, gradient headers, pill-shaped buttons, icons, and zebra-striped tables.
- **Inventory Management**: Add, edit, delete, and search devices with status badges.
- **User Authentication**: Login system with user credentials stored in SQLite.
- **Admin Utilities**:
  - `reset_admin_password.py`: Reset or create the admin password without deleting the database.
  - `add_users.py`: Script to add new users with preset credentials.
- **Data Export**: Export inventory to CSV.

## Getting Started

### Requirements
- Python 3.7+
- PyQt5 (see `requirements.txt`)

### Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/Ismailbak/It-inventory.git
   cd It-inventory/it-inventory
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the app:
   ```sh
   python main.py
   ```

### User Management
- **Default admin credentials:**
  - Username: `admin`
  - Password: `admin`
- To reset admin password:
  ```sh
  python reset_admin_password.py
  ```
- To add specific users:
  ```sh
  python add_users.py
  ```

## Screenshots
_Add screenshots here if desired._

## License
MIT

## Credits
Developed by Ismailbak and contributors.

---

Feel free to open issues or pull requests for improvements!
