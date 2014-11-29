#!/usr/bin/env python3

import mimetypes
import os
import socket
import sys
import re
import urllib.parse

HOST = '127.0.0.1'
MAX_CONNECTIONS = 100
BUFLEN = 1024


class Request(object):
    def __init__(self, data):
        first_line, *headers_lines = re.split('\r\n', data)
        self.method, self.path, self.http_version = first_line.split(' ')
        self.path = urllib.parse.unquote(self.path[1:], encoding=sys.getfilesystemencoding())
        self.headers = {}

        for line in headers_lines:
            if line:
                key, value = line.split(': ')
                self.headers[key] = value


def render_response(code, comment, mimetype, body):
    assert type(body) == bytes
    headers = (
        'HTTP/1.0 {0} {1}\r\n'
        'Content-Type: {2}\r\n'
        'Content-Length: {3}\r\n\r\n'
    ).format(code, comment, mimetype, len(body)).encode('ascii')
    return headers, body


def read_data_from_socket(sock):
    data = b''
    while True:
        data += sock.recv(BUFLEN)
        if b'\r\n\r\n' in data:
            break
    return data.decode('ascii')


def http_404(request, message):
    body = '<h2>{0}</h2>'.format(message)
    return render_response(code=404, comment='Not Found',
                           mimetype='text/html', body=body.encode('ascii'))


def send_file(request, path):
    data = open(path, 'rb').read()
    mimetype = mimetypes.guess_type(path)[0]

    if mimetype is None:
        mimetype = 'octet/stream'

    return render_response(code=200, comment='OK', mimetype=mimetype,
                           body=data)


def send_directory(request, path):
    files = [(not os.path.isdir(os.path.join(path, name)), name)
             for name in os.listdir(path)]
    files.sort()

    files = [filename + ('' if isfile else '/') for isfile, filename in files]

    encoding_line = '<meta charset="{encoding}">'
    file_line = '<div><a href="{filename}">{filename}</a></div>'
    data = (
        [encoding_line.format(encoding=sys.getfilesystemencoding())] +
        [file_line.format(filename=filename) for filename in files]
    )
    return render_response(code=200, comment='OK', mimetype='text/html',
                           body='\n'.join(data).encode(sys.getfilesystemencoding()))


def serve_static(request, directory):
    path = os.path.join(directory, request.path)
    if not os.path.exists(path):
        return http_404(request=request,
                        message='Path {0} doesn\'t exist.'.format(path))
    else:
        if os.path.isdir(path):
            index = os.path.join(path, 'index.html')
            if os.path.exists(index):
                return send_file(request, index)
            else:
                return send_directory(request, path)
        else:
            return send_file(request, path)


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


if __name__ == '__main__':
    main()