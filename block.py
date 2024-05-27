from flask import Flask, jsonify, request
from Blockchain import Blockchain
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
# Instanciar la Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # No hay recompensa en este ejemplo simplificado

    previous_hash = last_block['hash']
    block = blockchain.create_block(proof, previous_hash)
    block['hash'] = blockchain.hash(block)
    blockchain.chain[-1] = block  # Actualizar el bloque con su hash

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'hash': block['hash']   
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['donor', 'beneficiary', 'amount']
    if not all(k in values for k in required):
        return 'Campos requeridos', 400

    success, message = blockchain.add_transaction(values['donor'], values['beneficiary'], values['amount'])
    if not success:
        return jsonify({'message': message}), 400
    response = {'message': f'La transacción se agregará al bloque {message}'}
    return jsonify(response), 201

@app.route('/ongs/new', methods=['POST'])
def new_ong():
    values = request.get_json()
    required = ['name', 'address']
    if not all(k in values for k in required):
        return 'Los Campos son requeridos.', 400
    blockchain.add_ong(values['name'], values['address'])
    response = {'message': 'Ong registrada correctamente.'}
    return jsonify(response), 201

@app.route('/ongs', methods=['GET'])
def get_ongs():
    response = {
        'ongs': blockchain.ongs
    }
    return jsonify(response), 200

@app.route('/distribute', methods=['GET'])
def distribute():
    success = blockchain.distribute_funds()
    if not success:
        return jsonify({'message': 'No funds to distribute or no ONGs available'}), 400
    return jsonify({'message': 'Funds distributed successfully'}), 200

@app.route('/set_limit', methods=['POST'])
def set_limit():
    values = request.get_json()
    required = ['limit']
    if 'limit' not in values:
        return 'Limite es requerido', 400
    blockchain.set_donation_limit(values['limit'])
    response = {'message': 'Limite de donacion creado correctamente'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/donation_info', methods=['GET'])
def get_donation_info():
    # Calcula la cantidad total donada sumando las cantidades de todas las transacciones en la cadena
    total_donations = sum(
        transaction['amount'] 
        for block in blockchain.chain 
        for transaction in block['transactions'] 
        if transaction['donor'] != 'Platform'
    )
    # Obtiene el límite de donaciones de la cadena de bloques
    donation_limit = blockchain.donation_limit
    
    # Devuelve la cantidad total donada y el límite de donaciones como un JSON
    return jsonify({
        'total_donations': total_donations,
        'donation_limit': donation_limit
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
