import sys
import argparse
from socketserver import ThreadingUDPServer, DatagramRequestHandler
from datetime import datetime


class ThreadedServerHandler(DatagramRequestHandler):
    """
    Class handling every request.
    Every request from client will be handled by new thread.
    """

    def handle(self):
        """
        Function handling current connection.
        :return: None
        """
        print('New connection.')
        self.info(f'Connection from {self.client_address[0]}({self.client_address[1]})')
        self.send(
            '********************************\n** Welcome to the BBS server. **\n********************************')

    def send(self, msg):
        """
        Send message to user
        :param msg: message
        :param res: optional response to client
        :return: None
        """
        socket = self.request[1]
        socket.sendto(bytes(f'{msg}\n', 'utf-8'), self.client_address)

    def info(self, log):
        """
        Print info log
        :param log: info log
        :return: None
        """
        global verbosity
        if verbosity > 1:
            print(f'[\033[96mINFO\033[00m] {log}')
            sys.stdout.flush()

    def warning(self, log):
        """
        Print warning log
        :param log: warning log
        :return: None
        """
        global verbosity
        if verbosity > 0:
            print(f'[\033[93mWARN\033[00m] {log}')
            sys.stdout.flush()


def parse_arguments():
    """
    Generate an argument parser
    :return: argparse.Namespace an object containing all required arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='IP for hosting server', nargs='?')
    parser.add_argument('port', help='port number', nargs='?', type=int)
    parser.add_argument('-v', '--verbosity', help='verbosity level (0-2)', default=0, type=int)
    return parser.parse_args()


if __name__ == '__main__':
    """
    Main running server
    Setup with python3 ./UDPserver.py <host> <port>
    :return: None
    """

    # Check arguments, host and port
    args = parse_arguments()
    host = args.host
    port = args.port

    verbosity = args.verbosity

    ThreadingUDPServer.allow_reuse_address = True
    ThreadingUDPServer.daemon_threads = True
    with ThreadingUDPServer((host, port), ThreadedServerHandler) as server:
        try:
            print(f'\n{datetime.now()}'
                  , f'\nStarting UDP server at {host}:{port}\nQuit the server with CONTROL-C.\n')
            server.serve_forever()
        except KeyboardInterrupt:
            print('')
            server.shutdown()
