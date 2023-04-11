import socket

from HelperModule import udt
from stop_and_wait.receiver import SnwReceiver
from go_back_n.receiver import GbnReceiver


def create_client(server_address, file_name, protocol):
    try:
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("UDP client socket created")

        # send a packet to server with file name
        # protocol to use and to identify client address
        packet = file_name + "," + str(protocol)
        udt.send(packet.encode(), sock, server_address)

        file_name = "new_" + file_name
        # create file for writing in binary mode
        with open(file_name, "wb") as file:
            if protocol == 1:
                stop_and_wait = SnwReceiver(sock, server_address, file)
                stop_and_wait.receive_file()
            elif protocol == 2:
                go_back_n = GbnReceiver(sock, server_address, file)
                go_back_n.receive_file()
            else:
                print("Invalid protocol")

        print("Connection closed")
        sock.close()
    except IOError as error:
        print("Error doing the connection")
        print(error)


def client_parameters():
    try:
        ip_server = input("Server IP: ")
        port_server = int(input("Server port: "))
        address = (ip_server, port_server)
        protocol = int(input("Protocol to use:\n1. Stop-and-Wait\n2. Go-Back-N\nEnter the number: "))
        file_name = input("File name: ")
        create_client(address, file_name, protocol)
    except ValueError:
        print("Invalid parameter")
        exit()


if __name__ == "__main__":
    try:
        client_parameters()
    except KeyboardInterrupt:
        print("Shutting down")
