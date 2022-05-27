import json
import random

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

    def sign_transaction(self, receiver, amount, nft=None):
        sender = self.public_key.export_key(format=PUBLIC_KEY_FORMAT)
        fee = amount * FEE_CONSTANT
        transaction_hash = sha256_hash(nft, sender, receiver, amount, fee)
        signer = DSS.new(self.private_key, STANDARD_FOR_SIGNATURES)
        signature = str(signer.sign(transaction_hash))
        return signature

    def sign_block(self, block):
        block_hash = sha256_hash(block.index, block.prev_hash, block.data.serialize())
        signer = DSS.new(self.private_key, STANDARD_FOR_SIGNATURES)
        signature = str(signer.sign(block_hash))
        return signature

    def make_transaction(self, receiver, amount, nft=None):
        sender = self.public_key.export_key(format=PUBLIC_KEY_FORMAT)
        fee = amount * FEE_CONSTANT
        if self.get_balance() >= amount + fee:
            transaction_hash = sha256_hash(nft, sender, receiver, amount, fee)
            signer = DSS.new(self.private_key, STANDARD_FOR_SIGNATURES)
            signature = str(signer.sign(transaction_hash))
            transaction = Transaction(nft, receiver, sender, amount, signature)
            # self.transaction_pool.append(transaction)
            return transaction

        return False

    def create_block(self):
        if len(self.transaction_pool) >= NUM_OF_TRANSACTIONS_IN_BLOCK:
            block = self.blockchain.create_block(self.transaction_pool[-1])
            block_hash = sha256_hash(block.index, block.prev_hash, block.data.serialize())
            signer = DSS.new(self.private_key, STANDARD_FOR_SIGNATURES)
            signature = str(signer.sign(block_hash))
            block.validator = self.public_key.export_key(format=PUBLIC_KEY_FORMAT)
            block.signature = signature
            self.transaction_pool = []
            return block

    def choose_validator(self):
        validators = self.blockchain.get_validators_dict()
        total_staked = sum(validators.values())
        weights = []

        for validator in validators:
            weights.append(float(validators[validator] / total_staked))

        if not validators:
            print("error, no validators.")

        else:
            selected_validator = random.choices(list(validators.keys()), weights=weights, k=1)[0]
            return selected_validator

        # return selected_validator, validators[selected_validator]

    def add_proposed_block(self, block):
        """adds a block the the proposed blocks list"""
        self.proposed_blocks.append(block)

    def add_a_block_to_chain(self):
        """adds a block from the proposed blocks to the blockchain iff the block is valid and its validator is the current leader, also empties the transaction pool and the proposed blocks list"""
        # if len(self.proposed_blocks) > 10:
        current_leader = self.choose_validator()
        for block in self.proposed_blocks:
            if block.is_valid(self.blockchain):  # and block.validator == current_leader:
                self.blockchain.chain.append(block)
                self.transaction_pool = []
                self.proposed_blocks = []
                return True
        return False

    def get_balance(self):
        return self.blockchain.get_balance(self.public_key.export_key(format=PUBLIC_KEY_FORMAT))

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
        try:
            with open("storage\\blockchain.json", "r") as blockchain_file:
                self.blockchain = Blockchain.deserialize(blockchain_file.read())
        except (IOError, json.decoder.JSONDecodeError):
            print("file is empty")

    def write_to_file(self):
        with open(f"storage\\blockchain.json", "w") as blockchain_file:
            blockchain_file.write(self.blockchain.serialize())

    def make_transaction_and_add_to_blockchain(self, receiver, amount):
        self.make_transaction(receiver, amount)
        self.create_block()
        self.write_to_file()

    def __str__(self):
        return f"secret_key: {self.private_key}\n" \
               + f"public_key: {self.public_key}\n" \
               + f"blockchain: {self.blockchain}\n"
