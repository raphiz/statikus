import os
from jinja2 import Environment, FileSystemLoader
import shutil
import glob
import inspect
from collections import defaultdict
from .utils import pushd
from .exceptions import URLParseException
from .url import is_variable, process_variable_url, cleanup

__title__ = 'statikus'
__version__ = '0.1.0.dev0'
__author__ = 'Raphael Zimmermann'
__license__ = 'MIT'


class Page:

    def __init__(self, data, url_variables):
        self.data = data
        self.variables = url_variables
        self.custom_url = None

    def touch(self, route):
        path = route
        if route[-1] == '/':
            path = route + 'index.html'
        dir_name = os.path.dirname(path[1:])
        if len(dir_name) > 0 and not os.path.exists(dir_name):
            os.makedirs(dir_name)
        return path[1:]


class JinjaPage(Page):

    def render(self, route, context):
        loader = FileSystemLoader(os.path.join(context['project_root'], 'templates/'))
        env = Environment(loader=loader)
        jinja_context = self.data
        jinja_context['assets'] = context['assets']
        jinja_context['options'] = context['options']
        template = env.get_template(context['source'] + '.html')
        with open(self.touch(route), 'w') as f:
            f.write(template.render(**jinja_context))
        return route, self


class RawPage(Page):

    def render(self, route, context):
        with open(self.touch(route), 'w') as f:
            f.write(self.data)
        return route, self


class Asset():

    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def __getattr__(self, name):
        if name == 'url':
            # TODO: find a better solution...
            return '/' + self.destination
        super(AccessCounter, self).__delattr__(name)


class Statikus():

    def __init__(self, **kwargs):
        self.options = kwargs
        self.destination_dir = '_site/'
        self.project_root = os.getcwd()
        self.assets_dir = self.destination_dir + '/assets/'
        self.assets = defaultdict(set)
        self.routes = {}

    def add_asset(self, category, path):
        if hasattr(path, '__iter__') and not isinstance(path, str):
            for p in path:
                self.add_asset(category, p)
        else:
            # TODO: Do this stuff in run! Store patterns only here!
            matches = glob.glob(path, recursive=True)
            counter = 0
            for f in matches:
                if os.path.exists(f) and not os.path.isdir(f):
                    counter += 1
                    abs_f = os.path.abspath(f)

                    # Check if asset is already used
                    for asset in self.assets[category]:
                        if asset.source == abs_f:
                            # asset is already used - aborting
                            return
                    print("Adding asset: %s" % f)
                    self.assets[category].add(Asset(abs_f, f))
            if counter == 0:
                print('WARNING: No resouces found for %s' % path)

    def requires_asset(self, category, path):
        def decorator(f):
            self.add_asset(category, path)
            return f
        return decorator

    def route(self, path):
        def decorator(f):
            self.routes[path] = f
            return f
        return decorator

    def _render_page(self, route, page, source):
        context = {
            'project_root': self.project_root,
            'assets': self.assets,
            'options': self.options,
            'source': source
        }
        if type(page) is dict:
            page = render_page(page)
        return page.render(cleanup(route), context)

    def run(self, serve=False):
        if os.path.exists(self.destination_dir):
            for item in os.listdir(self.destination_dir):
                item = os.path.join(self.destination_dir, item)
                if os.path.isfile(item):
                    os.remove(item)
                else:
                    shutil.rmtree(item)
        else:
            os.makedirs(self.destination_dir)
        created = {}
        with pushd(self.destination_dir):
            for route, fn in self.routes.items():
                parameter_names = fn.__code__.co_varnames[:fn.__code__.co_argcount]
                params = [self.options[key] for key in parameter_names]
                if inspect.isgeneratorfunction(fn):
                    for page in fn(*params):
                        if not is_variable(route):
                            raise URLParseException('When using generator functions, variable'
                                                    'urls must be used!')
                        url = process_variable_url(route, page.variables, page.custom_url)
                        k, v = self._render_page(url, page, fn.__code__.co_name)
                        # TODO: Check for duplicates!
                        created[k] = v
                else:
                    k, v = self._render_page(route, fn(*params), fn.__code__.co_name)
                    # TODO: Check for duplicates!
                    # especially /foo/baa/ vs /foo/baa/index.html
                    created[k] = v
            for category, assets in self.assets.items():
                # TODO: add hooks for asset handling!
                for asset in assets:
                    # Create destination directory
                    dir_name = os.path.dirname(asset.destination)

                    if len(dir_name) > 0 and not os.path.exists(dir_name):
                        os.makedirs(dir_name)

                    # Copy source into the destination
                    shutil.copyfile(asset.source, asset.destination)
        if serve:
            utils.serve('0.0.0.0', 8000, self.destination_dir, self.run)


def render_page(template_context, **url_variables):
    return JinjaPage(template_context, url_variables)


def raw_page(raw, **url_variables):
    return RawPage(raw, url_variables)
