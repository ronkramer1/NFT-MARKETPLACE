import configparser

from Crypto.Hash import SHA256

config = configparser.ConfigParser()
try:
    config.read('configure.ini')

    FEE_CONSTANT = int(config['transaction']['FEE_CONSTANT'])
    NUM_OF_TRANSACTIONS_IN_BLOCK = int(config['cryptography']['NUM_OF_TRANSACTIONS_IN_BLOCK'])

    CURVE = config['cryptography']['CURVE']
    CURVE_FORMAT = config['cryptography']['CURVE_FORMAT']
    PUBLIC_KEY_FORMAT = config['cryptography']['PUBLIC_KEY_FORMAT']
    PRIVATE_KEY_FORMAT = config['cryptography']['PRIVATE_KEY_FORMAT']
    PRIVATE_KEY_PROTECTION = config['cryptography']['PRIVATE_KEY_PROTECTION']
    NUM_OF_TRANSACTIONS_IN_BLOCK = int(config['cryptography']['NUM_OF_TRANSACTIONS_IN_BLOCK'])
    STANDARD_FOR_SIGNATURES = config['cryptography']['STANDARD_FOR_SIGNATURES']

    RECV_SIZE = eval(config['networking']['RECV_SIZE'])
    UDP_PORT = int(config['networking']['UDP_PORT'])
    TCP_PORT = int(config['networking']['TCP_PORT'])
    NUMBER_OF_CONNECTED_CLIENTS = int(config['networking']['NUMBER_OF_CONNECTED_CLIENTS'])

except configparser.ParsingError:
    print("could not read from ini")
    FEE_CONSTANT = 0.02

    CURVE = 'P-256'
    CURVE_FORMAT = 'PEM'

    RECV_SIZE = 1024 * 10
    UDP_PORT = 50000
    TCP_PORT = 50001
    NUMBER_OF_CONNECTED_CLIENTS = 2


def sha256_hash(*args):
    """return a sha256 hash of a concatenation of the input input"""
    str_rep = ""
    for arg in args:
        str_rep += str(arg)

    return SHA256.new(str_rep.encode())