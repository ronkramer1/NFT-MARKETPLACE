import json
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS

from blockchain import Blockchain
from transaction import Transaction
from utils import *


class Wallet:
    def __init__(self, private_key=None, blockchain=Blockchain()):
        if not private_key:
            self.private_key = ECC.generate(curve=CURVE)
        else:
            self.private_key = private_key

        self.public_key = self.private_key.public_key()
        self.blockchain = blockchain

        self.transaction_pool = []
        self.proposed_blocks = []

    def sign_transaction(self, receiver, amount):
        sender = self.public_key.export_key(format=PUBLIC_KEY_FORMAT)
        fee = amount * FEE_CONSTANT
        hashed_transaction = sha256_hash(sender, receiver, amount, fee)
        signer = DSS.new(self.private_key, STANDARD_FOR_SIGNATURES)
        signature = signer.sign(hashed_transaction)
        return signature

    def verify_transaction(self, hashed_transaction, signature):
        verifier = DSS.new(self.public_key, STANDARD_FOR_SIGNATURES)
        return verifier.verify(hashed_transaction, signature)

    def make_transaction(self, receiver, amount):
        self.transaction_pool.append(Transaction(receiver, self.public_key.export_key(format=PUBLIC_KEY_FORMAT), amount,
                                                 self.sign_transaction(receiver, amount), amount * FEE_CONSTANT))

    def create_block(self):
        pass

    # blockchain file:
    def create_blockchain_file(self):
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

    def __str__(self):
        return f"secret_key: {self.private_key}\n" \
               + f"public_key: {self.public_key}\n" \
               + f"blockchain: {self.blockchain}\n"


if __name__ == "__main__":
    # wallet = Wallet()
    # wallet.create_blockchain_file()
    chain = Blockchain()
    for i in range(3):
        chain.create_block(Transaction())
    wallet = Wallet(chain)
    wallet.create_blockchain_file()
