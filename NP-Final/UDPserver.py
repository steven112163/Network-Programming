import sys
import argparse
import struct
import socket
import threading
from select import select


def parse_arguments():
    """
    Generate an argument parser
    :return: argparse.Namespace an object containing all required arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('numOfClients', help='number of client connections', nargs='?', type=int)
    parser.add_argument('port', help='port number', nargs='?', type=int)
    parser.add_argument('-v', '--verbosity', help='verbosity level (0-2)', default=0, type=int)
    return parser.parse_args()


def download_handler(num):
    global host, port
    print(f'Start thread with {host}:{port + num}')
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

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as so:
        so.setblocking(False)
        so.bind((host, port + num))

        # Get file size from client
        ready = select([so], [], [])
        res_packet = so.recv(1032)
        file_size = int(str(res_packet, 'utf-8'))

        # Start receiving
        content = b''
        while True:
            # Get response from client
            while True:
                ready = select([so], [], [], 0.1)
                if not ready[0]:
                    retransmission_flag = True
                    break
                res_packet, address = so.recvfrom(1032)
                if res_packet:
                    break
            if retransmission_flag:
                so.sendto(response_struct.pack(packet_seq - 1, end_flag), address)
                retransmission_flag = False
                continue
            res_packet = packet_struct.unpack(res_packet)

            # Tell client to retransmit if sequence number is different
            if res_packet[0] != packet_seq:
                so.sendto(response_struct.pack(packet_seq - 1, end_flag), address)
            else:
                if res_packet[1] == 1:
                    end_flag = 1
                so.sendto(response_struct.pack(packet_seq, end_flag), address)
                packet_seq = packet_seq + 1
                content = content + res_packet[2]
                content = content[:file_size]

            sys.stdout.write('\r')
            percentage = int(len(content) / int(file_size)) * 20
            sys.stdout.write(f"{port + num}: [{'=' * percentage}{' ' * (20 - percentage)}] {5 * percentage}%")
            sys.stdout.flush()

            if end_flag == 1:
                print()
                break
        with open(f'file{num}.bin', 'bw') as f:
            f.write(content)


if __name__ == '__main__':
    """
    Main running server
    Setup with python3 ./UDPserver.py <numOfClients> <port> [-v (0-2)]
    :return: None
    """

    # Check arguments, host and port
    args = parse_arguments()
    num_of_clients = args.numOfClients
    host = 'localhost'
    port = args.port

    verbosity = args.verbosity

    threads = []
    for i in range(num_of_clients):
        threads.append(threading.Thread(target=download_handler, args=(i,)))
        threads[i].start()
    for i in range(num_of_clients):
        threads[i].join()

