from Crypto.PublicKey import ECC

from utils import *
from wallet import Wallet


class Main:

    def __init__(self):
        self.wallet = None

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

    def recreate_wallet(self, password):
        try:
            with open(f"storage\\private key.txt", 'r') as secret_key_file:
                protected_secret_key = secret_key_file.read()
                self.wallet = Wallet(ECC.import_key(protected_secret_key, passphrase=password))
        except ValueError:
            print("password doesn't match the protected private key that was provided.")
        except (IndexError, FileNotFoundError) as e:
            print("there is no wallet on this device.")


if __name__ == "__main__":
    main = Main()
    main.recreate_wallet("ronronron")
    # print(main.wallet)
    main.wallet.create_blockchain_file()
    print(main.wallet.blockchain)
    # main.create_wallet()
    # print(main.wallet)

