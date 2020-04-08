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
        print('New connection.')
        self.conn = sqlite3.connect('server_0510002.db')
        self.conn.row_factory = sqlite3.Row
        self.wfile.write(bytes(
            '********************************\n** Welcome to the BBS server. **\n********************************\n',
            'utf-8'))
        self.wfile.write(bytes('% ', 'utf-8'))
        self.current_user = None
        while True:
            try:
                command = str(self.rfile.readline(), 'utf-8').strip().split()
                if command:
                    if command[0] == 'exit':
                        self.conn.close()
                        return
                    self.command_handler(command)
                self.wfile.write(bytes('% ', 'utf-8'))
            except Exception as e:
                print(str(e))

    def command_handler(self, command):
        """
        Function handling entered command
        :param command: Command sent from client
        :return: None
        """
        if command[0] == 'register':
            self.register_handler(command)
        elif command[0] == 'login':
            self.login_handler(command)
        elif command[0] == 'logout':
            self.logout_handler(command)
        elif command[0] == 'whoami':
            self.whoami_handler(command)

    def register_handler(self, command):
        """
        Function handling register command
        :param command: Command sent from client
        :return: None
        """

        # Check arguments
        if len(command) != 4:
            self.wfile.write(bytes('Usage: register <username> <email> <password>\n', 'utf-8'))
            return

        # Check whether username is used
        cursor = self.conn.execute('SELECT username from USERS WHERE Username=:username', {"username": command[1]})
        if cursor.fetchone() is not None:
            self.wfile.write(bytes('Username is already used.\n', 'utf-8'))
            return

        self.conn.execute('INSERT INTO USERS (Username, Email, Password) VALUES (:username, :email, :password)',
                          {"username": command[1], "email": command[2], "password": command[3]})
        self.conn.commit()
        self.wfile.write(bytes('Register successfully.\n', 'utf-8'))

    def login_handler(self, command):
        """
        Function handling login command
        :param command: Command sent from client
        :return: None
        """

        # Check arguments
        if len(command) != 3:
            self.wfile.write(bytes('Usage: login <username> <password>\n', 'utf-8'))
            return

        # Check if user is already logged in
        if self.current_user:
            self.wfile.write(bytes(f'Please logout first.\n', 'utf-8'))
            return

        cursor = self.conn.execute('SELECT Username, Password FROM USERS WHERE Username=:username',
                                   {"username": command[1]})
        row = cursor.fetchone()
        if row is None:
            self.wfile.write(bytes('Login failed.\n', 'utf-8'))
            return
        if command[2] != row['Password']:
            self.wfile.write(bytes('Login failed.\n', 'utf-8'))
            return

        self.current_user = row['Username']
        self.wfile.write(bytes(f'Welcome, {self.current_user}.\n', 'utf-8'))

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
            self.wfile.write(bytes('Please login first.\n', 'utf-8'))

    def whoami_handler(self, command):
        """
        Function handling whoami command
        :param command: Command sent from client
        :return: None
        """
        if self.current_user:
            self.wfile.write(bytes(f'{self.current_user}.\n', 'utf-8'))
        else:
            self.wfile.write(bytes('Please login first.\n', 'utf-8'))


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
    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="USERS";')
    if cursor.fetchone() is None:
        conn.execute('''CREATE TABLE USERS (
                            UID      INTEGER PRIMARY KEY AUTOINCREMENT,
                            Username TEXT UNIQUE NOT NULL,
                            Email    TEXT NOT NULL,
                            Password TEXT NOT NULL
                        );''')
    conn.close()

    ThreadingTCPServer.allow_reuse_address = True
    ThreadingTCPServer.daemon_threads = True
    with ThreadingTCPServer((host, port), ThreadedServerHandler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\n')
            server.shutdown()


if __name__ == '__main__':
    main()
