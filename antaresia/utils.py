def render_response(code, comment, mimetype, body):
    assert type(body) == bytes
    headers = (
        'HTTP/1.0 {0} {1}\r\n'
        'Content-Type: {2}\r\n'
        'Content-Length: {3}\r\n\r\n'
    ).format(code, comment, mimetype, len(body)).encode('ascii')
    return headers, body


def http_404(request, message):
    body = '<h2>{0}</h2>'.format(message)
    return render_response(code=404, comment='Not Found',
                           mimetype='text/html', body=body.encode('ascii'))