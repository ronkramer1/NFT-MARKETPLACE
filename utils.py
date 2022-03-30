import configparser

config = configparser.ConfigParser()
try:
    config.read('configure.ini')
    FEE_PERCENTAGE = config['transaction']['FEE_PERCENTAGE']

    CURVE = config['cryptography']['CURVE']
    CURVE_FORMAT = config['cryptography']['CURVE_FORMAT']

    RECV_SIZE = eval(config['networking']['RECV_SIZE'])
    UDP_PORT = int(config['networking']['UDP_PORT'])
    TCP_PORT = int(config['networking']['TCP_PORT'])
    NUMBER_OF_CONNECTED_CLIENTS = int(config['networking']['NUMBER_OF_CONNECTED_CLIENTS'])

except configparser.ParsingError:
    print("could not read from ini")
    FEE_PERCENTAGE = '2'

    CURVE = 'P-256'
    CURVE_FORMAT = 'PEM'

    RECV_SIZE = 1024 * 10
    UDP_PORT = 50000
    TCP_PORT = 50001
    NUMBER_OF_CONNECTED_CLIENTS = 2
