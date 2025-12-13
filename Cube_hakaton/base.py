import sqlite3

class SQL:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    # Добавление пользователя в БД
    def add_user(self, id, table):
        query = f"INSERT INTO {table} (id) VALUES(?)"
        with self.connection:
            return self.cursor.execute(query, (id,))

    def add_word(self, word):
        query = f"INSERT INTO words (word) VALUES(?)"
        with self.connection:
            return self.cursor.execute(query, (word,))

    def delete_user(self, id, table):
        query = f"DELETE FROM {table} WHERE id = ?"
        with self.connection:
            return self.cursor.execute(query, (id,))

    def delete_word(self, word):
        query = f"DELETE FROM words WHERE word = ?"
        with self.connection:
            return self.cursor.execute(query, (word,))

    # Проверка, есть ли пользователь в БД
    def user_exist(self, id, table):
        query = f"SELECT * FROM {table} WHERE id = ?"
        with self.connection:
            result = self.cursor.execute(query, (id,)).fetchall()
            return bool(len(result))

    # Универсальные методы
    #db.get_field("user", id, "status")
    def get_field(self, table, id, field):
        query = f"SELECT {field} FROM {table} WHERE id = ?"
        with self.connection:
            result = self.cursor.execute(query, (id,)).fetchone()
            if result:
                return result[0]
            else:
                return None

    def get_field_name(self, table, name, field):
        query = f"SELECT {field} FROM {table} WHERE name = ?"
        with self.connection:
            result = self.cursor.execute(query, (name,)).fetchone()
            if result:
                return result[0]
            else:
                return None

    def get_users(self):
        query = f"SELECT balance, name FROM users"
        with self.connection:
            result = self.cursor.execute(query).fetchall()
            if result:
                return result
            else:
                return None

    def get_users_id(self):
        query = f"SELECT id FROM users"
        with self.connection:
            result = self.cursor.execute(query).fetchall()
            if result:
                return result
            else:
                return None

    def get_words(self):
        query = f"SELECT word, date FROM words"
        with self.connection:
            result = self.cursor.execute(query).fetchall()
            if result:
                return result
            else:
                return None

    def get_user(self, name):
        query = f"SELECT name, balance FROM users WHERE name = ?"
        with self.connection:
            result = self.cursor.execute(query, (name,)).fetchone()
            if result:
                return result
            else:
                return None

    def get_daily(self, daily):
        query = f"SELECT word FROM words WHERE daily = ?"
        with self.connection:
            result = self.cursor.execute(query, (daily,)).fetchone()
            if result:
                return result
            else:
                return None

    #db.get_update("user", id, "status", 1)
    def update_field(self, table, id, field, value):
        query = f"UPDATE {table} SET {field} = ? WHERE id = ?"
        with self.connection:
            self.cursor.execute(query, (value, id))

    def update_all(self, table, field, value):
        query = f"UPDATE {table} SET {field} = ?"
        with self.connection:
            self.cursor.execute(query, (value,))

    def update_word(self, word, field, value):
        query = f"UPDATE words SET {field} = ? WHERE word = ?"
        with self.connection:
            self.cursor.execute(query, (value, word))

    def update_field_name(self, table, name, field, value):
        query = f"UPDATE {table} SET {field} = ? WHERE name = ?"
        with self.connection:
            self.cursor.execute(query, (value, name))

    def close(self):
        self.connection.close()