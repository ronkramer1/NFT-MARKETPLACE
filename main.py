from select import select

from Crypto.PublicKey import ECC

from block import Block
from peer import Peer
from transaction import Transaction
from utils import *
from wallet import Wallet

from PyQt5 import QtCore as qtc


class Main:

    def __init__(self):
        self.wallet = None
        self.peer = Peer()

    def create_wallet2(self):
        self.wallet = Wallet()
        password = "hello"
        with open(f"storage\\private key 2.txt", 'w') as private_key_file:
            if password:
                private_key_file.write(self.wallet.private_key.export_key(format=PRIVATE_KEY_FORMAT,
                                                                          passphrase=password,
                                                                          protection=PRIVATE_KEY_PROTECTION))
            else:
                private_key_file.write(self.wallet.private_key.export_key(format=PRIVATE_KEY_FORMAT,
                                                                          protection=PRIVATE_KEY_PROTECTION))

        return self.wallet

    def create_wallet(self):
        self.wallet = Wallet()
        password = "ronronron"
        with open(f"storage\\private key.txt", 'w') as private_key_file:
            if password:
                private_key_file.write(self.wallet.private_key.export_key(format=PRIVATE_KEY_FORMAT,
                                                                          passphrase=password,
                                                                          protection=PRIVATE_KEY_PROTECTION))
            else:
                private_key_file.write(self.wallet.private_key.export_key(format=PRIVATE_KEY_FORMAT,
                                                                          protection=PRIVATE_KEY_PROTECTION))
        return self.wallet

    def recreate_wallet(self, password):
        try:
            with open(f"storage\\private key.txt", 'r') as secret_key_file:
                protected_secret_key = secret_key_file.read()
                self.wallet = Wallet(ECC.import_key(protected_secret_key, passphrase=password))
        except ValueError:
            print("password doesn't match the protected private key that was provided.")
        except (IndexError, FileNotFoundError) as e:
            print("there is no wallet on this device.")

        return self.wallet

    def recreate_wallet2(self, password):
        try:
            with open(f"storage\\private key 2.txt", 'r') as secret_key_file:
                protected_secret_key = secret_key_file.read()
                self.wallet = Wallet(ECC.import_key(protected_secret_key, passphrase=password))
        except ValueError:
            print("password doesn't match the protected private key that was provided.")
        except (IndexError, FileNotFoundError) as e:
            print("there is no wallet on this device.")

        return self.wallet

    def constant_receive(self):
        """tries to receive messages from other peers (both tcp and udp), calls itself every 0.1 seconds"""
        if self.peer.tcp_client:
            rlist, wlist, xlist = select([self.peer.udp_receiver, self.peer.tcp_client], [], [], 0.01)
        else:
            rlist, wlist, xlist = select([self.peer.udp_receiver], [], [], 0.01)
        for sock in rlist:
            if sock == self.peer.udp_receiver:
                received_message = self.peer.udp_receive()
                self.received_from_udp_socket(received_message)

            if sock == self.peer.tcp_client:
                try:
                    received_message = sock.recv(RECV_SIZE).decode()
                except ConnectionResetError:
                    received_message = ''
                if received_message[:len("position ")] == "position ":
                    block_position_from_end_of_chain_to_send = int(received_message[len("position "):])
                    self.send_a_missing_block(block_position_from_end_of_chain_to_send)
                elif received_message[len("finished"):] == "finished" or received_message == '':
                    self.peer.close_client()

        qtc.QTimer.singleShot(100, self.constant_receive)

    def received_from_udp_socket(self, message):
        """handles a message that was received by the udp receiver socket"""
        if type(message) == Transaction:
            if self.wallet.add_transaction_to_pool(message):
                self.add_transaction_to_pool_tree(message)
        elif type(message) == Block:
            self.wallet.add_proposed_block(message)
            self.add_block_to_proposed_tree(message)
        elif type(message) == str and message[:len("connected")] == "connected":
            self.send_a_missing_block(self.wallet.blockchain.chain[-1].block_number)
        else:
            print(message)

    def send_a_missing_block(self, position):
        """sends a block that might be missing for a newly connected peer on tcp"""
        block_to_send = [block for block in self.wallet.blockchain.chain if block.block_number == position][0]
        self.peer.tcp_client_send(block_to_send)

    def request_missing_blocks(self):
        """starts requesting blocks that might be missing"""
        self.collect_blocks()

    def collect_blocks(self):
        """collects blocks that might be missing from other peers"""
        missing_blocks_by_peer = {}
        self.peer.request_update_connection()
        finished_so_far = 0
        tcp_connected_peers = []
        finished_collecting_missing_blocks = False

        def collect_blocks_networking():
            nonlocal finished_so_far
            nonlocal tcp_connected_peers
            nonlocal finished_collecting_missing_blocks

            rlist, wlist, xlist = [], [], []
            if len(tcp_connected_peers) <= NUMBER_OF_CONNECTED_CLIENTS:
                rlist, wlist, xlist = select([self.peer.tcp_server] + tcp_connected_peers, [], [], 0.01)
            for sock in rlist:
                if sock == self.peer.tcp_server:
                    (new_sock, address) = self.peer.tcp_server.accept()
                    tcp_connected_peers.append(new_sock)

                elif sock in tcp_connected_peers:
                    received_message = sock.recv(RECV_SIZE).decode()
                    if received_message[:len("Block: ")] == "Block: ":
                        received_message = received_message[len("Block: "):]
                        received_block = Block.deserialize(received_message)
                        if received_block.block_number not in [block.block_number for block in self.wallet.blockchain.chain]:  # if block number isn't alewady in chain
                            if sock not in missing_blocks_by_peer:
                                missing_blocks_by_peer[sock] = []
                            missing_blocks_by_peer[sock].append(received_block)
                            sock.send(f"position {received_block.block_number - 1}".encode('utf-8'))
                        else:
                            sock.send("finished".encode('utf-8'))
                            finished_so_far += 1
                            if finished_so_far >= NUMBER_OF_CONNECTED_CLIENTS:
                                finished_collecting_missing_blocks = True

                    elif received_message == '':
                        tcp_connected_peers.remove(sock)

                    else:
                        print(received_message)

            if not (self.finished_collecting_missing_blocks_by_button or finished_collecting_missing_blocks):
                qtc.QTimer.singleShot(1000, collect_blocks_networking)
            else:
                tcp_connected_peers = []
                self.peer.close_server()
                if finished_collecting_missing_blocks:
                    self.handle_collected_blocks(list(missing_blocks_by_peer.values()))
                self.finish_entering_wallet()

        collect_blocks_networking()



if __name__ == "__main__":
    main = Main()
    main_wallet = main.recreate_wallet("ronronron")
    second_wallet = main.recreate_wallet2("hello")
    main_wallet.create_blockchain_file()
    second_wallet.create_blockchain_file()

    # second_wallet.make_transaction_and_add_to_blockchain(STAKE_ADDRESS,
    #                                                    55)

    # print(main_wallet.blockchain)
    print(main_wallet.choose_validator())
