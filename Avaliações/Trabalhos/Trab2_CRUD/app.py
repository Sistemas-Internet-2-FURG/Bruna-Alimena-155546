from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

def get_db_connection():
    conn = sqlite3.connect('mercado.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS Sessao(
        id_sessao INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_sessao TEXT NOT NULL,
        corredor_sessao TEXT NOT NULL
    )
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS Produtos(
        id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_produto TEXT NOT NULL,
        quantidade_produto INTEGER NOT NULL,
        sessao_id INTEGER,
        FOREIGN KEY(sessao_id) REFERENCES Sessao(id_sessao)
    )
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS Usuarios(
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    products = conn.execute('''
        SELECT Produtos.id_produto, Produtos.nome_produto, Produtos.quantidade_produto, 
               Sessao.nome_sessao, Sessao.corredor_sessao
        FROM Produtos
        JOIN Sessao ON Produtos.sessao_id = Sessao.id_sessao
    ''').fetchall()

    sessions = conn.execute('''
        SELECT * FROM Sessao
    ''').fetchall()  

    conn.close()
    return render_template('index.html', products=products, sessions=sessions)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO Usuarios (nome_usuario, senha) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash('Nome de usuário já existe!')
            return redirect(url_for('register'))

        conn.close()
        flash('Cadastro realizado com sucesso!')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Usuarios WHERE nome_usuario = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['senha'], password):
            session['user_id'] = user['id_usuario']
            session['username'] = user['nome_usuario']
            flash('Login realizado com sucesso!')
            return redirect(url_for('index'))
        else:
            flash('Nome de usuário ou senha incorretos.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você foi deslogado.')
    return redirect(url_for('login'))

@app.route('/create_product', methods=['GET', 'POST'])
def create_product():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    sessions = conn.execute('SELECT * FROM Sessao').fetchall()
    conn.close()

    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        session_id = request.form['session_id']
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO Produtos (nome_produto, quantidade_produto, sessao_id) VALUES (?, ?, ?)',
            (name, quantity, session_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('create_product.html', sessions=sessions)

@app.route('/create_aisle', methods=['GET', 'POST'])
def create_aisle():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        aisle = request.form['aisle']
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO Sessao (nome_sessao, corredor_sessao) VALUES (?, ?)',
            (name, aisle)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('create_aisle.html')

@app.route('/update_aisle/<int:id>', methods=['GET', 'POST'])
def update_aisle(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    aisle = conn.execute('SELECT * FROM Sessao WHERE id_sessao = ?', (id,)).fetchone()

    if not aisle:
        conn.close()
        flash('Sessão não encontrada.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        aisle_number = request.form['aisle']
        conn.execute(
            'UPDATE Sessao SET nome_sessao = ?, corredor_sessao = ? WHERE id_sessao = ?',
            (name, aisle_number, id)
        )
        conn.commit()
        conn.close()
        flash('Sessão atualizada com sucesso!')
        return redirect(url_for('index'))

    conn.close()
    return render_template('update_aisle.html', aisle=aisle)

@app.route('/update_product/<int:id>', methods=['GET', 'POST'])
def update_product(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM Produtos WHERE id_produto = ?', (id,)).fetchone()
    sessions = conn.execute('SELECT * FROM Sessao').fetchall()

    if not product:
        conn.close()
        return 'Produto não encontrado', 404

    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        session_id = request.form['session_id']
        conn.execute(
            'UPDATE Produtos SET nome_produto = ?, quantidade_produto = ?, sessao_id = ? WHERE id_produto = ?',
            (name, quantity, session_id, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('update_product.html', product=product, sessions=sessions)

def can_delete_aisle(id):
    conn = get_db_connection()
    products = conn.execute('SELECT COUNT(*) as count FROM Produtos WHERE sessao_id = ?', (id,)).fetchone()
    conn.close()
    return products['count'] == 0

@app.route('/delete_aisle/<int:id>', methods=['POST'])
def delete_aisle(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if can_delete_aisle(id):
        conn = get_db_connection()
        conn.execute('DELETE FROM Sessao WHERE id_sessao = ?', (id,))
        conn.commit()
        conn.close()
        flash('Sessão excluída com sucesso!')
    else:
        flash('Não é possível excluir a sessão, pois há produtos relacionados a ela.')

    return redirect(url_for('index'))

@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM Produtos WHERE id_produto = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == 'app':
    create_tables()  
    app.run(debug=True)