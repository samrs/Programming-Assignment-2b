import socket
from HelperModule import udt
from stop_and_wait.sender import SnwSender
from go_back_n.sender import GbnSender

IP_SERVER = "localhost"
TIMEOUT = 1


def create_server(server_address, window_size):
    try:
        # Create a UDP socket
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind the socket to the port and ip address
        server.bind(server_address)
        print("UDP server socket created")
        print('Starting up on {} port {}'.format(*server_address))

        # receives file name, protocol and client address
        packet, client_address = udt.recv(server)
        packet = packet.decode().split(",")
        file_name = packet[0]
        protocol = int(packet[1])
        print("File name: " + file_name)

        # tries to open file and selects protocol
        with open(file_name, "rb") as file:
            if protocol == 1:
                print("Protocol: SnW")
                stop_and_wait = SnwSender(server, client_address, TIMEOUT)
                stop_and_wait.send_file(file)

                print("Transmitted_packets: " + str(stop_and_wait.get_transmitted_packets()))
                print("Retransmitted_packets: " + str(stop_and_wait.get_retransmitted_packets()))
                print("Time_taken: " + str(stop_and_wait.get_time_taken()))
            elif protocol == 2:
                print("Protocol: GBN")
                go_back_n = GbnSender(server, client_address, window_size, TIMEOUT)
                go_back_n.send_file(file)

                print("Window: " + str(window_size))
                print("Transmitted_packets: " + str(go_back_n.get_transmitted_packets()))
                print("Retransmitted_packets: " + str(go_back_n.get_retransmitted_packets()))
                print("Time_taken: " + str(go_back_n.get_time_taken()))
                print("Number of timeouts: " + str(go_back_n.get_timeouts()))
            else:
                print("Invalid protocol")

        print("Connection closed")
        server.close()
    except OSError as error:
        print("Error creating UDP server socket or opening file")
        print(error)
        return


def start():
    # read port and check if it is a number
    try:
        port = int(input("Connect at port# "))
        window_size = int(input("Window size: "))
    except ValueError:
        print("Invalid port")
        exit()
    address = (IP_SERVER, port)
    create_server(address, window_size)


if __name__ == "__main__":
    try:
        start()
        # plot_figures()
    except KeyboardInterrupt:
        print("Shutting down")
