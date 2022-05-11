import datetime
import hashlib
import json
import time

from transaction import Transaction


class Block:
    def __init__(self, index=0, prev_hash="", data=Transaction(),
                 timestamp=str(datetime.datetime.now()), validator="", signature=""):
        self.index = index
        self.data = data
        self.timestamp = timestamp
        self.prev_hash = prev_hash
        self.block_data = f"{self.data} - {self.prev_hash} - {self.timestamp}"
        self.validator = validator
        self.signature = signature
        # self.index = index
        # self.data = data
        # # self.timestamp = generate_timestamp()
        # self.prev_hash = prev_hash
        # self.block_data = f"{self.data} - {self.prev_hash}"

    def generate_hash(self):
        return hashlib.sha256(str(self.block_data).encode()).hexdigest()

    def serialize(self):
        """returns a (json) string representation of the block"""
        block_dict = dict(self.__dict__)
        transaction_list = []
        for transaction in block_dict["data"]:
            transaction_list.append(transaction.__dict__)
        block_dict["data"] = transaction_list
        return str(json.dumps(block_dict, indent=4))

    @staticmethod
    def deserialize(data):
        """takes a json representation of a block and returns the represented block"""
        if type(data) == str:
            data_dict = json.loads(data)
        else:
            data_dict = data
        transaction_list = []
        for transaction in data_dict["data"]:
            transaction_list.append(Transaction.deserialize(transaction))
        return Block(data_dict["index"],
                     data_dict["prev_hash"],
                     transaction_list,
                     data_dict["timestamp"])
                     # data_dict["validator"],
                     # data_dict["signature"])


    def __str__(self):
        # return '%s(%s)' % (
        #     type(self).__name__,
        #     ', '.join('%s=%s' % item for item in vars(self).items())
        # )
        # cls.__str__ = __str__
        # return cls
        return f"Block {self.index}: {self.block_data}"


def main():
    block = Block()
    print(block.serialize())


if __name__ == "__main__":
    main()
