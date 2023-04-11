from HelperModule import packet, udt


class GbnReceiver:
    def __init__(self, sock, server_address, file):
        self.__sock = sock
        self.__address = server_address
        self.__file = file
        self.__expected_seq_number = 1
        self.__sndpkt = packet.make(0)
        self.__is_receiving = True

    def receive_file(self):
        while self.__is_receiving:
            self.__rdt_rcv(self.__file)
            self.__send_ack()
        print("File received")

    def __rdt_rcv(self, file):
        rcvpkt = udt.recv(self.__sock)[0]
        # if the received packed is the expected
        # then writes into file
        if rcvpkt and self.__has_seq_number(rcvpkt):
            _, data = packet.extract(rcvpkt)
            if data:
                file.write(data)
            else:
                # empty data is end of file
                self.__is_receiving = False
            # creates new ACK for this sequence
            self.__sndpkt = packet.make(seq_num=self.__expected_seq_number)
            self.__expected_seq_number += 1

    # verifies expected sequence
    def __has_seq_number(self, rcvpkt):
        seq_number = packet.extract(rcvpkt)[0]
        return seq_number == self.__expected_seq_number

    # send ack for last packet received
    def __send_ack(self):
        udt.send(self.__sndpkt, self.__sock, self.__address)
