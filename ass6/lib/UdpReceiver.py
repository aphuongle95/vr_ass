import socket
import threading

class UdpReceiver:

    def __init__(self, LISTEN_ADDRESS, LISTEN_PORT, MESSAGE_CALLBACK):
        self.listen_address = LISTEN_ADDRESS
        self.listen_port = LISTEN_PORT
        self.source = (self.listen_address, self.listen_port)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(self.source)
        self.message_callback = MESSAGE_CALLBACK
        threading.Thread(target = self.main_loop).start()

    def main_loop(self):
        while True:
            data, address = self.udp_socket.recvfrom(1024)
            self.message_callback(data.decode('utf-8'))