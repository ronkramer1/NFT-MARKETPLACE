import datetime
import hashlib
import time


def generate_timestamp():
    return datetime.datetime.now()


class Block:
    def __init__(self, data=None, index=0, prev_hash=None):
        self.index = index
        self.data = data
        self.timestamp = generate_timestamp()
        self.prev_hash = prev_hash
        self.block_data = f"{self.data} - {self.prev_hash} - {self.timestamp}"

    def generate_hash(self):
        return hashlib.sha256(str(self.block_data).encode()).hexdigest()

    def __str__(self):
        # return '%s(%s)' % (
        #     type(self).__name__,
        #     ', '.join('%s=%s' % item for item in vars(self).items())
        # )
        # cls.__str__ = __str__
        # return cls
        return f"Block {self.index}: {self.block_data}"


def main():
    block1 = Block()
    print(str(block1))
    time.sleep(1)
    block2 = Block(1, 1000, block1.generate_hash())
    print(str(block2))
    time.sleep(1)
    block3 = Block(2, 10000, block2.generate_hash())
    print(str(block3))


if __name__ == '__main__':
    main()

