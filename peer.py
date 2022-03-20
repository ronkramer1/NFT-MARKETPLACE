import sys
from socket import *
from select import select
from block import Block

RECV_SIZE = 1024
UDP_PORT = 50000
TCP_PORT = 50001
NUMBER_OF_CONNECTED_CLIENTS = 2
host_ip = gethostbyname(gethostname())


class Peer:
    """used to handle networking, both udp and tcp"""
    def __init__(self):
        # udp sockets:
        self.udp_sender = socket(AF_INET, SOCK_DGRAM)
        self.udp_sender.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        self.udp_receiver = socket(AF_INET, SOCK_DGRAM)
        self.udp_receiver.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.udp_receiver.bind(('', UDP_PORT))

        # tcp sockets:
        self.tcp_server = None

        self.tcp_client = None

    # sending:
    def udp_send_raw(self, message):
        """broadcasts a udp message"""
        self.udp_sender.sendto(message.encode('utf-8'), ('255.255.255.255', UDP_PORT))

    def udp_send(self, to_send):
        """formats and broadcasts a udp message"""
        if type(to_send) == Block:
            self.udp_send_raw("block:" + to_send())
        else:
            self.udp_send_raw(to_send)

    # receiving
    def udp_receive_raw(self):
        """receives a message from the udp_receiver port and returns it"""
        return self.udp_receiver.recvfrom(RECV_SIZE)

    def udp_receive(self):
        """receives a udp message, interprets it, and returns the relevant information, also tcp connects if
        necessary """
        (received_message, sender_address) = self.udp_receive_raw()
        received_message = received_message.decode('utf-8')
        if received_message[:len("block:")] == "block:":
            return received_message[len("block:"):]
        else:
            return received_message

    def constant_receive(self):
        """tries to receive messages from other peers (both tcp and udp), calls itself every 0.1 seconds"""
        rlist, wlist, xlist = select([self.udp_receiver], [], [], 0.01)
        for sock in rlist:
            if sock == self.udp_receiver:
                received_message = self.udp_receive()
                self.received_from_udp_socket(received_message)

    def received_from_udp_socket(self, message):
        """handles a message that was received by the udp receiver socket"""
        print(message)

