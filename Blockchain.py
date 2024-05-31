import hashlib
import json
from time import time
from flask import Flask, jsonify, request
from uuid import uuid4

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.ongs = []
        self.donation_limit = None
        self.total_donations = 0.0

        genesis_block = self.create_block(proof=100, previous_hash='1')
        genesis_block['hash'] = self.hash(genesis_block)
        self.chain[-1] = genesis_block

    def create_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            'hash': ''  # Este campo se actualizará después
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def add_transaction(self, donor, beneficiary, amount):
        amount = float(amount)
        if self.donation_limit is None:
            return False, f"Se debe fijar una cantidad limite de donaciones"
        if self.donation_limit is not None and float(self.total_donations) + amount > float(self.donation_limit):
            return False, f"Se ha alcanzado el limite de donaciones  {self.donation_limit}"
        
        self.current_transactions.append({
            'donor': donor,
            'beneficiary': beneficiary,
            'amount': amount,
        })
        self.total_donations += amount
        return True, self.last_block['index'] + 1
    

    def add_ong(self, name, address):
        self.ongs.append({
            'name': name,
            'address': address,
        })

    def distribute_funds(self):
        if self.total_donations == 0:
            return False, f'No hay fondos suficientes para ser distribuidos'
        if not self.ongs :
            return False, f'No hay ONG para distribuir las donaciones'

        amount_per_ong = self.total_donations / len(self.ongs)
        for ong in self.ongs:
            self.add_transaction('Platform', ong['address'], amount_per_ong)
        
        self.total_donations = 0
        return True

    def set_donation_limit(self, limit):
        self.donation_limit = limit

    def validate_chain(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block['previous_hash'] != self.hash(previous_block):
                return False

            if not self.valid_proof(previous_block['proof'], current_block['proof']):
                return False

        return True

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    
    
