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


if __name__ == '__main__':
    """
    Client
    Setup with python3 ./TCPclient.py <host> <port>
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
                command = input() + '\n'
                so.sendall(bytes(command, 'utf-8'))
                response = get_message(so)
                if response == 'exit':
                    so.close()
                    break
                print(f'{response}', end='', flush=True)
        except KeyboardInterrupt:
            pass
