import mimetypes
import os.path
import re
import socket
import sys
import urllib.parse

from antaresia import settings
from antaresia.utils import render_response, http_404


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


class Server(object):
    def __init__(self, host=settings.HOST, port=5000):
        self.addr = (host, port)
        self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serversock.bind(self.addr)
        self.serversock.listen(settings.MAX_CONNECTIONS)

    def read_data_from_socket(self, sock):
        data = b''
        while True:
            data += sock.recv(settings.BUFLEN)
            if b'\r\n\r\n' in data:
                break
        return data.decode('ascii')

    def send_file(self, request, path):
        data = open(path, 'rb').read()
        mimetype = mimetypes.guess_type(path)[0]

        if mimetype is None:
            mimetype = 'octet/stream'

        return render_response(code=200, comment='OK', mimetype=mimetype,
                               body=data)

    def send_directory(self, request, path):
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

    def serve_static(self, request, directory):
        path = os.path.join(directory, request.path)
        if not os.path.exists(path):
            return http_404(request=request,
                            message='Path {0} doesn\'t exist.'.format(path))
        else:
            if os.path.isdir(path):
                index = os.path.join(path, 'index.html')
                if os.path.exists(index):
                    return self.send_file(request, index)
                else:
                    return self.send_directory(request, path)
            else:
                return self.send_file(request, path)

    def run(self, directory):
        print('Server a server on http://{0}:{1}/\n'.format(*self.addr))

        while True:
            client, addr = self.serversock.accept()
            print('Connection from: ', addr)

            data = self.read_data_from_socket(client)
            print(data)

            request = Request(data)
            head, body = self.serve_static(request=request, directory=directory)
            print(head.decode('ascii'))
            client.sendall(head + body)

            client.close()