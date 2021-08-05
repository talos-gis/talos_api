def get_format(formats, **kwargs):
    of = formats[0]
    if 'http_request' in kwargs:
        http_request = kwargs['http_request']
        best = http_request.accept_mimetypes.best
        for f in formats:
            if f in best:
                of = f
    return of
