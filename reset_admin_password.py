import sqlite3
import getpass

DB_NAME = 'inventory.db'

def reset_admin_password():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    new_pwd = getpass.getpass('Enter new admin password: ')
    confirm_pwd = getpass.getpass('Confirm new admin password: ')
    if new_pwd != confirm_pwd:
        print('Passwords do not match. Aborting.')
        return
    c.execute('UPDATE users SET password = ? WHERE username = ?', (new_pwd, 'admin'))
    if c.rowcount == 0:
        print('No admin user found. Creating admin user.')
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', new_pwd))
    conn.commit()
    conn.close()
    print('Admin password reset successfully.')

if __name__ == '__main__':
    reset_admin_password()
