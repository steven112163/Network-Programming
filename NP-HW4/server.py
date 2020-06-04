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
            self.comment_handler(command)
        elif command[0] == 'mail-to':
            self.mail_to_handler(command)
        elif command[0] == 'list-mail':
            self.list_mail_handler(command)
        elif command[0] == 'retr-mail':
            self.retr_mail_handler(command)
        elif command[0] == 'delete-mail':
            self.delete_mail_handler(command)
        else:
            self.warning(f'Invalid command from {self.client_address[0]}({self.client_address[1]})\n\t{command}')

    def register_handler(self, command):
        """
        Function handling register command
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

        # Insert new user into DB
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

        # Check whether user exists and password is correct
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

    def create_board_handler(self, command):
        """
        Function handling create-board command
        :param command: create-board <name>
        :return: None
        """

        # Check arguments
        self.info(f'Create-board from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if len(command) != 2:
            self.send('Usage: create-board <name>')
            self.warning(f'Incomplete create-board command from {self.client_address[0]}({self.client_address[1]})')
            return

        # Check whether user is logged in
        if not self.current_user:
            self.send('Please login first.')
            self.warning(f'User from {self.client_address[0]}({self.client_address[1]}) is already logged out')
            return

        # Check whether board exists
        cursor = self.conn.execute('SELECT BoardName FROM BOARDS WHERE BoardName=:board_name',
                                   {"board_name": command[1]})
        if cursor.fetchone() is not None:
            self.send('Board already exist.')
            self.warning(f'Board name from {self.client_address[0]}({self.client_address[1]}) exists')
            return

        # Create new board
        self.conn.execute('INSERT INTO BOARDS (BoardName, Moderator) VALUES (:board_name, :moderator)',
                          {"board_name": command[1], "moderator": self.current_user})
        self.conn.commit()
        self.send('Create board successfully.')

    def create_post_handler(self, command):
        """
        Function handling create-post command
        :param command: create-post <board-name> --title <title> --content <content>
        :return: None
        """

        # Check arguments
        self.info(f'Create-post from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if '--title' not in command or '--content' not in command:
            self.send('Usage: create-post <board-name> --title <title> --content <content>')
            self.warning(f'Incomplete create-post command from {self.client_address[0]}({self.client_address[1]})')
            return
        title_idx = command.index('--title')
        content_idx = command.index('--content')
        if title_idx == 1 or content_idx == title_idx + 1 or len(command) == content_idx + 1:
            self.send('Usage: create-post <board-name> --title <title> --content <content>')
            self.warning(f'Incomplete create-post command from {self.client_address[0]}({self.client_address[1]})')
            return

        # Check whether user is logged in
        if not self.current_user:
            self.send('Please login first.')
            self.warning(f'User from {self.client_address[0]}({self.client_address[1]}) is already logged out')
            return

        # Check whether board exists
        cursor = self.conn.execute('SELECT BoardName FROM BOARDS WHERE BoardName=:board_name',
                                   {"board_name": command[1]})
        if cursor.fetchone() is None:
            self.send('Board does not exist.')
            self.warning(f'Board name from {self.client_address[0]}({self.client_address[1]}) does not exist')
            return

        # Get title and content
        title = ' '.join(command[title_idx + 1:content_idx])
        content = ' '.join(command[content_idx + 1:])
        content = '\t--\n\t' + content.replace('<br>', '\n\t') + '\n\t--'

        # Create new post
        self.conn.execute(
            'INSERT INTO POSTS (BoardName, Title, Content, Author, PostDate) VALUES (:board_name, :title, :content, :author, date("now", "localtime"))',
            {"board_name": command[1], "title": title, "content": content, "author": self.current_user})
        self.conn.commit()
        self.send('Create post successfully.')

    def list_board_handler(self, command):
        """
        Function handling list-board command
        :param command: list-board ##<key>
        :return: None
        """

        # Check arguments
        self.info(f'List-board from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if len(command) > 2:
            self.send('Usage: list-board ##<key>')
            self.warning(f'Incomplete list-board command from {self.client_address[0]}({self.client_address[1]})')
            return
        elif len(command) == 2:
            key_word = command[1][2:]
            key_word = '%' + key_word + '%'
        else:
            key_word = None

        # Get boards based on given key word
        if key_word:
            cursor = self.conn.execute('SELECT BoardName, Moderator FROM BOARDS WHERE BoardName LIKE :key_word',
                                       {"key_word": key_word})
        else:
            cursor = self.conn.execute('SELECT BoardName, Moderator FROM BOARDS')

        # Show boards
        message = '\tIndex\tName\tModerator'
        for index, board in enumerate(cursor, 1):
            message = message + f'\n\t{index}\t{board["BoardName"]}\t{board["Moderator"]}'
        self.send(message)

    def list_post_handler(self, command):
        """
        Function handling list-post command
        :param command: list-post <board-name> ##<key>
        :return: None
        """

        # Check arguments
        self.info(f'List-post from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if len(command) > 3 or len(command) == 1:
            self.send('Usage: list-post <board-name> ##<key>')
            self.warning(f'Incomplete list-post command from {self.client_address[0]}({self.client_address[1]})')
            return
        elif len(command) == 3:
            key_word = command[2][2:]
            key_word = '%' + key_word + '%'
        else:
            key_word = None

        # Check whether given board exists
        cursor = self.conn.execute('SELECT BoardName FROM BOARDS WHERE BoardName=:board_name',
                                   {"board_name": command[1]})
        if cursor.fetchone() is None:
            self.send('Board does not exist.')
            self.warning(f'Board name from {self.client_address[0]}({self.client_address[1]}) does not exist')
            return

        # Get posts based on given board name and key word
        if key_word:
            cursor = self.conn.execute(
                'SELECT ID, Title, Author, PostDate FROM POSTS WHERE BoardName=:board_name AND Title LIKE :key_word',
                {"board_name": command[1], "key_word": key_word})
        else:
            cursor = self.conn.execute('SELECT ID, Title, Author, PostDate FROM POSTS WHERE BoardName=:board_name',
                                       {"board_name": command[1]})

        # Show posts
        message = '\tID\tTitle\tAuthor\tDate'
        for post in cursor:
            split_date = post["PostDate"].split('-')
            date = split_date[1] + '/' + split_date[2]
            message = message + f'\n\t{post["ID"]}\t{post["Title"]}\t{post["Author"]}\t{date}'
        self.send(message)

    def read_handler(self, command):
        """
        Function handling read command
        :param command: read <post-id>
        :return: None
        """

        # Check arguments
        self.info(f'Read from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if len(command) != 2:
            self.send('Usage: read <post-id>')
            self.warning(f'Incomplete read command from {self.client_address[0]}({self.client_address[1]})')
            return

        # Check whether post exists
        cursor = self.conn.execute('SELECT Author, Title, PostDate, Content FROM POSTS WHERE ID=:id',
                                   {"id": command[1]})
        post = cursor.fetchone()
        if post is None:
            self.send('Post does not exist.')
            self.warning(f'Post ID from {self.client_address[0]}({self.client_address[1]}) does not exist')
            return

        # Get comments in the post
        cursor = self.conn.execute('SELECT Username, Comment FROM COMMENTS WHERE PostID=:id', {"id": command[1]})

        # Show the post and its comments
        message = f'\tAuthor\t:{post["Author"]}\n' \
                  f'\tTitle\t:{post["Title"]}\n' \
                  f'\tDate\t:{post["PostDate"]}\n' \
                  f'\t{post["Content"]}'
        for comment in cursor:
            message = message + f'\n\t{comment["Username"]}: {comment["Comment"]}'
        self.send(message)

    def delete_post_handler(self, command):
        """
        Function handling delete-post command
        :param command: delete-post <post-id>
        :return: None
        """

        # Check arguments
        self.info(f'Delete-post from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if len(command) != 2:
            self.send('Usage: delete-post <post-id>')
            self.warning(f'Incomplete delete-post command from {self.client_address[0]}({self.client_address[1]})')
            return

        # Check whether user is logged in
        if not self.current_user:
            self.send('Please login first.')
            self.warning(f'User from {self.client_address[0]}({self.client_address[1]}) is already logged out')
            return

        # Check whether post exists
        cursor = self.conn.execute('SELECT ID, Author FROM POSTS WHERE ID=:id', {"id": command[1]})
        post = cursor.fetchone()
        if post is None:
            self.send('Post does not exist.')
            self.warning(f'Post id from {self.client_address[0]}({self.client_address[1]}) does not exist')
            return

        # Check whether user is the post owner
        if post["Author"] != self.current_user:
            self.send('Not the post owner.')
            self.warning(f'User from {self.client_address[0]}({self.client_address[1]}) is not the post owner')
            return

        # Delete post and its comments
        self.conn.execute('DELETE FROM COMMENTS WHERE PostID=:id', {"id": command[1]})
        self.conn.commit()
        self.conn.execute('DELETE FROM POSTS WHERE ID=:id', {"id": command[1]})
        self.conn.commit()
        self.send('Delete successfully.')

    def update_post_handler(self, command):
        """
        Function handling update-post command
        :param command: update-post <post-id> --title/content <new>
        :return: None
        """

        # Check arguments
        self.info(f'Update-post from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if '--title' in command:
            title_idx = command.index('--title')
            content_idx = None
        elif '--content' in command:
            title_idx = None
            content_idx = command.index('--content')
        else:
            self.send('Usage: update-post <post-id> --title/content <new>')
            self.warning(f'Incomplete update-post command from {self.client_address[0]}({self.client_address[1]})')
            return
        if title_idx:
            if title_idx == 1 or len(command) == title_idx + 1:
                self.send('Usage: update-post <post-id> --title/content <new>')
                self.warning(f'Incomplete update-post command from {self.client_address[0]}({self.client_address[1]})')
                return
        elif content_idx:
            if content_idx == 1 or len(command) == content_idx + 1:
                self.send('Usage: update-post <post-id> --title/content <new>')
                self.warning(f'Incomplete update-post command from {self.client_address[0]}({self.client_address[1]})')
                return

        # Check whether user is logged in
        if not self.current_user:
            self.send('Please login first.')
            self.warning(f'User from {self.client_address[0]}({self.client_address[1]}) is already logged out')
            return

        # Check whether post exists
        cursor = self.conn.execute('SELECT Author FROM POSTS WHERE ID=:id', {"id": command[1]})
        post = cursor.fetchone()
        if post is None:
            self.send('Post does not exist.')
            self.warning(f'Post id from {self.client_address[0]}({self.client_address[1]}) does not exist')
            return

        # Check whether user is the post owner
        if post["Author"] != self.current_user:
            self.send('Not the post owner.')
            self.warning(f'User from {self.client_address[0]}({self.client_address[1]}) is not the post owner')
            return

        # Update the post
        if title_idx:
            title = ' '.join(command[title_idx + 1:])
            self.conn.execute('UPDATE POSTS SET Title=:title WHERE ID=:id', {"title": title, "id": command[1]})
            self.conn.commit()
        elif content_idx:
            content = ' '.join(command[content_idx + 1:])
            content = content.replace('<br>', '\n\t')
            self.conn.execute('UPDATE POSTS SET Content=:content WHERE ID=:id', {"content": content, "id": command[1]})
            self.conn.commit()
        self.send('Update successfully.')

    def comment_handler(self, command):
        """
        Function handling comment command
        :param command: comment <post-id> <comment>
        :return: None
        """

        # Check arguments
        self.info(f'Comment from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if len(command) < 3:
            self.send('Usage: comment <post-id> <comment>')
            self.warning(f'Incomplete comment command from {self.client_address[0]}({self.client_address[1]})')
            return

        # Check whether user is logged in
        if not self.current_user:
            self.send('Please login first.')
            self.warning(f'User from {self.client_address[0]}({self.client_address[1]}) is already logged out')
            return

        # Check whether post exists
        cursor = self.conn.execute('SELECT ID FROM POSTS WHERE ID=:id', {"id": command[1]})
        if cursor.fetchone() is None:
            self.send('Post does not exist.')
            self.warning(f'Post id from {self.client_address[0]}({self.client_address[1]}) does not exist')
            return

        # Create comment
        comment = ' '.join(command[2:])
        self.conn.execute('INSERT INTO COMMENTS (PostID, Username, Comment) VALUES (:id, :username, :comment)',
                          {"id": command[1], "username": self.current_user, "comment": comment})
        self.conn.commit()
        self.send('Comment successfully.')

    def mail_to_handler(self, command):
        """
        Function handling mail-to command
        :param command: mail-to <username> --subject <subject> --content <content>
        :return: None
        """

        # Check arguments
        self.info(f'Mail-to from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if '--subject' not in command or '--content' not in command:
            self.send('Usage: mail-to <username> --subject <subject> --content <content>')
            self.warning(f'Incomplete mail-to command from {self.client_address[0]}({self.client_address[1]})')
            return
        subject_idx = command.index('--subject')
        content_idx = command.index('--content')
        if subject_idx == 1 or content_idx == subject_idx + 1 or len(command) == content_idx + 1:
            self.send('Usage: mail-to <username> --subject <subject> --content <content>')
            self.warning(f'Incomplete mail-to command from {self.client_address[0]}({self.client_address[1]})')
            return

        # Check whether user is logged in
        if not self.current_user:
            self.send('Please login first.')
            self.warning(f'User from {self.client_address[0]}({self.client_address[1]}) is already logged out')
            return

        # Check whether user exists
        cursor = self.conn.execute('SELECT Username FROM USERS WHERE Username=:username', {"username": command[1]})
        if cursor.fetchone() is None:
            self.send(f'{command[1]} does not exist.')
            self.warning(f'Username from {self.client_address[0]}({self.client_address[1]}) does not exist')
            return

        # Get subject and content
        subject = ' '.join(command[subject_idx + 1:content_idx])
        content = ' '.join(command[content_idx + 1:])
        content = '\t--\n\t' + content.replace('<br>', '\n\t')

        # Create new mail
        self.conn.execute(
            'INSERT INTO MAILS (Recipient, Subject, Sender, Content, MailDate) VALUES (:recipient, :subject, :sender, :content, date("now", "localtime"))',
            {"recipient": command[1], "subject": subject, "sender": self.current_user, "content": content})
        self.conn.commit()
        self.send('Sent successfully.')

    def list_mail_handler(self, command):
        """
        Function handling list-mail command
        :param command: list-mail
        :return: None
        """

        # Check whether user is logged in
        self.info(f'List-mail from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if not self.current_user:
            self.send('Please login first.')
            self.warning(f'User from {self.client_address[0]}({self.client_address[1]}) is already logged out')
            return

        # Get all user's mails from his/her mailbox
        cursor = self.conn.execute('SELECT Subject, Sender, MailDate FROM MAILS WHERE Recipient=:recipient',
                                   {"recipient": self.current_user})

        # Show mails
        message = '\tID\tSubject\tFrom\tDate'
        for mailID, mail in enumerate(cursor, 1):
            split_date = mail["MailDate"].split('-')
            date = split_date[1] + '/' + split_date[2]
            message = message + f'\n\t{mailID}\t{mail["Subject"]}\t\t{mail["Sender"]}\t{date}'
        self.send(message)

    def retr_mail_handler(self, command):
        """
        Function handling retr-mail command
        :param command: retr-mail <mail#>
        :return: None
        """

        # Check arguments
        self.info(f'Retr-mail from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if len(command) != 2:
            self.send('Usage: retr-mail <mail#>')
            self.warning(f'Incomplete retr-mail command from {self.client_address[0]}({self.client_address[1]})')
            return

        # Check whether user is logged in
        if not self.current_user:
            self.send('Please login first.')
            self.warning(f'User from {self.client_address[0]}({self.client_address[1]}) is already logged out')
            return

        # Check whether mail exists
        cursor = self.conn.execute(
            'SELECT Subject, Sender, Content, MailDate FROM MAILS WHERE Recipient=:recipient',
            {"recipient": self.current_user})
        mail = None
        for mailID, row in enumerate(cursor, 1):
            if mailID == int(command[1]):
                mail = row
                break
        if mail is None:
            self.send('No such mail.')
            self.warning(f'Mail ID from {self.client_address[0]}({self.client_address[1]}) does not exist')
            return

        # Show the mail
        self.send(f'\tSubject\t:{mail["Subject"]}\n'
                  f'\tFrom\t:{mail["Sender"]}\n'
                  f'\tDate\t:{mail["MailDate"]}\n'
                  f'{mail["Content"]}')

    def delete_mail_handler(self, command):
        """
        Function handling delete-mail command
        :param command: delete-mail <mail#>
        :return: None
        """

        # Check arguments
        self.info(f'Delete-mail from {self.client_address[0]}({self.client_address[1]})\n\t{command}')
        if len(command) != 2:
            self.send('Usage: delete-mail <mail#>')
            self.warning(f'Incomplete delete-mail command from {self.client_address[0]}({self.client_address[1]})')
            return

        # Check whether user is logged in
        if not self.current_user:
            self.send('Please login first.')
            self.warning(f'User from {self.client_address[0]}({self.client_address[1]}) is already logged out')
            return

        # Check whether mail exists
        cursor = self.conn.execute(
            'SELECT ID FROM MAILS WHERE Recipient=:recipient', {"recipient": self.current_user})
        mail = None
        for mailID, row in enumerate(cursor, 1):
            if mailID == int(command[1]):
                mail = row
                break
        if mail is None:
            self.send('No such mail.')
            self.warning(f'Mail ID from {self.client_address[0]}({self.client_address[1]}) does not exist')
            return

        # Delete the mail
        self.conn.execute('DELETE FROM MAILS WHERE Recipient=:username AND ID=:id',
                          {"username": self.current_user, "id": mail["ID"]})
        self.conn.commit()
        self.send('Mail deleted.')


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
    Setup with python3 ./server.py <host> <port>
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

    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="BOARDS";')
    if cursor.fetchone() is None:
        conn.execute('''CREATE TABLE BOARDS(
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            BoardName TEXT NOT NULL UNIQUE,
                            Moderator TEXT NOT NULL,
                            FOREIGN KEY(Moderator) REFERENCES USERS(Username)
                        );''')

    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="POSTS";')
    if cursor.fetchone() is None:
        conn.execute('''CREATE TABLE POSTS(
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            BoardName TEXT NOT NULL,
                            Title TEXT NOT NULL,
                            Content TEXT NOT NULL,
                            Author TEXT NOT NULL,
                            PostDate TEXT NOT NULL,
                            FOREIGN KEY(BoardName) REFERENCES BOARDS(BoardName),
                            FOREIGN KEY(Author) REFERENCES USERS(Username)
                        );''')

    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="COMMENTS";')
    if cursor.fetchone() is None:
        conn.execute('''CREATE TABLE COMMENTS(
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            PostID INTEGER NOT NULL,
                            Username TEXT NOT NULL,
                            Comment TEXT NOT NULL,
                            FOREIGN KEY(PostID) REFERENCES POSTS(ID),
                            FOREIGN KEY(Username) REFERENCES USERS(Username)
                        );''')

    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="MAILS";')
    if cursor.fetchone() is None:
        conn.execute('''CREATE TABLE MAILS(
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            Recipient TEXT NOT NULL,
                            Subject TEXT NOT NULL,
                            Sender TEXT NOT NULL,
                            MailDate TEXT NOT NULL,
                            Content TEXT NOT NULL,
                            FOREIGN KEY(Recipient) REFERENCES USERS(Username),
                            FOREIGN KEY(Sender) REFERENCES USERS(Username)
                        );''')
    conn.close()

    ThreadingTCPServer.allow_reuse_address = True
    ThreadingTCPServer.daemon_threads = True
    with ThreadingTCPServer((host, port), ThreadedServerHandler) as server:
        try:
            print(f'\n{datetime.now()}'
                  , f'\nStarting server at {host}:{port}\nQuit the server with CONTROL-C.\n')
            server.serve_forever()
        except KeyboardInterrupt:
            print('')
            server.shutdown()
