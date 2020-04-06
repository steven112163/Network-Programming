import threading
import sys
import sqlite3
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
        self.current_user = None
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
        if len(command) != 4:
            self.wfile.write(bytes('Usage: register <username> <email> <password>\n', 'utf-8'))

    def login_handler(self, command):
        """
        Function handling login command
        :param command: Command sent from client
        :return: None
        """
        if len(command) != 3:
            self.wfile.write(bytes('Usage: login <username> <password>\n', 'utf-8'))

    def logout_handler(self, command):
        """
        Function handling logout command
        :param command: Command sent from client
        :return: None
        """
        if self.current_user:
            self.wfile.write(bytes(f'Bye, {self.current_user}.\n', 'utf-8'))
            self.current_user = None
        else:
            self.wfile.write(bytes('Please login first\n', 'utf-8'))

    def whoami_handler(self, command):
        """
        Function handling whoami command
        :param command: Command sent from client
        :return: None
        """
        if self.current_user:
            self.wfile.write(bytes(f'{self.current_user}\n', 'utf-8'))
        else:
            self.wfile.write(bytes('Please login first\n', 'utf-8'))


def main():
    """
    Main running server
    Setup with ./server <port>
    :return: None
    """

    # Check arguments
    if len(sys.argv) != 2:
        print("Usage: python3 ./server.py <port>")
        return
    host = 'localhost'
    try:
        port = int(sys.argv[1])
    except:
        print("Usage: python3 ./server.py <port>")
        return

    # Create database and table
    conn = sqlite3.connect('server_0510002.db')
    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="users";')
    if cursor.fetchone() is None:
        conn.execute('''CREATE TABLE users (
                            username TEXT PRIMARY KEY NOT NULL,
                            email    TEXT NOT NULL,
                            password TEXT NOT NULL
                        );''')
    conn.close()

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
