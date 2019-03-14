
def application(environ, start_response):
    method = environ['REQUEST_METHOD']
    path = environ['PATH_INFO']
    start_response('200 OK', [('Content-Type', 'text/html')])
    print(type(method))
    print(type(path))
    print(path)
    # return [b'<h1>Hello, web!</h1>']
    if method == 'GET' and path == '/':
        return ['<h1>Hello, web!</h1>'.encode('utf-8')]
    if method == 'GET' and path == '/start':
        return ['<h1>start!</h1>'.encode('utf-8')]
