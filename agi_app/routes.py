from flask import session, flash, Flask, render_template, request, redirect, url_for, session, flash
from models import get_connection, get_user_by_username, check_user_password
from werkzeug.security import generate_password_hash
from auth import login_required



app = Flask(__name__)
app.secret_key = 'substitua-por-uma-chave-secreta'

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and check_user_password(user, password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Credenciais inválidas.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    search_query = request.args.get('q', '')
    sort = request.args.get('sort', 'id')
    direction = request.args.get('direction', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    # Segurança: só colunas válidas
    valid_cols = ['id', 'npu', 'cliente', 'estado']
    if sort not in valid_cols: sort = 'id'
    if direction not in ['asc', 'desc']: direction = 'asc'

    conn = get_connection()
    cur = conn.cursor()

    # Conta total com filtro
    if search_query:
        cur.execute(
            f"SELECT COUNT(*) FROM processos WHERE npu LIKE ? OR cliente LIKE ?",
            (f'%{search_query}%', f'%{search_query}%')
        )
        total = cur.fetchone()[0]
        cur.execute(
            f"SELECT * FROM processos WHERE npu LIKE ? OR cliente LIKE ? "
            f"ORDER BY {sort} {direction} LIMIT ? OFFSET ?",
            (f'%{search_query}%', f'%{search_query}%', per_page, offset)
        )
    else:
        cur.execute("SELECT COUNT(*) FROM processos")
        total = cur.fetchone()[0]
        cur.execute(
            f"SELECT * FROM processos ORDER BY {sort} {direction} LIMIT ? OFFSET ?",
            (per_page, offset)
        )

    processos = cur.fetchall()
    conn.close()

    total_pages = (total + per_page - 1) // per_page
    return render_template('index.html',
                           processos=processos,
                           page=page,
                           total_pages=total_pages,
                           q=search_query,
                           sort=sort,
                           direction=direction)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_processo():
    if request.method == 'POST':
        npu = request.form['npu']
        cliente = request.form['cliente']
        estado = request.form['estado']
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO processos (npu, cliente, estado) VALUES (?, ?, ?)',
            (npu, cliente, estado)
        )
        conn.commit()
        conn.close()
        flash('Processo adicionado com sucesso.', 'success')
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/view/<int:id>')
@login_required
def view(id):
    conn = get_connection()
    processo = conn.execute(
        "SELECT * FROM processos WHERE id = ?", (id,)
    ).fetchone()
    conn.close()
    return render_template('view.html', processo=processo)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    conn = get_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        npu = request.form['npu']
        cliente = request.form['cliente']
        estado = request.form['estado']
        cur.execute(
            'UPDATE processos SET npu = ?, cliente = ?, estado = ? WHERE id = ?',
            (npu, cliente, estado, id)
        )
        conn.commit()
        conn.close()
        flash('Processo atualizado com sucesso.', 'success')
        return redirect(url_for('index'))

    processo = cur.execute(
        "SELECT * FROM processos WHERE id = ?", (id,)
    ).fetchone()
    conn.close()
    return render_template('edit.html', processo=processo)

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    conn = get_connection()
    conn.execute('DELETE FROM processos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Processo excluído.', 'warning')
    return redirect(url_for('index'))
@app.route('/usuarios')
def listar_usuarios():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, username FROM users')
    usuarios = cur.fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios)
@app.route('/usuarios/add', methods=['GET', 'POST'])
def adicionar_usuario():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO users (username,password_hash) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            flash('Usuário criado com sucesso!')
        except:
            flash('Erro: nome de usuário já existe!')
        conn.close()
        return redirect(url_for('listar_usuarios'))

    return render_template('add_usuario.html')

@app.route('/usuarios/delete/<int:id>')
def excluir_usuario(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))


    conn = get_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE id =?', (id,))
    conn.commit()
    conn.close()
    flash('Usuário excluído com sucesso.')
    return redirect(url_for('listar_usuarios'))

@app.route('/clientes')
@login_required
def listar_clientes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM clientes')
    clientes = cur.fetchall()
    conn.close()
    return render_template('clientes/listar.html', clientes=clientes)

@app.route('/clientes/add', methods=['GET', 'POST'])
@login_required
def adicionar_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)', (nome, email, telefone))
        conn.commit()
        conn.close()
        return redirect(url_for('listar_clientes'))
    return render_template('clientes/adicionar.html')

@app.route('/clientes/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(id):
    conn = get_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        cur.execute('UPDATE clientes SET nome = ?, email = ?, telefone = ? WHERE id = ?', (nome, email, telefone, id))
        conn.commit()
        conn.close()
        return redirect(url_for('listar_clientes'))
    cur.execute('SELECT * FROM clientes WHERE id = ?', (id,))
    cliente = cur.fetchone()
    conn.close()
    return render_template('clientes/editar.html', cliente=cliente)

@app.route('/clientes/delete/<int:id>')
@login_required
def deletar_cliente(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM clientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('listar_clientes'))
