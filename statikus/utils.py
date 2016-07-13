import os
from contextlib import contextmanager
from http.server import HTTPServer, SimpleHTTPRequestHandler
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


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


class MyHandler(PatternMatchingEventHandler):

    def __init__(self, run):
        # TODO make ignore_patterns configurable!
        super(MyHandler, self).__init__(ignore_patterns=["./_site/*", "./venv/*"],
                                        ignore_directories=True)
        self._run = run
        self.abspath = os.path.abspath('./')

    def on_any_event(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        if event.src_path[-3:] == '.py':
            print('Warning: python file has changed - restart the server!')
            return

        with pushd(self.abspath):
            print('Regenerate page...')
            self._run(False)


def serve(host, port, destination_dir, run):
    try:
        observer = Observer()
        observer.schedule(MyHandler(run), './', recursive=True)
        observer.start()

        with pushd(destination_dir):
            print("Serving at http://%s:%s" % (host, port))
            httpd = HTTPServer((host, port), HttpRequestLoggingHandler)
            httpd.serve_forever()

    except KeyboardInterrupt as e:
        print("Shutting down...")
