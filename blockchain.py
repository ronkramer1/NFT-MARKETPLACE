import json

from block import *


class Blockchain:
    def __init__(self, chain=None):
        if chain is None:
            chain = [Block()]
        self.chain = chain

    def create_block(self, data=None):
        index = self.chain[-1].index + 1
        prev_hash = self.chain[-1].generate_hash()
        self.chain.append(Block(data, index, prev_hash))

    def __str__(self):
        ret_str = ""
        for block in self.chain:
            ret_str += f"{block}\n"
        return ret_str[:-1]

    # def serialize(self):
    #     return str(json.dumps(self, default=lambda o: o.__dict__,
    #                        sort_keys=True, indent=4))

    def serialize(self):
        blockchain_dict = dict(self.__dict__)
        block_list = []
        for block in blockchain_dict["chain"]:
            block_dict = dict(block.__dict__)
            transaction_list = []
            transaction = block_dict["data"]
            transaction_list.append(transaction.__dict__)
            block_dict["data"] = transaction_list
            block_list.append(block_dict)
        blockchain_dict["chain"] = block_list
        return str(json.dumps(blockchain_dict, indent=4))

    @staticmethod
    def deserialize(data):
        data_dict = json.loads(data)
        block_list = []
        for block in data_dict["chain"]:
            block_list.append(Block.deserialize(block))
        return Blockchain(block_list)


def main():
    blockchain = Blockchain()
    for i in range(3):
        blockchain.create_block(Transaction())
    # print(first.__str__())
    # blockchain.create_parent_block()
    # print(blockchain)
    # print(blockchain.serialize())
    print(blockchain.serialize())


if __name__ == "__main__":
    main()
