import jwt
from flask import request, jsonify
from functools import wraps

SECRET_KEY = "sua_chave_secreta_super_segura"  # 🔐 Substitua por uma chave forte

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Token is missing"}), 401

        try:
            token = auth_header.split(" ")[1]  # Bearer <TOKEN>
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user_id = decoded_token["user_id"]  # Armazena o ID do usuário na request
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated_function
