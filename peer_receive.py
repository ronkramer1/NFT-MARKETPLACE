import time
from threading import Thread

from block import Block
from blockchain import Blockchain
from peer import Peer


# def generate_blocks():
#     block1 = Block()
#     print(str(block1))
#     time.sleep(1)
#     block2 = Block(1, 1000, block1.generate_hash())
#     print(str(block2))
#     time.sleep(1)
#     block3 = Block(2, 10000, block2.generate_hash())
#     print(str(block3))


def send_udp(peer):
    for i in range(10):
        peer.udp_send('transferred 0.1 KCN to Ron')


def receive_udp(peer):
    for i in range(1000):
        peer.constant_receive()


def main():
    # blockchain = Blockchain()
    # blockchain.create_block('transferred 0.1 KCN to Ron')
    # blockchain.create_block('received 100 KCN from Nadav')
    # blockchain.create_block('minted NFT bored ape')
    # print(blockchain)
    peer = Peer()
    receive_udp(peer)
    # t1 = Thread(target=send_udp, args=(peer, ))
    # t2 = Thread(target=receive_udp, args=(peer, ))
    #
    # t1.start()
    # t2.start()
    #
    # t1.join()
    # t2.join()


if __name__ == '__main__':
    main()
