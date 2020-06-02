import sys
import argparse
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
        global groups, users, counter
        users[f'user{counter}'] = [self.client_address]
        groups[f'user{counter}'] = {f'user{counter}': self.client_address}
        self.current_user = f'user{counter}'
        counter = counter + 1
        print(f'New connection from {self.client_address[0]}:{self.client_address[1]} ({self.current_user})')
        self.info(f'Connection from {self.client_address[0]}({self.client_address[1]})')
        self.send(
            '********************************\n** Welcome to the BBS server. **\n********************************')

        while True:
            try:
                command = str(self.rfile.readline(), 'utf-8').strip().split()
                if command:
                    if command[0] == 'exit':
                        self.wfile.write(bytes('exit', 'utf-8'))
                        users.pop(self.current_user, None)
                        groups.pop(self.current_user, None)
                        for g in groups:
                            if self.current_user in g:
                                g.pop(self.current_user, None)
                        print(f'({self.current_user}) {self.client_address[0]}:{self.client_address[1]} disconnected')
                        self.info(f'Exit from {self.client_address[0]}({self.client_address[1]})')
                        return
                    self.command_handler(command)
                else:
                    self.wfile.write(bytes('% ', 'utf-8'))
            except Exception as e:
                print(str(e))

    def send(self, msg):
        """
        Send message to user
        :param msg: message
        :return: None
        """
        self.wfile.write(bytes(f'{msg}\n% ', 'utf-8'))

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
        if command[0] == 'list-users':
            self.list_users(command)
        elif command[0] == 'group-add':
            self.group_add(command)
        elif command[0] == 'group-remove':
            self.group_remove(command)
        elif command[0] == 'group-send':
            self.group_send(command)
        elif command[0] == 'get-message':
            self.get_message()
        else:
            self.warning(f'Invalid command from {self.client_address[0]}({self.client_address[1]})\n\t{command}')

    def list_users(self, command):
        """
        Function handling list-users command
        :param command: list-users
        :return: None
        """
        message = ''
        for k in users.keys():
            message = message + f'{k}\n'
        self.send(message[:len(message) - 1])

    def group_add(self, command):
        """
        Function handling group-add command
        :param command: group-add <username>
        :return: None
        """

        # Check arguments
        if len(command) != 2:
            self.send('Usage: group-add <username>')
            self.warning(f'Incomplete group-add command from {self.client_address[0]}({self.client_address[1]})')
            return

        # Check whether user exists
        if command[1] not in users:
            self.send(f'{command[1]} does not exist.')
            self.warning(f'Username from {self.client_address[0]}({self.client_address[1]}) does not exist')
            return

        # Check duplicate username
        if command[1] in groups[self.current_user]:
            self.send(f'Add {command[1]} successfully.')
            self.warning(f'Duplicate username from {self.client_address[0]}({self.client_address[1]})')
            return

        # Add username into current user's group
        groups[self.current_user][command[1]] = users[command[1]][0]
        self.info(f'{groups[self.current_user]}')
        self.send(f'Add {command[1]} successfully.')

    def group_remove(self, command):
        """
        Function handling group-remove command
        :param command: group-remove <username>
        :return: None
        """

        # Check arguments
        if len(command) != 2:
            self.send('Usage: group-remove <username>')
            self.warning(f'Incomplete group-remove command from {self.client_address[0]}({self.client_address[1]})')
            return

        # Check whether user exists
        if command[1] not in users or command[1] not in groups[self.current_user]:
            self.send(f'{command[1]} does not exist.')
            self.warning(f'Username from {self.client_address[0]}({self.client_address[1]}) does not exist')
            return

        # Remove username from current user's group
        groups[self.current_user].pop(command[1], None)
        self.info(f'{groups[self.current_user]}')
        self.send(f'Remove {command[1]} successfully.')

    def group_send(self, command):
        """
        Function handling group-send command
        :param command: group-send <message>
        :return: None
        """

        # Check arguments
        if len(command) < 2:
            self.send('Usage: group-send <message>')
            self.warning(f'Incomplete group-send command from {self.client_address[0]}({self.client_address[1]})')
            return

        # Send message to all users in current user's group
        message = ' '.join(command[1:])
        for k, ipport in groups[self.current_user].items():
            users[k].append(message)
        self.wfile.write(bytes('% ', 'utf-8'))

    def get_message(self):
        """
        Function handling get-message command
        :return: None
        """
        # Get all messages of current user and delete it all
        self.info(f'Get message from ({self.current_user}) {self.client_address[0]}({self.client_address[1]})')
        message = '\n'.join(users[self.current_user][1:])
        users[self.current_user] = [users[self.current_user][0]]
        self.send(f'\n{message}')


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
    Setup with python3 ./TCPserver.py <host> <port> [-v (0-2)]
    :return: None
    """

    # Check arguments, host and port
    args = parse_arguments()
    host = args.host
    port = args.port

    verbosity = args.verbosity

    # Setup users dict
    users = {}
    groups = {}
    counter = 1

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

