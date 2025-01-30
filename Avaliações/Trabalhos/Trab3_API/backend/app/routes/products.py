from flask import Flask, request, jsonify, session
from app.models import get_db_connection
from app.utils.auth_utils import jwt_required
from flask import Blueprint
import jwt
from functools import wraps

SECRET_KEY = 'sua_chave_secreta_super_segura'

# Decorador para validar o token
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Extrair o token após "Bearer"

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        
        try:
            # Decodifica o JWT token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data['user_id']  # user_id do token gerado no login
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401
        
        # Armazenar o user_id na sessão para uso posterior
        session['user_id'] = current_user_id
        return f(*args, **kwargs)
    
    return decorated_function


product_routes = Blueprint("product_routes", __name__)

def register_product_routes(app):
    @app.route('/api/products', methods=['GET'])
    @token_required
    def get_products():
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        products = conn.execute('''SELECT Produtos.id_produto, Produtos.nome_produto, Produtos.quantidade_produto, 
                                          Sessao.nome_sessao, Sessao.corredor_sessao
                                   FROM Produtos
                                   JOIN Sessao ON Produtos.sessao_id = Sessao.id_sessao''').fetchall()
        
        products_list = [dict(product) for product in products]
        conn.close()
        return jsonify(products_list)

    @app.route('/api/products', methods=['POST'])
    @token_required 
    def create_product():
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        name = data['name']
        quantity = data['quantity']
        session_id = data['session_id']
        
        conn = get_db_connection()
        conn.execute('''INSERT INTO Produtos (nome_produto, quantidade_produto, sessao_id) 
                         VALUES (?, ?, ?)''', (name, quantity, session_id))
        product_id = conn.execute('SELECT LAST_INSERT_ROWID()').fetchone()[0]
    
        # Obter os dados do produto
        product = conn.execute('''SELECT id_produto, nome_produto, quantidade_produto, sessao_id
                                  FROM Produtos
                                  WHERE id_produto = ?''', (product_id,)).fetchone()
        
        conn.commit()
        conn.close()
        
        # Retornar os dados do produto inserido
        return jsonify({
            'id': product[0],
            'nome_produto': product[1],
            'quantidade_produto': product[2],
            'sessao_id': product[3],
            'message': 'Product created successfully'
        }), 201

    @app.route('/api/products/<int:product_id>', methods=['PUT'])
    @token_required
    def update_product(product_id):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        name = data.get('name')
        quantity = data.get('quantity')
        session_id = data.get('session_id')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''UPDATE Produtos
                          SET nome_produto = ?, quantidade_produto = ?, sessao_id = ?
                          WHERE id_produto = ?''', (name, quantity, session_id, product_id))

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Product not found'}), 404

        # Obtém os dados atualizados
        updated_product = cursor.execute('''SELECT id_produto, nome_produto, quantidade_produto, sessao_id
                                           FROM Produtos
                                           WHERE id_produto = ?''', (product_id,)).fetchone()

        conn.commit()
        conn.close()

        return jsonify({
            'id': updated_product[0],
            'nome_produto': updated_product[1],
            'quantidade_produto': updated_product[2],
            'sessao_id': updated_product[3],
            'message': 'Product updated successfully'
        }), 200

    @app.route('/api/products/<int:product_id>', methods=['DELETE'])
    @token_required
    def delete_product(product_id):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM Produtos WHERE id_produto = ?', (product_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Product not found'}), 404

        conn.commit()
        conn.close()
        return jsonify({'message': 'Product deleted successfully'}), 200
