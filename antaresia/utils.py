from antaresia.models import render_response


def http_404(request, message):
    body = '<h2>{0}</h2>'.format(message)
    return render_response(code=404, comment='Not Found',
                           mimetype='text/html', body=body.encode('ascii'))