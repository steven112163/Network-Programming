import socket
import argparse
import struct
import sys
from select import select


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
        ready = select([sock], [], [])
        if ready[0]:
            part = sock.recv(1024)
            if not part:
                continue
            message.append(str(part, 'utf-8'))
            if len(part) < 1024:
                break

    return ''.join(message)


def response_handler(raw_res, sock):
    """
    Function handling responses
    :param raw_res: response from server
    :param sock: socket object
    :return: Message needs to be showed. And True if response is 'exit', False otherwise.
    """
    res = raw_res.split('|')
    if res[0] == 'exit':
        return '', True
    elif res[0] == 'File downloaded successfully.\n% ':
        download_handler(res, sock)

    return res[0], False


def download_handler(res, sock):
    """
    Function handling download response
    :param res: response from server
    :param sock: socket object
    :return: None
    """
    # Setup packet structure with (packet_seq, end, 1024 characters)
    # Packet is 4 + 4 + 1024 = 1032 bytes
    packet_struct = struct.Struct('II1024s')

    # Setup response structure with (packet_seq)
    # Packet is 4 + 4 = 8 bytes
    response_struct = struct.Struct('II')

    # Sequence number of packet that we expect
    packet_seq = 1

    # Setup flags
    retransmission_flag = False
    end_flag = 0

    # Connect to downloading port
    temp_port = int(res[4])

    # Tell server to start
    sock.sendto(response_struct.pack(packet_seq, end_flag), (host, temp_port))

    # Start receiving
    content = b''
    while True:
        # Get response from server
        while True:
            ready = select([sock], [], [], 0.1)
            if not ready[0]:
                retransmission_flag = True
                break
            res_packet = sock.recv(1032)
            if res_packet:
                break
        if retransmission_flag:
            sock.sendto(response_struct.pack(packet_seq - 1, end_flag), (host, temp_port))
            retransmission_flag = False
            continue
        res_packet = packet_struct.unpack(res_packet)

        # Tell server to retransmit if sequence number is different
        if res_packet[0] != packet_seq:
            sock.sendto(response_struct.pack(packet_seq - 1, end_flag), (host, temp_port))
        else:
            if res_packet[1] == 1:
                end_flag = 1
            sock.sendto(response_struct.pack(packet_seq, end_flag), (host, temp_port))
            packet_seq = packet_seq + 1
            content = content + res_packet[2]
            content = content[:int(res[3])]

        sys.stdout.write('\r')
        percentage = int(len(content) / int(res[3])) * 20
        sys.stdout.write(f"[{'='*percentage}{' '*(20-percentage)}] {5*percentage}%")
        sys.stdout.flush()

        if end_flag == 1:
            print()
            break

    if res[2] == 'binary':
        with open(f'ClientStorage/{res[1]}', 'bw') as f:
            f.write(content)
    else:
        content = str(content, 'utf-8')
        with open(f'ClientStorage/{res[1]}', 'w') as f:
            f.write(content)


if __name__ == '__main__':
    """
    Client
    Setup with python3 ./UDPclient.py <host> <port>
    :return: None
    """

    # Check arguments, host and port
    args = parse_arguments()
    host = args.host
    port = args.port

    # Start client process
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as so:
        so.setblocking(False)
        try:
            so.sendto(bytes('', 'utf-8'), (host, port))
            print(f'{get_message(so)}', end='', flush=True)
            while True:
                command = input() + '\n'
                so.sendto(bytes(command, 'utf-8'), (host, port))
                raw_response = get_message(so)
                response, exitOrNot = response_handler(raw_response, so)
                if exitOrNot:
                    so.close()
                    break
                print(f'{response}', end='', flush=True)
        except KeyboardInterrupt:
            pass
