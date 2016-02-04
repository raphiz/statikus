import os
from jinja2 import Environment, FileSystemLoader
import shutil
import inspect
from collections import defaultdict
from .utils import pushd
from .exceptions import URLParseException
from .url import is_variable, process_variable_url, cleanup

__title__ = 'statikus'
__version__ = '0.1.0-dev'
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
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        return path[1:]


class JinjaPage(Page):
    env = Environment(loader=FileSystemLoader(os.path.abspath('templates/')))

    def render(self, route, context):
        jinja_context = self.data
        jinja_context['assets'] = context['assets']
        jinja_context['options'] = context['options']

        template = self.env.get_template(context['source'] + '.html')
        with open(self.touch(route), 'w') as f:
            f.write(template.render(**jinja_context))
        return route, self


class RawPage(Page):

    def render(self, route, context):
        with open(self.touch(route), 'w') as f:
            f.write(self.data)
        return route, self


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

    def _render_page(self, route, page, source):
        context = {
            'assets': self.assets,
            'options': self.options,
            'source': source
        }
        if type(page) is dict:
            page = render_page(page)
        return page.render(cleanup(route), context)

    def run(self):

        # TODO: support generators (when using variables/wildcards in URLs)
        # if it contains <name>, the method must provide it as dict / tuple
        # if it contains *, the method must provide the full path!

        if os.path.exists(self.destination_dir):
            # This is pretty ugly....
            shutil.rmtree(self.destination_dir)

        os.makedirs(self.destination_dir)

        created = {}
        with pushd(self.destination_dir):
            # self.assets_processor(self.assets_dir, self.assets)
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
                        # Check for duplicates!
                        created[k] = v
                else:
                    k, v = self._render_page(route, fn(*params), fn.__code__.co_name)
                    # Check for duplicates!
                    # especially /foo/baa/ vs /foo/baa/index.html
                    created[k] = v


def render_page(template_context, **url_variables):
    return JinjaPage(template_context, url_variables)


def raw_page(raw, **url_variables):
    return RawPage(raw, url_variables)
