import json

from Crypto.PublicKey import ECC

from nft import NFT
from utils import *


class Transaction:
    def __init__(self, nft=None, receiver=STAKE_ADDRESS, sender="", amount=NUMBER_OF_COINS, signature=""):
        self.nft = nft
        self.receiver = receiver
        self.sender = sender
        self.amount = amount
        self.signature = signature
        self.fee = float(self.amount * FEE_CONSTANT / 100)

    def is_valid(self, blockchain):
        """returns true if the transaction is valid"""
        if not (self.serialize() == Transaction().serialize() and self in blockchain.chain[0].data):  # unless initial transaction for initial coin offering
            # check signature against sender and rest of transaction:
            hash_of_transaction = self.generate_hash()
            verifier = DSS.new(ECC.import_key(self.sender), STANDARD_FOR_SIGNATURES)
            try:
                verifier.verify(hash_of_transaction, self.signature.encode())
            except ValueError:
                return False

            # check if the receiver and sender are valid (if it's a point on the elliptic curve):
            # is receiver valid:
            if self.receiver != STAKE_ADDRESS:
                receiver_key = ECC.import_key(self.receiver)
                try:
                    x = int(receiver_key.pointQ.x)
                    y = int(receiver_key.pointQ.y)
                except AttributeError:
                    return False
                if ((y ** 2) - ((x ** 3) - (a * x) + b)) % p == 0:
                    return False

            # is sender valid:
            sender_key = ECC.import_key(self.sender)
            try:
                x = int(sender_key.pointQ.x)
                y = int(sender_key.pointQ.y)
            except AttributeError:
                return False
            if ((y ** 2) - ((x ** 3) - (a * x) + b)) % p == 0:
                return False

            # check if fee is valid:
            if float(self.fee) != float(self.amount * FEE_CONSTANT / 100):
                return False

            # check if amount is more than 0, or different than zero in case of retrieving stake:
            if (self.receiver != STAKE_ADDRESS and float(self.amount) <= 0) or (self.receiver == STAKE_ADDRESS and float(self.amount) == 0):
                return False

            # check if the amount can be sent by sender:
            if blockchain.get_balance(self.sender) < (float(self.amount) + float(self.fee)):
                return False

            if (self.receiver == STAKE_ADDRESS) and (self.amount < 0) and (blockchain.get_validators()[self.sender] < -self.amount):
                return False

            # check if transaction is a duplicate of an existing transaction:
            for block in blockchain.chain:
                for transaction in block.data:
                    if transaction == self:
                        return False

        print("transaction valid")
        return True

    def generate_hash(self):
        """returns a hash of the sender, receiver, amount, and fee"""
        return sha256_hash(self.nft, self.sender, self.receiver, self.amount, self.fee)

    def serialize(self):
        transaction_dict = self.__dict__
        if not transaction_dict["nft"]:
            transaction_dict = {
                "receiver": self.receiver,
                "sender": self.sender,
                "amount": self.amount,
                "signature": self.signature,
                "fee": self.fee
            }
        return str(json.dumps(transaction_dict, indent=4))

    @staticmethod
    def deserialize(data):
        data_dict = {}
        if type(data) == str:
            data_dict = json.loads(data)
            print(data_dict)
        elif type(data) == dict:
            data_dict = data

        try:
            return Transaction(data_dict["nft"],
                               data_dict["receiver"],
                               data_dict["sender"],
                               data_dict["amount"],
                               data_dict["signature"])
        except KeyError:
            return Transaction(None,
                               data_dict["receiver"],
                               data_dict["sender"],
                               data_dict["amount"],
                               data_dict["signature"])

    def __str__(self):
        if self.nft:
            return f"nft: {self.nft}\n" \
                   + f"signature: {self.signature}\n" \
                   + f"sender: {self.sender}\n" \
                   + f"receiver: {self.receiver}\n" \
                   + f"amount: {self.amount}\n" \
                   + f"fee: {self.fee}\n"

        return f"signature: {self.signature}\n" \
               + f"sender: {self.sender}\n" \
               + f"receiver: {self.receiver}\n" \
               + f"amount: {self.amount}\n" \
               + f"fee: {self.fee}\n"
