from Crypto.PublicKey import ECC

from utils import *
from wallet import Wallet


class Main:

    def __init__(self):
        self.wallet = None

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
