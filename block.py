import datetime
import hashlib
import json
import time

from transaction import Transaction
from utils import sha256_hash


class Block:
    def __init__(self, index=0, prev_hash="", data=Transaction(),
                 timestamp=str(datetime.datetime.now()), validator="", signature=""):
        self.index = index
        self.data = data
        self.timestamp = timestamp
        self.prev_hash = prev_hash
        self.validator = validator
        self.signature = signature

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
