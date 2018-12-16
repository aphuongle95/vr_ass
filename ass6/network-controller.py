import socket

class UdpBroadcaster:

    def __init__(self, SEND_ADDRESS, SEND_PORT):

        self.send_address = SEND_ADDRESS
        self.send_port = SEND_PORT
        self.destination = (self.send_address, self.send_port)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setblocking(0)


    def broadcast(self, MESSAGE):
        encoded_message = MESSAGE.encode('utf-8')
        self.udp_socket.sendto(encoded_message, self.destination)
        #print('sent', MESSAGE)


def start():
    udp_broadcaster = UdpBroadcaster("127.0.0.1", 7070)

    while True:
        command = input('> ')
        udp_broadcaster.broadcast(command)


if __name__ == '__main__':
    start()