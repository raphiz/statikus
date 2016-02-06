import os
from contextlib import contextmanager
from http.server import HTTPServer, SimpleHTTPRequestHandler


@contextmanager
def pushd(newDir):
    previousDir = os.getcwd()
    os.chdir(newDir)
    try:
        yield
    finally:
        os.chdir(previousDir)


class HttpRequestLoggingHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def serve(host, port):
    try:
        server_address = ()
        print("Serving at http://%s:%s" % (host, port))
        httpd = HTTPServer((host, port), HttpRequestLoggingHandler)
        httpd.serve_forever()
    except KeyboardInterrupt as e:
        print("Shutting down...")
