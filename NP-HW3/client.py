import socket
import argparse
import boto3


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
    elif res[0] == 'Register successfully.':
        register_handler(res)
    elif res[0] == 'Create post successfully.':
        create_post_handler(res)
    elif res[0] == 'Delete successfully.':
        delete_handler(res)
    elif res[0] == 'Update successfully.' and len(res) > 1:
        update_post_handler(res)
    elif res[0] == 'Comment successfully.':
        comment_handler(res)
    elif res[0] == "It's read command":
        return read_handler(res), False

    return res[0], False


def register_handler(res):
    """
    Function handling register response
    :param res: response from server
    :return: None
    """
    global s3
    s3.create_bucket(Bucket=res[1])


def create_post_handler(res):
    """
    Function handling create-post response
    :param res: response from server
    :return: None
    """
    global s3
    s3.put_object(
        Bucket=res[1],
        Key=res[2],
        Body=res[3]
    )


def read_handler(res):
    """
    Function handling read response
    :param res: response from server
    :return: None
    """
    global s3
    content = s3.Object(res[1], res[2]).get()['Body'].read().decode()
    return f'\tAuthor\t:{res[3]}\n'\
           f'\tTitle\t:{res[4]}\n'\
           f'\tDate\t:{res[5]}\n'\
           f'{content}'


def delete_handler(res):
    """
    Function handling delete response
    :param res: response from server
    :return: None
    """
    global s3
    s3.Object(res[1], res[2]).delete()


def update_post_handler(res):
    """
    Function handling update-post response
    :param res: response from server
    :return: None
    """
    global s3
    # TODO: Need to check
    s3.put_object(
        Bucket=res[1],
        Key=res[2],
        Body=res[3]
    )


def comment_handler(res):
    """
    Function handling comment response
    :param res: response from server
    :return: None
    """
    global s3
    content = s3.Object(res[1], res[2]).get()['Body'].read().decode()
    content = content + f'\n\t{res[3]}'
    # TODO: Need to check
    s3.put_object(
        Bucket=res[1],
        Key=res[2],
        Body=content
    )


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

    # Connect to S3
    s3 = boto3.resource('s3')

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
