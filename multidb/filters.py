READ_ONLY_METHODS = ('GET', 'TRACE', 'HEAD', 'OPTIONS')


def request_method_filter(request):
    return request.method not in READ_ONLY_METHODS
