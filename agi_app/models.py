import sqlite3
import hashlib

DB_PATH = 'clientes.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''
          CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT,
            telefone TEXT   
             )
            ''')

    # Tabela de processos
    cur.execute('''
        CREATE TABLE IF NOT EXISTS processos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            npu TEXT NOT NULL,
            cliente TEXT NOT NULL,
            estado TEXT NOT NULL
      )
    ''')

    # Tabela de usuários
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Cria usuário admin padrão (senha: admin123) se não existir
    cur.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cur.fetchone():
        hashed = hashlib.sha256('admin123'.encode('utf-8')).hexdigest()
        cur.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                    ('admin', hashed))

    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    conn.close()
    return user

def check_user_password(user, password):
    return user['password'] == hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_users_table():
    conn = get_connection()
    cur = conn.cursor()

    # Cria a tabela se ela não existir
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')

    # Garante que o admin padrão exista
    cur.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cur.fetchone():
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash('admin123')
        cur.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', ('admin', password_hash))
        print("Usuário admin criado com senha padrão: admin123")

    conn.commit()
    conn.close()