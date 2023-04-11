from HelperModule import packet, udt


class SnwReceiver:
    def __init__(self, socket, server_address, file):
        self.__sock = socket
        self.__address = server_address
        self.__file = file
        self.__ack = b"ACK"
        self.__sndpkt = None
        self.__sequence = 0

    def receive_file(self):
        while True:
            # waits for packet
            rcvpkt = udt.recv(self.__sock)[0]
            if rcvpkt:
                # extract data and sequence number received
                seq_num, data = packet.extract(rcvpkt)
                # send ACK with sequence received
                self.__rdt_send(seq_num)
                if not data:
                    # empty data is end of file
                    print("File received")
                    return
                # validates if it is the require sequence
                if self.__has_seq(seq_num, self.__sequence):
                    self.__deliver_data(data)
                    # Swapping 1 with 0 and 0 with 1
                    # change for next sequence
                    self.__sequence = 1 - self.__sequence

    def __has_seq(self, seq_num, require_sequence):
        return seq_num == require_sequence

    # creates packet and sends it
    def __rdt_send(self, sequence):
        self.__sndpkt = packet.make(sequence, self.__ack)
        udt.send(self.__sndpkt, self.__sock, self.__address)

    # writes data to file
    def __deliver_data(self, data):
        self.__file.write(data)
