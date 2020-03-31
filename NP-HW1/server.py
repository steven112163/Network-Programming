import socket
import threading
from socketserver import ThreadingTCPServer, StreamRequestHandler


class ThreadedServerHandler(StreamRequestHandler):
    def handle(self):
        data = str(self.rfile.readline(), 'ascii').strip()
        current_thread = threading.current_thread()
        self.wfile.write(bytes(f'{current_thread.name}: {data}', 'ascii'))
        return


def client(host, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as so:
        so.connect((host, port))
        so.sendall(bytes(message, 'ascii'))
        response = str(so.recv(1024), 'ascii')
        print(f'Received: {response}')


def main():
    host = 'localhost'
    port = 7890
    with ThreadingTCPServer((host, port), ThreadedServerHandler) as server:
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)

        client(host, port, 'test 1\n')
        client(host, port, 'test 2\n')
        client(host, port, 'test 3\n')

        server.shutdown()


if __name__ == '__main__':
    main()
