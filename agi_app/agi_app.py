from models import init_db
from routes import app
from models import create_users_table

if __name__ == '__main__':
    init_db()
    create_users_table()
    app.run(debug=True)
