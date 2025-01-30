from flask import request, jsonify, session, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import get_db_connection
import sqlite3
import jwt
import datetime

auth_routes = Blueprint("auth_routes", __name__)
SECRET_KEY = "sua_chave_secreta_super_segura"  # 🔐 Altere para um valor seguro!

def generate_jwt(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Expira em 1 hora
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def register_auth_routes(app):
    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json()
        username = data['username']
        password = data['password']
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO Usuarios (nome_usuario, senha) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'error': 'Username already exists'}), 400
        
        conn.close()
        return jsonify({'message': 'Registration successful'}), 201

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data['username']
        password = data['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Usuarios WHERE nome_usuario = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['senha'], password):
            session['user_id'] = user['id_usuario']
            session['username'] = user['nome_usuario']
            
            token_payload = {
                "user_id": session['user_id'],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expira em 1 hora
            }
            token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")

            return jsonify({
                "id_usuario": session['user_id'],
                "token": token
            }), 200
        
        return jsonify({"error": "Invalid username or password"}), 401
