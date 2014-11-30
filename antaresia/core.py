import socket
import sys

from antaresia.models import Request, serve_static

HOST = '127.0.0.1'
MAX_CONNECTIONS = 100
BUFLEN = 1024


def read_data_from_socket(sock):
    data = b''
    while True:
        data += sock.recv(BUFLEN)
        if b'\r\n\r\n' in data:
            break
    return data.decode('ascii')


def run_server(port, directory):
    print('Server a server on http://{0}:{1}/\n'.format(HOST, port))

    addr = (HOST, port)
    serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversock.bind(addr)
    serversock.listen(MAX_CONNECTIONS)

    while True:
        client, addr = serversock.accept()
        print('Connection from: ', addr)

        data = read_data_from_socket(client)
        print(data)

        request = Request(data)
        head, body = serve_static(request=request, directory=directory)
        print(head.decode('ascii'))
        client.sendall(head + body)

        client.close()


def main():
    if len(sys.argv) != 3:
        print('Usage: {0} PORT DIR'.format(sys.argv[0]))
        sys.exit(1)
    else:
        port = int(sys.argv[1])
        directory = sys.argv[2]
        run_server(port, directory)