def create_tables():
    from .models import get_db_connection
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS Sessao(
        id_sessao INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_sessao TEXT NOT NULL,
        corredor_sessao TEXT NOT NULL
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS Produtos(
        id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_produto TEXT NOT NULL,
        quantidade_produto INTEGER NOT NULL,
        sessao_id INTEGER,
        FOREIGN KEY(sessao_id) REFERENCES Sessao(id_sessao)
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS Usuarios(
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()
