import json

from crypto.PublicKey import ECC
from blockchain import Blockchain
from utils import *


class Wallet:
    def __init__(self, blockchain=Blockchain()):
        self.private_key = ECC.generate(curve=CURVE)
        self.public_key = self.private_key.public_key()
        self.blockchain = blockchain

        self.transaction_pool = []
        self.proposed_blocks = []

    # blockchain file:
    def create_blockchain_file(self):
        """creates a blockchain file from blockchain in wallet"""
        try:
            with open("storage\\blockchain.json", "r+") as blockchain_file:
                if type(json.load(blockchain_file)) != dict:
                    blockchain_file.seek(0)
                    json.dump(self.blockchain.serialize(), blockchain_file, indent=4)
        except (IOError, json.decoder.JSONDecodeError):
            with open("storage\\blockchain.json", "w") as blockchain_file:
                blockchain_file.write(self.blockchain.serialize())
        with open("storage\\blockchain.json", "r") as blockchain_file:
            self.blockchain = Blockchain.deserialize(blockchain_file.read())
