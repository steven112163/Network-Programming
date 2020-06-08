import socket
import argparse
import sys
from select import select
from kafka import KafkaConsumer


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


def response_handler(raw_res):
    """
    Function handling responses
    :param raw_res: response from server
    :return: Message needs to be showed. And True if response is 'exit', False otherwise.
    """
    res = raw_res.split('|')
    if res[0] == 'exit':
        return '', True
    elif res[0] == 'Subscribe successfully.\n% ':
        subscribe_handler(res)
    elif res[0] == 'Unsubscribe successfully.\n% ':
        unsubscribe_handler(res)
    elif res[0].startswith('Bye'):
        logout_handler(res)

    return res[0], False


def logout_handler(res):
    """
    Function handling logout response
    :param res: response from server
    :return: None
    """
    global consumer
    consumer.unsubscribe()


def subscribe_handler(res):
    """
    Function handling subscribe response
    :param res: response from server
    :return: None
    """
    global consumer
    subs = consumer.subscription()
    if subs is not None:
        subs.add(res[1])
        consumer.subscribe(list(subs))
    else:
        consumer.subscribe([res[1]])


def unsubscribe_handler(res):
    """
    Function handling unsubscribe response
    :param res: response from server
    :return: None
    """
    global consumer
    subs = consumer.subscription()
    if subs is not None:
        for s in res[1:]:
            try:
                subs.remove(s)
            except KeyError:
                pass
        consumer.subscribe(list(subs))


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

    # Setup Kafka consumer
    consumer = KafkaConsumer(consumer_timeout_ms=500)

    # Start client process
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as so:
        try:
            so.connect((host, port))
            print(f'{get_message(so)}', end='', flush=True)
            while True:
                ready = select([sys.stdin], [], [], 0.5)
                if ready[0]:
                    command = input() + '\n'
                    so.sendall(bytes(command, 'utf-8'))
                    raw_response = get_message(so)
                    response, exitOrNot = response_handler(raw_response)
                    if exitOrNot:
                        so.close()
                        break
                    print(f'{response}', end='', flush=True)
                else:
                    consumer.poll()
                    for msg in consumer:
                        print(str(msg.value, 'utf-8'))
                        print('% ', end='', flush=True)
        except KeyboardInterrupt:
            pass
