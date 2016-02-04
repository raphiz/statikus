from urllib.parse import urljoin
import os
from jinja2 import Environment, FileSystemLoader
import shutil
from contextlib import contextmanager
from collections import defaultdict
import jinja2

__title__ = 'statikus'
__version__ = '0.1.0-dev'
__author__ = 'Raphael Zimmermann'
__license__ = 'MIT'


@contextmanager
def pushd(newDir):
    previousDir = os.getcwd()
    os.chdir(newDir)
    yield
    os.chdir(previousDir)


class Statikus():

    def __init__(self, **kwargs):
        self.options = kwargs
        self.destination_dir = '_site/'
        self.assets_dir = self.destination_dir + '/assets/'
        self.assets = defaultdict(list)
        self.routes = {}

    def requires_asset(self, category, path):
        def decorator(f):
            self.assets[category].append(path)
            return f
        return decorator

    def route(self, path):
        def decorator(f):
            self.routes[path] = f
            return f
        return decorator

    def run(self):

        env = Environment(loader=FileSystemLoader(os.path.abspath('templates/')))

        # TODO: support generators (when using variables/wildcards in URLs)
        # if it contains <name>, the method must provide it as dict / tuple
        # if it contains *, the method must provide the full path!

        if os.path.exists(self.destination_dir):
            # This is pretty ugly....
            shutil.rmtree(self.destination_dir)

        os.makedirs(self.destination_dir)
        with pushd(self.destination_dir):
            # self.assets_processor(self.assets_dir, self.assets)
            # TODO: load route from url 
            for route, fn in self.routes.items():
                if route[-1] == '/':
                    # TODO: what if exists?  | what if not index!
                    os.makedirs(route)

                    params = [self.options[key] for key in fn.__code__.co_varnames]
                    context = fn(*params)
                    context['assets'] = self.assets
                    context['options'] = self.options

                    # What about methods which do not have a coresponding template?
                    # Should there be a coresponding "template" decorator?
                    template = env.get_template(fn.__code__.co_name + '.html')

                    with open(route + 'index.html', 'w') as f:
                        f.write(template.render(**context))
