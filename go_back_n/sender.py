import selectors
import time

from HelperModule import packet, udt, timer


class GbnSender:
    def __init__(self, sock, address, window_size, timeout):
        self.__sock = sock
        self.__address = address
        self.__selector = selectors.DefaultSelector()
        self.__base = 1
        self.__next_seq_number = 1
        self.__window_size = window_size
        self.__sndpkt = {}
        self.__timer = timer.Timer(timeout)
        self.__is_sending = True
        self.__is_ending_file = False
        self.__transmitted_packets = 0
        self.__retransmitted_packets = 0
        self.__number_timeouts = 0
        self.__time_taken = 0
        self.__sock.setblocking(False)
        self.__selector.register(sock, selectors.EVENT_READ | selectors.EVENT_WRITE)

    def send_file(self, file):
        start_time = time.time()
        while self.__is_sending:
            # when socket is ready to read or write
            for key, mask in self.__selector.select(timeout=1):
                try:
                    if mask & selectors.EVENT_WRITE:
                        # sends packets and verify for timeout
                        self.__rdt_send(file)
                        self.__timeout()
                    if mask & selectors.EVENT_READ:
                        # reads for incoming ACK
                        self.__rdt_rcv()
                except OSError:
                    print("Error writing/reading")
                    return
        end_time = time.time()
        self.__time_taken = end_time - start_time
        self.__transmitted_packets = self.__transmitted_packets + self.__retransmitted_packets
        self.__close_connection()

    def __rdt_send(self, file):
        if (self.__next_seq_number < self.__base + self.__window_size) and not self.__is_ending_file:
            data = file.read(1020)
            # creates packet with correct sequence number
            self.__sndpkt[self.__next_seq_number] = packet.make(self.__next_seq_number, data)
            udt.send(self.__sndpkt[self.__next_seq_number], self.__sock, self.__address)
            # if base reach next sequence number starts timer again
            if self.__base == self.__next_seq_number:
                self.__timer.start()
            self.__next_seq_number += 1
            self.__transmitted_packets += 1
            # empty data is ending of file
            if not data:
                self.__is_ending_file = True

    # verifies timeout
    def __timeout(self):
        if self.__timer.timeout():
            self.__number_timeouts += 1
            # restarts timer and resends all packets in range
            self.__timer.restart()
            for i in range(self.__base, self.__next_seq_number):
                udt.send(self.__sndpkt[i], self.__sock, self.__address)
                self.__retransmitted_packets += 1

    def __rdt_rcv(self):
        # reads ACK from client
        rcvpkt = udt.recv(self.__sock)[0]
        if rcvpkt:
            # get ack and update base
            self.__base = packet.extract(rcvpkt)[0] + 1
            if self.__base == self.__next_seq_number:
                self.__timer.stop()
                # ending of file is end of transmission
                if self.__is_ending_file:
                    print("File sent")
                    self.__is_sending = False
            else:
                # restarts time, move window
                self.__timer.restart()

    def __close_connection(self):
        print("Close selector")
        self.__selector.unregister(self.__sock)
        self.__selector.close()

    def get_transmitted_packets(self):
        return self.__transmitted_packets

    def get_retransmitted_packets(self):
        return self.__retransmitted_packets

    def get_time_taken(self):
        return self.__time_taken

    def get_timeouts(self):
        return self.__number_timeouts
