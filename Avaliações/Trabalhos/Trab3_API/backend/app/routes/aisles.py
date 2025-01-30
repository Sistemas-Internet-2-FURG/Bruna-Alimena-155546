from flask import Flask, request, jsonify, session
from app.models import get_db_connection
import jwt
from functools import wraps
SECRET_KEY = 'sua_chave_secreta_super_segura'
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
        
        # Armazenar o user_id para uso posterior
        kwargs['user_id'] = current_user_id
        return f(*args, **kwargs)
    
    return decorated_function


def register_aisle_routes(app):
    @app.route('/api/aisles', methods=['POST'])
    @token_required
    def create_aisle():
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        name = data['name']
        aisle = data['aisle']
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO Sessao (nome_sessao, corredor_sessao) 
            VALUES (?, ?)''', (name, aisle))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Aisle created successfully'}), 201
    @app.route('/api/aisles/<int:aisle_id>', methods=['PUT'])
    @token_required
    def update_aisle(aisle_id):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        name = data.get('name')
        aisle = data.get('aisle')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE Sessao
            SET nome_sessao = ?, corredor_sessao = ?
            WHERE id_sessao = ?
        ''', (name, aisle, aisle_id))

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Aisle not found'}), 404

        # Obtém os dados atualizados
        updated_aisle = cursor.execute('''
            SELECT id_sessao, nome_sessao, corredor_sessao
            FROM Sessao
            WHERE id_sessao = ?
        ''', (aisle_id,)).fetchone()

        conn.commit()
        conn.close()

        return jsonify({
            'id': updated_aisle[0],
            'nome_sessao': updated_aisle[1],
            'corredor_sessao': updated_aisle[2],
            'message': 'Aisle updated successfully'
        }), 200

    @app.route('/api/aisles/<int:aisle_id>', methods=['DELETE'])
    @token_required
    def delete_aisle(aisle_id):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se há produtos associados ao corredor
        cursor.execute('SELECT COUNT(*) FROM Produtos WHERE sessao_id = ?', (aisle_id,))
        product_count = cursor.fetchone()[0]

        if product_count > 0:
            conn.close()
            return jsonify({'error': 'Cannot delete aisle with products'}), 400

        # Exclui o corredor
        cursor.execute('DELETE FROM Sessao WHERE id_sessao = ?', (aisle_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Aisle not found'}), 404

        conn.commit()
        conn.close()
        return jsonify({'message': 'Aisle deleted successfully'}), 200

    
