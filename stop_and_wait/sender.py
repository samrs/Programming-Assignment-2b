import socket
import time

from HelperModule import packet, udt
from HelperModule.timer import Timer


class SnwSender:
    def __init__(self, sock, address, timeout):
        self.__sock = sock
        self.__address = address
        self.__timer = Timer(timeout)
        self.__sequence_number = 0
        self.__ack = b"ACK"
        self.__sndpkt = None
        # sets timeout to wait for an ack
        self.__sock.settimeout(timeout)
        self.__transmitted_packets = 0
        self.__retransmitted_packets = 0
        self.__time_taken = 0

    def send_file(self, file):
        # get start time
        start_time = time.time()
        while True:
            data = file.read(1020)
            # sends a packet and then wait for its ACK
            self.__rdt_send(data)
            self.__wait_ack()
            # end of data is an end of transmission
            # one empty packet was sent previously to notify end of file
            if not data:
                end_time = time.time()
                self.__time_taken = end_time - start_time
                break

    def __wait_ack(self):
        try:
            while True:
                # wait for ACK
                rcvpkt = udt.recv(self.__sock)[0]
                # verifies for an expected ACK
                if rcvpkt and self.__isACK(rcvpkt):
                    self.__timer.stop()
                    # Swapping 1 with 0 and 0 with 1
                    self.__sequence_number = 1 - self.__sequence_number
                    break
        except socket.timeout:
            # an exception is launch when timeout is reach
            self.__timeout()
            # wait for ack again
            self.__wait_ack()

    def __rdt_send(self, data):
        # sends packet and start timer
        self.__sndpkt = packet.make(self.__sequence_number, data)
        udt.send(self.__sndpkt, self.__sock, self.__address)
        self.__timer.start()
        self.__transmitted_packets += 1

    def __isACK(self, rcvpkt):
        seq_num, message = packet.extract(rcvpkt)
        return (message == self.__ack) and (seq_num == self.__sequence_number)

    def __timeout(self):
        # verifies again with timer module
        if self.__timer.timeout():
            # sends packet again and restarts timer
            udt.send(self.__sndpkt, self.__sock, self.__address)
            self.__timer.restart()
            self.__transmitted_packets += 1
            self.__retransmitted_packets += 1

    def get_transmitted_packets(self):
        return self.__transmitted_packets

    def get_retransmitted_packets(self):
        return self.__retransmitted_packets

    def get_time_taken(self):
        return self.__time_taken
