import threading, sys
from socketserver import ThreadingTCPServer, StreamRequestHandler


class ThreadedServerHandler(StreamRequestHandler):
    def handle(self):
        print('New connection')
        self.wfile.write(bytes('# ', 'utf-8'))
        while True:
            try:
                data = str(self.rfile.readline(), 'utf-8').strip()
                if data:
                    if data == 'exit':
                        return
                    current_thread = threading.current_thread()
                    self.wfile.write(bytes(f'{current_thread.name}: {data}\n# ', 'utf-8'))
            except Exception as e:
                print(str(e))


def main():
    if len(sys.argv) != 2:
        print("Usage: ./server <port>")
        return

    host = 'localhost'
    try:
        port = int(sys.argv[1])
    except:
        print("Usage: ./server <port>")
        return

    ThreadingTCPServer.allow_reuse_address = True
    with ThreadingTCPServer((host, port), ThreadedServerHandler) as server:
        print("Server loop running")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\n')
            server.shutdown()


if __name__ == '__main__':
    main()
