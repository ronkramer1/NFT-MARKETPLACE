import json

from nft import NFT
from utils import *


class Transaction:
    def __init__(self, nft=None, receiver=STAKE_ADDRESS, sender="", amount=NUMBER_OF_COINS, signature=""):
        self.nft = nft
        self.receiver = receiver
        self.sender = sender
        self.amount = amount
        self.signature = signature
        self.fee = float(amount * FEE_CONSTANT / 100)

    def validate_transaction(self, blockchain):
        if not (blockchain.get_balance(self.sender) >= self.amount + self.fee):
            return False
        return True

    def serialize(self):
        transaction_dict = json.dumps(self.__dict__, indent=4)
        print(transaction_dict)
        for value in transaction_dict:
            print(value)
        return str(transaction_dict)

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
