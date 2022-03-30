from utils import *


class Transaction:
    def __init__(self, amount, sender, receiver, signature):
        self.amount = amount
        self.fee = float(amount * FEE_PERCENTAGE / 100)
        self.sender = sender
        self.receiver = receiver
        self.signature = signature

