import datetime
import hashlib
import json
import time

from Crypto.PublicKey import ECC
from Crypto.Signature import DSS

from transaction import Transaction
from utils import sha256_hash, STANDARD_FOR_SIGNATURES


class Block:
    def __init__(self, index=0, prev_hash="", data=Transaction(),
                 timestamp=str(datetime.datetime.now()), validator="", signature=""):
        self.index = index
        self.data = data
        self.timestamp = timestamp
        self.prev_hash = prev_hash
        self.validator = validator
        self.signature = signature

    def is_valid(self, blockchain):
        """returns true iff the block is valid"""
        if self != Block():  # allow the genesis block
            # check transactions:
            for transaction in self.data:
                if not transaction.is_valid(blockchain):
                    return False

            # check signature:
            serialized_data = []
            transaction = self.data
            serialized_data.append(transaction.serialize())  # serialize data so that it won't be an object, but a string
            hash_of_block_content = sha256_hash(self.index, self.prev_hash, serialized_data)
            verifier = DSS.new(ECC.import_key(self.validator), STANDARD_FOR_SIGNATURES)
            try:
                verifier.verify(hash_of_block_content, eval(self.signature))
            except ValueError:
                return False

            # check block number:
            if self.index != blockchain.chain[-1].block_number + 1:
                return False

            # check if everyone can pay all for all transactions in block:
            senders = {}
            for transaction in self.data:
                if transaction.sender not in senders:
                    senders[transaction.sender] = []
                senders[transaction.sender].append(transaction)

            for sender, transactions in senders.items():
                senders_balance = blockchain.get_balance(sender)
                total_amount = 0
                for transaction in transactions:
                    total_amount += (transaction.amount + transaction.fee)
                if total_amount > senders_balance:
                    return False

        return True

    def generate_hash(self):
        return sha256_hash(self.index, self.data, self.timestamp, self.prev_hash, self.validator, self.signature).\
            hexdigest()

    def serialize(self):
        block_dict = dict(self.__dict__)
        transaction = block_dict["data"]
        block_dict["data"] = transaction.__dict__
        return str(json.dumps(block_dict, indent=4))

    @staticmethod
    def deserialize(data):
        if type(data) == str:
            data_dict = json.loads(data)
        else:
            data_dict = data

        transaction = Transaction.deserialize(data_dict["data"])
        return Block(data_dict["index"],
                     data_dict["prev_hash"],
                     transaction,
                     data_dict["timestamp"],
                     data_dict["validator"],
                     data_dict["signature"])

    def __str__(self):
        return f"index: {self.index}\n" \
               + f"data: {self.data}\n" \
               + f"timestamp: {self.timestamp}\n" \
               + f"prev_hash: {self.prev_hash}\n" \
               + f"validator: {self.validator}\n" \
               + f"signature: {self.signature}\n"


def main():
    block = Block()
    print(block.serialize())


if __name__ == "__main__":
    main()
