import socket
import argparse
import struct
import os
from select import select
from collections import OrderedDict


def parse_arguments():
    """
    Generate an argument parser
    :return: argparse.Namespace an object containing all required arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='server IP', nargs='?')
    parser.add_argument('port', help='server port', nargs='?', type=int)
    parser.add_argument('fileName', help='file name', nargs='?')
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


if __name__ == '__main__':
    """
    Client
    Setup with python3 ./UDPclient.py <server-IP> <server-port> <file-name>
    :return: None
    """

    # Check arguments, host and port
    args = parse_arguments()
    host = args.host
    port = args.port
    name = args.fileName

    # Start client process
    # Setup packet structure with (packet_seq, end, 1024 characters)
    # Packet is 4 + 4 + 1024 = 1032 bytes
    packet_struct = struct.Struct('II1024s')

    # Setup response structure with (packet_seq, end)
    # Packet is 4 + 4 = 8 bytes
    response_struct = struct.Struct('II')

    # Sequence number of packet that we have to send next time
    packet_seq = 1

    # Setup ordered dict for storing previous data
    previous_data = OrderedDict()

    # Setup retransmission flag
    retransmission_flag = False

    file_size = os.path.getsize(name)
    with open(name, 'rb') as f:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as so:
            # Tell server the file size
            so.sendto(bytes(f'{file_size}', 'utf-8'), (host, port))

            # Start sending
            while True:
                # Send previous data if retransmission is needed, send file data otherwise
                if retransmission_flag:
                    data = previous_data[packet_seq]
                else:
                    data = f.read(1024)
                    previous_data[packet_seq] = data

                # Tell server if it's end of file
                end = 1 if data == b'' else 0
                so.sendto(packet_struct.pack(packet_seq, end, data), (host, port))
                print(f'Send seq:{packet_seq}, end:{end} to ({host}, {port})')

                # Refrain number of data in previous_data to 10
                if len(previous_data) > 10:
                    previous_data.popitem(last=False)

                # Get response from server
                while True:
                    res_packet = so.recv(8)
                    if res_packet:
                        break
                res = response_struct.unpack(res_packet)

                # Flag retransmission if sequence number is different
                if res[0] != packet_seq:
                    retransmission_flag = True
                else:
                    packet_seq = packet_seq + 1
                    retransmission_flag = False
                    # If server receives all packets, then break
                    if end == 1:
                        break

