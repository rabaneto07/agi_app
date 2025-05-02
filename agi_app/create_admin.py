from models import get_connection

def create_admin():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Criar tabela users se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Inserir o usuário admin
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'admin123'))
        conn.commit()
        print("Usuário admin criado com sucesso!")
    except Exception as e:
        print("Erro ao criar usuário:", e)
    
    conn.close()

if __name__ == '__main__':
    create_admin()