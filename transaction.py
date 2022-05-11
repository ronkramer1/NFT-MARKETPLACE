import json

from utils import *


class Transaction:
    def __init__(self, receiver="also ron", sender="ron", amount=1, signature="", fee=0):
        self.amount = amount
        self.fee = float(amount * FEE_PERCENTAGE / 100)
        self.sender = sender
        self.receiver = receiver
        self.signature = signature
        self.fee = fee

    def serialize(self):
        """returns a json string of the transaction, can be used for sending."""
        return str(json.dumps(self.__dict__, indent=4))

    @staticmethod
    def deserialize(data):
        """takes a serialized (json string of a) transaction and returns a transaction object"""
        if type(data) == str:
            data_dict = json.loads(data)
        elif type(data) == dict:
            data_dict = data
        return Transaction(data_dict["receiver"],
                           data_dict["sender"],
                           data_dict["amount"],
                           data_dict["signature"],
                           data_dict["fee"])

    def __str__(self):
        return f"signature: {self.signature}\n" \
               + f"sender: {self.sender}\n" \
               + f"receiver: {self.receiver}\n" \
               + f"amount: {self.amount}\n" \
               + f"fee: {self.fee}\n"
