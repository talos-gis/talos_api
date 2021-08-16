def get_format(formats, default=None, **kwargs):
    of = default if default is not None else formats[0]
    if 'http_request' in kwargs:
        http_request = kwargs['http_request']
        best = http_request.accept_mimetypes.best
        for f in formats:
            if f in best:
                of = f
    return of
