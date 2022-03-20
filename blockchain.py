from block import *

def main():
    first = Block(0, 100, 123)
    print(first.__str__())
    # blockchain = Blockchain
    # blockchain.create_parent_block()
    # print(blockchain.blockchain)


class Blockchain:
    def __init__(self):
        self.chain = [Block()]

    def create_block(self, data=None):
        index = self.chain[-1].index + 1
        prev_hash = self.chain[-1].generate_hash()
        self.chain.append(Block(data, index, prev_hash))

    def __str__(self):
        ret_str = ""
        for block in self.chain:
            ret_str += f"{block}\n"
        return ret_str[:-1]



