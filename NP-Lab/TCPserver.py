import sys
import argparse
import sqlite3
from socketserver import ThreadingTCPServer, StreamRequestHandler
from datetime import datetime


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
        self.info(f'Connection from {self.client_address[0]}({self.client_address[1]})')
        self.conn = sqlite3.connect('server_0510002.db')
        self.conn.row_factory = sqlite3.Row
        self.send(
            '********************************\n** Welcome to the BBS server. **\n********************************')
        self.current_user = None
        while True:
            try:
                command = str(self.rfile.readline(), 'utf-8').strip().split()
                if command:
                    if command[0] == 'exit':
                        self.conn.close()
                        self.wfile.write(bytes('exit', 'utf-8'))
                        self.info(f'Exit from {self.client_address[0]}({self.client_address[1]})')
                        return
                    self.command_handler(command)
                else:
                    self.wfile.write(bytes('% ', 'utf-8'))
            except Exception as e:
                print(str(e))

    def send(self, msg, res=None, content=None):
        """
        Send message to user
        :param msg: message
        :param res: optional response to client
        :param content: optional byte response to client
        :return: None
        """
        if res is None:
            self.wfile.write(bytes(f'{msg}\n% ', 'utf-8'))
        elif content is None:
            self.wfile.write(bytes(f'{msg}\n% |{res}', 'utf-8'))
        else:
            self.wfile.write(bytes(f'{msg}\n% |{res}|', 'utf-8') + content)

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
        elif command[0] == 'list-file':
            self.list_file_handler(command)
        elif command[0] == 'download':
            self.download_handler(command)
        else:
            self.warning(f'Invalid command from {self.client_address[0]}({self.client_address[1]})\n\t{command}')

    def register_handler(self, command):
        """
        Function handling register command
        Need to tell client bucket name
        :param command: register <username> <email> <password
        :return: None
        """

        # Check arguments
        self.info(f'Register from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if len(command) != 4:
            self.send('Usage: register <username> <email> <password>')
            self.warning(f'Incomplete register command from {self.client_address[0]}({self.client_address[1]})')
            return

        # Check whether username is used
        cursor = self.conn.execute('SELECT Username from USERS WHERE Username=:username', {"username": command[1]})
        if cursor.fetchone() is not None:
            self.send('Username is already used.')
            self.warning(f'Username from {self.client_address[0]}({self.client_address[1]}) is used')
            return

        self.conn.execute(
            'INSERT INTO USERS (Username, Email, Password) VALUES (:username, :email, :password)',
            {"username": command[1], "email": command[2], "password": command[3]})
        self.conn.commit()
        self.send('Register successfully.')

    def login_handler(self, command):
        """
        Function handling login command
        :param command: login <username> <password>
        :return: None
        """

        # Check arguments
        self.info(f'Login from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if len(command) != 3:
            self.send('Usage: login <username> <password>')
            self.warning(f'Incomplete login command from {self.client_address[0]}({self.client_address[1]})')
            return

        # Check if user is already logged in
        if self.current_user:
            self.send('Please logout first.')
            self.warning(f'User from {self.client_address[0]}({self.client_address[1]}) is already logged in')
            return

        cursor = self.conn.execute('SELECT Username, Password FROM USERS WHERE Username=:username',
                                   {"username": command[1]})
        row = cursor.fetchone()
        if row is None:
            self.send('Login failed.')
            self.warning(f"Username entered from {self.client_address[0]}({self.client_address[1]}) isn't in DB")
            return
        if command[2] != row['Password']:
            self.send('Login failed.')
            self.warning(f'Password entered from {self.client_address[0]}({self.client_address[1]}) is wrong')
            return

        self.current_user = row['Username']
        self.send(f'Welcome, {self.current_user}.')

    def logout_handler(self, command):
        """
        Function handling logout command
        :param command: logout
        :return: None
        """
        self.info(f'Logout from {self.client_address[0]}({self.client_address[1]})\n\t{command}')

        if self.current_user:
            self.send(f'Bye, {self.current_user}.')
            self.current_user = None
            self.warning(f'User from {self.client_address[0]}({self.client_address[1]}) log out')
        else:
            self.send('Please login first.')
            self.warning(f'User from {self.client_address[0]}({self.client_address[1]}) is already logged out')

    def whoami_handler(self, command):
        """
        Function handling whoami command
        :param command: whoami
        :return: None
        """
        self.info(f'Whoami from {self.client_address[0]}({self.client_address[1]})\n\t{command}')

        if self.current_user:
            self.send(f'{self.current_user}.')
            self.warning(f'Current user check from {self.client_address[0]}({self.client_address[1]})')
        else:
            self.send('Please login first.')
            self.warning(f'User from {self.client_address[0]}({self.client_address[1]}) is already logged out')

    def list_file_handler(self, command):
        """
        Function handling list-file command
        :param command: list-file ##<key>
        :return: None
        """
        # Check arguments
        self.info(f'List-file from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if len(command) > 2:
            self.send('Usage: list-file ##<key>')
            self.warning(f'Incomplete list-file command from {self.client_address[0]}({self.client_address[1]})')
            return
        elif len(command) == 2:
            key_word = command[1][2:]
            key_word = '%' + key_word + '%'
        else:
            key_word = None

        # Get boards based on given key word
        if key_word:
            cursor = self.conn.execute('SELECT ID, FileName, FileType FROM FILES WHERE FileName LIKE :key_word',
                                       {"key_word": key_word})
        else:
            cursor = self.conn.execute('SELECT ID, FileName, FileType FROM FILES')

        # Show files
        message = '\tIndex\tName\t\tType'
        for row in cursor:
            message = message + f'\n\t{row["ID"]}\t{row["FileName"]}\t{row["FileType"]}'
        self.send(message)

    def download_handler(self, command):
        """
        Function handling download command
        :param command: download <file-id>
        :return: None
        """
        # Check arguments
        self.info(f'Download from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if len(command) != 2:
            self.send('Usage: download <file-id>')
            self.warning(f'Incomplete download command from {self.client_address[0]}({self.client_address[1]})')
            return

        # Check whether file exists
        cursor = self.conn.execute('SELECT FileName, FileType FROM FILES WHERE ID=:id', {"id": command[1]})
        file = cursor.fetchone()
        if file is None:
            self.send('File does not exist.')
            self.warning(f'File ID from {self.client_address[0]}({self.client_address[1]}) does not exist')
            return

        if file["FileType"] == 'binary':
            with open(f'ServerStorage/{file["FileName"]}', 'br') as f:
                self.send('File downloaded successfully.', f'{file["FileName"]}|{file["FileType"]}', f.read())
        else:
            with open(f'ServerStorage/{file["FileName"]}', 'r') as f:
                self.send('File downloaded successfully.', f'{file["FileName"]}|{file["FileType"]}|{f.read()}')


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
    Setup with python3 ./TCPserver.py <host> <port>
    :return: None
    """

    # Check arguments, host and port
    args = parse_arguments()
    host = args.host
    port = args.port

    verbosity = args.verbosity

    # Create database and table
    conn = sqlite3.connect('server_0510002.db')
    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="USERS";')
    if cursor.fetchone() is None:
        conn.execute('''CREATE TABLE USERS (
                            UID      INTEGER PRIMARY KEY AUTOINCREMENT,
                            Username TEXT NOT NULL UNIQUE,
                            Email    TEXT NOT NULL,
                            Password TEXT NOT NULL
                        );''')

    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="FILES";')
    if cursor.fetchone() is None:
        conn.execute('''CREATE TABLE FILES (
                            ID      INTEGER PRIMARY KEY AUTOINCREMENT,
                            FileName TEXT NOT NULL UNIQUE,
                            FileType    TEXT NOT NULL
                        );''')
        conn.execute(
            'INSERT INTO FILES (FileName, FileType) VALUES (:file_name, :file_type)',
            {"file_name": 'test_text.txt', "file_type": 'text'})
        conn.commit()
        conn.execute(
            'INSERT INTO FILES (FileName, FileType) VALUES (:file_name, :file_type)',
            {"file_name": 'hello.bin', "file_type": 'binary'})
        conn.commit()
    conn.close()

    ThreadingTCPServer.allow_reuse_address = True
    ThreadingTCPServer.daemon_threads = True
    with ThreadingTCPServer((host, port), ThreadedServerHandler) as server:
        try:
            print(f'\n{datetime.now()}'
                  , f'\nStarting TCP server at {host}:{port}\nQuit the server with CONTROL-C.\n')
            server.serve_forever()
        except KeyboardInterrupt:
            print('')
            server.shutdown()
