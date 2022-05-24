from select import select

from Crypto.PublicKey import ECC

from block import Block
from peer import Peer
from transaction import Transaction
from utils import *
from wallet import Wallet

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc


class Main:

    def __init__(self):
        self.wallet = None
        self.peer = Peer()
        self.finished_collecting_missing_blocks_by_button = False  # for checking if finished collecting missing blocks
        self.is_validator = False

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

    # block handling:
    def handle_blocks(self):
        """calls add_blocks_to_chain and make_blocks"""
        self.add_blocks_to_chain()
        self.make_blocks()

    def add_blocks_to_chain(self):
        """tries to add a block to chain, and keeps calling itself every five seconds"""
        if self.wallet.add_a_block_to_chain():
            # checking if validator now:
            if self.wallet.public_key.export_key(
                    format=PUBLIC_KEY_FORMAT) in self.wallet.blockchain.get_validators():
                self.is_validator = True
            else:
                self.is_validator = False

            # clearing trees:
            # self.ui.transaction_pool_tree.clear()
            # self.ui.proposed_blocks_tree.clear()

            # update blockchain file and blockchain tree:
            self.update_blockchain_file()
            with open(f"storage\\blockchain.json", "r") as blockchain_file:
                pass
                # self.put_json_chain_on_tree(blockchain_file)

        qtc.QTimer.singleShot(10000, self.add_blocks_to_chain)

    def make_blocks(self):
        """tries to make a block and send it, calls itself every five seconds"""
        new_block = self.wallet.make_block()
        if self.is_validator and new_block:
            self.peer.udp_send(new_block)
            # self.ui.transaction_pool_tree.clear()

        qtc.QTimer.singleShot(5000, self.make_blocks)

    # networking:
    def send_transaction(self):
        """sends a transaction, the data for the transaction is provided by the user"""
        password = self.ui.transaction_password_in.text()
        with open(f"storage\\private key.txt", 'r') as secret_key_file:
            protected_secret_key = secret_key_file.read()
            try:
                Wallet(ECC.import_key(protected_secret_key, passphrase=password))
            except ValueError:
                qtw.QMessageBox.critical(None, 'Fail',
                                         "password doesn't match the protected private key that was provided.")
                return

            selected_contacts = self.ui.contacts_list.selectedItems()
            if not selected_contacts:
                qtw.QMessageBox.critical(None, 'Fail', "no contact was selected.")
                return

            for receiver in selected_contacts:
                try:
                    receiver = receiver.text().split(": ")[-1]
                except AttributeError:
                    qtw.QMessageBox.critical(None, 'Fail', "no contact selected.")
                    return

                try:
                    amount = float(self.ui.amount_text_incer.text())
                except ValueError:
                    qtw.QMessageBox.critical(None, 'Fail', "amount must be a number.")
                    return

                if (amount > 0) or (receiver == STAKE_ADDRESS and amount != 0):
                    transaction = self.wallet.make_transaction(receiver, amount)
                    if transaction:
                        self.peer.udp_send(transaction)
                        qtw.QMessageBox.information(None, 'Success', "successfully sent the transaction.")
                    else:
                        qtw.QMessageBox.critical(None, 'Fail',
                                                 "you don't have enough coins to complete this transaction.")
                else:
                    qtw.QMessageBox.critical(None, 'Fail',
                                             "amount must be more than zero when not retrieving coins from stake, or different to zero when retrieving or staking coins.")

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
        while True:
            if self.peer.tcp_client:
                rlist, wlist, xlist = select([self.peer.udp_receiver, self.peer.tcp_client], [], [], 0.01)
            else:
                rlist, wlist, xlist = select([self.peer.udp_receiver], [], [], 0.01)
            for sock in rlist:
                if sock == self.peer.udp_receiver:
                    received_message = self.peer.udp_receive()
                    print(received_message)
                    self.received_from_udp_socket(received_message)

                if sock == self.peer.tcp_client:
                    try:
                        received_message = sock.recv(RECV_SIZE).decode()
                        print(received_message)
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
                pass
                # self.add_transaction_to_pool_tree(message)
        elif type(message) == Block:
            self.wallet.add_proposed_block(message)
            # self.add_block_to_proposed_tree(message)
        elif type(message) == str and message[:len("connected")] == "connected":
            self.send_a_missing_block(self.wallet.blockchain.chain[-1].index)
        else:
            print(message)

    def send_a_missing_block(self, position):
        """sends a block that might be missing for a newly connected peer on tcp"""
        block_to_send = [block for block in self.wallet.blockchain.chain if block.index == position][0]
        self.peer.tcp_client_send(block_to_send)

    def request_missing_blocks(self):
        """starts requesting blocks that might be missing"""
        self.collect_blocks()

    def finish_entering_wallet(self):
        """shows the menu_frame, and setting up the gui with all information from the wallet"""
        # self.ui.menu_frame.show()  # show the navigation menu after a wallet is created
        # self.ui.stackedWidget.setCurrentWidget(self.ui.my_wallet_pg)  # go to "my wallet" page
        # self.ui.public_key_lbl.setText(self.wallet.public_key.export_key(format=PUBLIC_KEY_FORMAT))
        # self.create_blockchain_file()
        # self.ui.current_balance_lbl.setText(str(self.wallet.get_balance()))
        # try:
        #     self.ui.current_stake_lbl.setText(str(self.wallet.blockchain.get_validators()[
        #                                               self.wallet.public_key.export_key(format=PUBLIC_KEY_FORMAT)]))
        # except KeyError:
        #     self.ui.current_stake_lbl.setText('0')
        #
        # with open(f"storage\\blockchain.json", "r") as blockchain_file:
        #     self.put_json_chain_on_tree(blockchain_file)

        if self.wallet.public_key.export_key(format=PUBLIC_KEY_FORMAT) in self.wallet.blockchain.get_validators():
            self.is_validator = True
        else:
            self.is_validator = False

        # with open(f"storage\\private key.txt", 'r') as secret_key_file:
        #     self.ui.protected_private_key_lbl.setText(secret_key_file.read())

        self.handle_blocks()
        self.constant_receive()

    def update_blockchain_file(self):
        """updates the blockchain file with data from wallet"""
        with open(f"storage\\blockchain.json", "w") as blockchain_file:
            blockchain_file.write(self.wallet.blockchain.serialize())
        # self.ui.current_balance_lbl.setText(str(self.wallet.get_balance()))
        try:
            pass
            # self.ui.current_stake_lbl.setText(str(self.wallet.blockchain.get_validators()[self.wallet.public_key.export_key(format=PUBLIC_KEY_FORMAT)]))
        except KeyError:
            pass
            # self.ui.current_stake_lbl.setText('0')

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

    def stop_waiting_for_blocks(self):
        """stops waiting for blocks"""
        self.finished_collecting_missing_blocks_by_button = True

    def handle_collected_blocks(self, collected_blocks_lists_list):
        """decides which of the collected blocks should be believed to, and adds them to the blockchain"""
        if collected_blocks_lists_list:
            valid_collected_blocks_lists_list = []
            for collected_blocks_lists in collected_blocks_lists_list:
                for collected_block in collected_blocks_lists:
                    if collected_block.is_valid(self.wallet.blockchain):
                        valid_collected_blocks_lists_list.append(collected_blocks_lists)

            valid_collected_blocks_lists_list_tuples = []
            for valid_collected_blocks_lists in valid_collected_blocks_lists_list:
                valid_collected_blocks_list_tuples = []
                for valid_collected_block in valid_collected_blocks_lists:
                    valid_collected_blocks_list_tuples.append(
                        (valid_collected_block.block_number, valid_collected_block.hash_block))
                valid_collected_blocks_lists_list_tuples.append(valid_collected_blocks_list_tuples)

            correct_valid_collected_blocks_list_tuples = most_frequent(valid_collected_blocks_lists_list_tuples)
            index_of_correct_valid_collected_blocks_list = valid_collected_blocks_lists_list_tuples.index(
                correct_valid_collected_blocks_list_tuples)
            correct_valid_collected_blocks_list = valid_collected_blocks_lists_list[
                index_of_correct_valid_collected_blocks_list]

            for correct_valid_collected_block in correct_valid_collected_blocks_list:
                self.wallet.add_proposed_block(correct_valid_collected_block)
                if not self.wallet.add_a_block_to_chain():
                    self.request_missing_blocks()

            with open(f"storage\\blockchain.json", "w") as blockchain_file:
                pass


if __name__ == "__main__":
    main = Main()
    main_wallet = main.recreate_wallet("ronronron")
    second_wallet = main.recreate_wallet2("hello")
    main_wallet.create_blockchain_file()
    second_wallet.create_blockchain_file()
    # main.peer.udp_send(Block())
    print(main.constant_receive())
    print(main.wallet.blockchain)

    # second_wallet.make_transaction_and_add_to_blockchain(STAKE_ADDRESS,
    #                                                    55)

    # print(main_wallet.blockchain)
    # print(main_wallet.choose_validator())
