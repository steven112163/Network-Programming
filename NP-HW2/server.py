import sys
import argparse
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
        self.debug(f'Connection from {self.client_address[0]}({self.client_address[1]})')
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
                        self.debug(f'Exit from {self.client_address[0]}({self.client_address[1]})')
                        return
                    self.command_handler(command)
                self.wfile.write(bytes('% ', 'utf-8'))
            except Exception as e:
                print(str(e))

    def debug(self, log):
        """
        Print log for debugging
        :param log: log for debugging
        :return: None
        """
        global verbosity
        if verbosity:
            print(f'# {log}')
            sys.stdout.flush()

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
        elif command[0] == 'create-board':
            self.create_board_handler(command)
        elif command[0] == 'create-post':
            self.create_post_handler(command)
        elif command[0] == 'list-board':
            self.list_board_handler(command)
        elif command[0] == 'list-post':
            self.list_post_handler(command)
        elif command[0] == 'read':
            self.read_handler(command)
        elif command[0] == 'delete-post':
            self.delete_post_handler(command)
        elif command[0] == 'update-post':
            self.update_post_handler(command)
        elif command[0] == 'comment':
            self.command_handler(command)
        else:
            self.debug(f'Invalid command from {self.client_address[0]}({self.client_address[1]})\n\t{command}')

    def register_handler(self, command):
        """
        Function handling register command
        :param command: Command sent from client
        :return: None
        """

        # Check arguments
        self.debug(f'Register from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if len(command) != 4:
            self.wfile.write(bytes('Usage: register <username> <email> <password>\n', 'utf-8'))
            self.debug(f'Incomplete register command from {self.client_address[0]}({self.client_address[1]})')
            return

        # Check whether username is used
        cursor = self.conn.execute('SELECT username from USERS WHERE Username=:username', {"username": command[1]})
        if cursor.fetchone() is not None:
            self.wfile.write(bytes('Username is already used.\n', 'utf-8'))
            self.debug(f'Username from {self.client_address[0]}({self.client_address[1]}) is used')
            return

        self.conn.execute('INSERT INTO USERS (Username, Email, Password) VALUES (:username, :email, :password)',
                          {"username": command[1], "email": command[2], "password": command[3]})
        self.conn.commit()
        self.wfile.write(bytes('Register successfully.\n', 'utf-8'))
        self.debug(f'Register successfully from {self.client_address[0]}({self.client_address[1]})')

    def login_handler(self, command):
        """
        Function handling login command
        :param command: Command sent from client
        :return: None
        """

        # Check arguments
        self.debug(f'Login from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if len(command) != 3:
            self.wfile.write(bytes('Usage: login <username> <password>\n', 'utf-8'))
            self.debug(f'Incomplete login command from {self.client_address[0]}({self.client_address[1]})')
            return

        # Check if user is already logged in
        if self.current_user:
            self.wfile.write(bytes(f'Please logout first.\n', 'utf-8'))
            self.debug(f'User from {self.client_address[0]}({self.client_address[1]}) is already logged in')
            return

        cursor = self.conn.execute('SELECT Username, Password FROM USERS WHERE Username=:username',
                                   {"username": command[1]})
        row = cursor.fetchone()
        if row is None:
            self.wfile.write(bytes('Login failed.\n', 'utf-8'))
            self.debug(f"Username entered from {self.client_address[0]}({self.client_address[1]}) isn't in DB")
            return
        if command[2] != row['Password']:
            self.wfile.write(bytes('Login failed.\n', 'utf-8'))
            self.debug(f'Password entered from {self.client_address[0]}({self.client_address[1]}) is wrong')
            return

        self.current_user = row['Username']
        self.wfile.write(bytes(f'Welcome, {self.current_user}.\n', 'utf-8'))
        self.debug(f'Log in successfully from {self.client_address[0]}({self.client_address[1]})')

    def logout_handler(self, command):
        """
        Function handling logout command
        :param command: Command sent from client
        :return: None
        """
        self.debug(f'Logout from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if self.current_user:
            self.wfile.write(bytes(f'Bye, {self.current_user}.\n', 'utf-8'))
            self.current_user = None
            self.debug(f'User from {self.client_address[0]}({self.client_address[1]}) log out')
        else:
            self.wfile.write(bytes('Please login first.\n', 'utf-8'))
            self.debug(f'User from {self.client_address[0]}({self.client_address[1]}) is already logged out')

    def whoami_handler(self, command):
        """
        Function handling whoami command
        :param command: Command sent from client
        :return: None
        """
        self.debug(f'Whoami from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if self.current_user:
            self.wfile.write(bytes(f'{self.current_user}.\n', 'utf-8'))
            self.debug(f'Current user check from {self.client_address[0]}({self.client_address[1]})')
        else:
            self.wfile.write(bytes('Please login first.\n', 'utf-8'))
            self.debug(f'User from {self.client_address[0]}({self.client_address[1]}) is already logged out')

    def create_board_handler(self, command):
        """
        Function handling create-board command
        :param command: Command sent from client
        :return: None
        """
        self.debug(f'Create-board from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if not self.current_user:
            self.wfile.write(bytes('Please login first.\n', 'utf-8'))
            self.debug(f'User from {self.client_address[0]}({self.client_address[1]}) is already logged out')
            return

        if len(command) != 2:
            self.wfile.write(bytes('Usage: create-board <name>\n', 'utf-8'))
            self.debug(f'Incomplete create-board command from {self.client_address[0]}({self.client_address[1]})')
            return

        cursor = self.conn.execute('SELECT BoardName FROM BOARDS WHERE BoardName=:board_name',
                                   {"board_name": command[1]})
        if cursor.fetchone() is not None:
            self.wfile.write(bytes('Board is already exist.\n', 'utf-8'))
            self.debug(f'Board name from {self.client_address[0]}({self.client_address[1]}) exists')
            return

        self.conn.execute('INSERT INTO BOARDS (BoardName, Moderator) VALUES (:board_name, :moderator)',
                          {"board_name": command[1], "moderator": self.current_user})
        self.conn.commit()
        self.wfile.write(bytes('Create Board successfully.\n', 'utf-8'))
        self.debug(f'Board created successfully from {self.client_address[0]}({self.client_address[1]})')

    def create_post_handler(self, command):
        """
        Function handling create-post command
        :param command: Command sent from client
        :return: None
        """
        self.debug(f'Create-post from {self.client_address[0]}({self.client_address[1]})\n\t{command}')

    def list_board_handler(self, command):
        """
        Function handling list-board command
        :param command: Command sent from client
        :return: None
        """
        self.debug(f'List-board from {self.client_address[0]}({self.client_address[1]})\n\t{command}')

        if len(command) > 2:
            self.wfile.write(bytes('Usage: list-board ##<key>\n', 'utf-8'))
            self.debug(f'Incomplete list-board command from {self.client_address[0]}({self.client_address[1]})')
            return
        elif len(command) == 2:
            key_word = command[1][2:]
            key_word = '%' + key_word + '%'
        else:
            key_word = None

        if key_word:
            cursor = self.conn.execute("SELECT ID, BoardName, Moderator FROM BOARDS WHERE BoardName LIKE :key_word",
                                       {"key_word": key_word})
        else:
            cursor = self.conn.execute('SELECT ID, BoardName, Moderator FROM BOARDS')

        self.wfile.write(bytes('\tIndex\tName\tModerator\n', 'utf-8'))
        for row in cursor:
            self.wfile.write(bytes(f'\t{row["ID"]}\t{row["BoardName"]}\t{row["Moderator"]}\n', 'utf-8'))

    def list_post_handler(self, command):
        """
        Function handling list-post command
        :param command: Command sent from client
        :return: None
        """
        self.debug(f'List-post from {self.client_address[0]}({self.client_address[1]})\n\t{command}')

    def read_handler(self, command):
        """
        Function handling read command
        :param command: Command sent from client
        :return: None
        """
        self.debug(f'Read from {self.client_address[0]}({self.client_address[1]})\n\t{command}')

    def delete_post_handler(self, command):
        """
        Function handling delete-post command
        :param command: Command sent from client
        :return: None
        """
        self.debug(f'Delete-post from {self.client_address[0]}({self.client_address[1]})\n\t{command}')

    def update_post_handler(self, command):
        """
        Function handling update-post command
        :param command: Command sent from client
        :return: None
        """
        self.debug(f'Update-post from {self.client_address[0]}({self.client_address[1]})\n\t{command}')

    def comment_handler(self, command):
        """
        Function handling comment command
        :param command: Command sent from client
        :return: None
        """
        self.debug(f'Comment from {self.client_address[0]}({self.client_address[1]})\n\t{command}')


def parse_arguments():
    """
    Generate an argument parser
    :return: argparse.Namespace an object containing all required arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('port', help='port number', nargs='?', type=int)
    parser.add_argument('-v', '--verbosity', help='verbosity level', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    """
    Main running server
    Setup with python3 ./server.py <port>
    :return: None
    """

    # Check arguments, host and port
    host = 'localhost'
    args = parse_arguments()
    port = args.port

    verbosity = args.verbosity

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

    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="BOARDS";')
    if cursor.fetchone() is None:
        conn.execute('''CREATE TABLE BOARDS(
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            BoardName TEXT NOT NULL UNIQUE,
                            Moderator TEXT NOT NULL,
                            FOREIGN KEY(Moderator) REFERENCES USERS(Username)
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
