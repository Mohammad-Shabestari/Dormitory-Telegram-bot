import sqlite3

class Database:
    def __init__(self, db_name="dormitory_data.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # ایجاد جدول کاربران
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY ,
                username TEXT,
                name TEXT ,
                student_id TEXT ,
                national_id TEXT ,
                room_block TEXT
            )
        ''')
        # ایجاد جدول پیام‌ها
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_id INTEGER,
                section TEXT,
                message_text TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lost_found_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                item_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                contact TEXT,
                photo IMAGE,
                status TEXT DEFAULT 'pending',
                channel_message_id INTEGER
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    def insert_user(self, user_id,username, name, student_id, national_id, room_block):
        self.cursor.execute('''
            INSERT INTO users (user_id,username, name, student_id, national_id, room_block)
            VALUES (?,?, ?, ?, ?, ?)
        ''', (user_id,username, name, student_id, national_id, room_block))
        self.conn.commit()

    def update_user(self, user_id, username, name, student_id, national_id, room_block):

        self.cursor.execute('''
            UPDATE users 
            SET username = ?, name = ?, student_id = ?, national_id = ?, room_block = ?
            WHERE user_id = ?
        ''', (username, name, student_id, national_id, room_block, user_id))

        self.conn.commit()

    def get_all_users(self):

        self.cursor.execute("SELECT user_id FROM users")
        users = self.cursor.fetchall()

        # تبدیل نتیجه به لیست دیکشنری‌ها
        return [{'telegram_id': user[0]} for user in users]

    def get_user(self,user_id):

        self.cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))

        return self.cursor.fetchone()


    def insert_message(self, user_id, message_id, section, message_text):
        self.cursor.execute('''
            INSERT INTO messages (user_id, message_id, section, message_text)
            VALUES (?, ?, ?, ?)
        ''', (user_id, message_id, section, message_text))
        self.conn.commit()


    def get_message_by_message_id(self, message_id):
        self.cursor.execute('''
            SELECT * FROM messages WHERE message_id = ?
        ''', (message_id,))
        return self.cursor.fetchone()

    # افزودن آیتم گم‌شده یا پیدا‌شده
    def insert_lost_found_item(self,user_id, item_type, title, description, contact,photo):
        self.cursor.execute('''
            INSERT INTO lost_found_items (user_id, item_type, title, description, contact,photo, channel_message_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?,NULL, CURRENT_TIMESTAMP)
        ''', (user_id, item_type, title, description, contact,photo))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_lost_found_item(self, ad_id):
        self.cursor.execute('''
            SELECT * FROM lost_found_items WHERE id = ?
        ''', (ad_id,))
        return self.cursor.fetchone()

    def get_user_lost_found_items(self, user_id, status='pending'):
        self.cursor.execute('''
            SELECT * FROM lost_found_items WHERE user_id = ? AND status = ?
        ''', (user_id, status))
        return self.cursor.fetchall()

    def update_channel_message_id(self, ad_id, channel_message_id):
        self.cursor.execute('''
            UPDATE lost_found_items SET channel_message_id = ? WHERE id = ?
        ''', (channel_message_id, ad_id))
        self.conn.commit()

    def delete_old_items(self):
        self.cursor.execute('''
            DELETE FROM lost_found_items 
            WHERE created_at <= DATE('now', '-3 months')
        ''')
        self.conn.commit()



# ایجاد شیء از کلاس Database برای استفاده در دیگر بخش‌ها
db = Database()