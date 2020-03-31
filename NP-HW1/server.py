import threading
import sys
from socketserver import ThreadingTCPServer, StreamRequestHandler


class ThreadedServerHandler(StreamRequestHandler):
    """
    Class handling every request.
    Every request from client will be handled by new thread.
    """

    def handle(self):
        """
        Function handling current connection.
        It continuously listens to the client until client enters "exit".
        :return: None
        """
        print('New connection')
        self.wfile.write(bytes('# ', 'utf-8'))
        while True:
            try:
                command = str(self.rfile.readline(), 'utf-8').strip().split()
                if command:
                    if command[0] == 'exit':
                        return
                    self.command_handler(command)
                self.wfile.write(bytes('# ', 'utf-8'))
            except Exception as e:
                print(str(e))

    def command_handler(self, command):
        """
        Function handling entered command
        :param command: Command sent from client
        :return: None
        """
        current_thread = threading.current_thread()
        self.wfile.write(bytes(f'{current_thread.name}: {command}\n', 'utf-8'))
        if command[0] == 'register':
            self.register_handler(command)
        elif command[0] == 'login':
            self.login_handler(command)
        elif command[0] == 'logout':
            self.logout_handler(command)
        elif command[0] == 'whoami':
            self.whoami_handler(command)
        else:
            self.wfile.write(bytes('Invalid command\n', 'utf-8'))

    def register_handler(self, command):
        """
        Function handling register command
        :param command: Command sent from client
        :return: None
        """
        pass

    def login_handler(self, command):
        """
        Function handling login command
        :param command: Command sent from client
        :return: None
        """
        pass

    def logout_handler(self, command):
        """
        Function handling logout command
        :param command: Command sent from client
        :return: None
        """
        pass

    def whoami_handler(self, command):
        """
        Function handling whoami command
        :param command: Command sent from client
        :return: None
        """
        pass


def main():
    """
    Main running server
    Setup with ./server <port>
    :return: None
    """
    if len(sys.argv) != 2:
        print("Usage: ./server <port>")
        return

    host = 'localhost'
    try:
        port = int(sys.argv[1])
    except:
        print("Usage: ./server <port>")
        return

    ThreadingTCPServer.allow_reuse_address = True
    ThreadingTCPServer.daemon_threads = True
    with ThreadingTCPServer((host, port), ThreadedServerHandler) as server:
        print("Server loop running")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\n')
            server.shutdown()


if __name__ == '__main__':
    main()
