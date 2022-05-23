import json

from utils import *


class Transaction:
    def __init__(self, receiver="", sender="", amount=NUMBER_OF_COINS, signature=""):
        self.amount = amount
        self.sender = sender
        self.receiver = receiver
        self.signature = signature
        self.fee = float(amount * FEE_CONSTANT / 100)

    def validate_transaction(self, blockchain):
        if not (blockchain.get_balance(self.sender) >= self.amount + self.fee):
            return False
        return True

    def serialize(self):
        return str(json.dumps(self.__dict__, indent=4))

    @staticmethod
    def deserialize(data):
        if type(data) == str:
            data_dict = json.loads(data)
            print(data_dict)
        elif type(data) == dict:
            data_dict = data
        return Transaction(data_dict["receiver"],
                           data_dict["sender"],
                           data_dict["amount"],
                           data_dict["signature"])

    def __str__(self):
        return f"signature: {self.signature}\n" \
               + f"sender: {self.sender}\n" \
               + f"receiver: {self.receiver}\n" \
               + f"amount: {self.amount}\n" \
               + f"fee: {self.fee}\n"
