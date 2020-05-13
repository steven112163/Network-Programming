import socket
import argparse


def parse_arguments():
    """
    Generate an argument parser
    :return: argparse.Namespace an object containing all required arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='server IP', nargs='?')
    parser.add_argument('port', help='server port', nargs='?', type=int)
    return parser.parse_args()


def get_message(sock):
    """
    Get message from server
    :return: str of message
    """
    message = []
    while True:
        part = sock.recv(1024)
        message.append(str(part, 'utf-8'))
        if len(part) < 1024:
            break

    return ''.join(message)


def response_handler(res):
    """
    Function handling responses
    :param res: response from server
    :return: Message needs to be showed. And True if response is 'exit', False otherwise.
    """
    res = res.split('|')
    if res[0] == 'exit':
        return '', True

    return res[0], False


def register_handler(res):
    """
    Function handling register response
    :param res: response from server
    :return: None
    """
    pass


def create_post_handler(res):
    """
    Function handling create-post response
    :param res: response from server
    :return: None
    """
    pass


def read_handler(res):
    """
    Function handling read response
    :param res: response from server
    :return: None
    """
    pass


def delete_handler(res):
    """
    Function handling delete response
    :param res: response from server
    :return: None
    """
    pass


def update_post_handler(res):
    """
    Function handling update-post response
    :param res: response from server
    :return: None
    """
    pass


def comment_handler(res):
    """
    Function handling comment response
    :param res: response from server
    :return: None
    """
    pass


if __name__ == '__main__':
    """
    Client
    Setup with python3 ./client.py <host> <port>
    :return: None
    """

    # Check arguments, host and port
    args = parse_arguments()
    host = args.host
    port = args.port

    # Start client process
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as so:
        try:
            so.connect((host, port))
            print(f'{get_message(so)}', end='', flush=True)
            while True:
                command = input()
                so.sendall(bytes(command + '\n', 'utf-8'))
                raw_response = get_message(so)
                response, exitOrNot = response_handler(raw_response)
                if exitOrNot:
                    so.close()
                    break
                print(f'{response}', end='', flush=True)
        except KeyboardInterrupt:
            pass
