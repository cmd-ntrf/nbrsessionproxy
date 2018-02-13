import os
import getpass
import json

from urllib.parse import urlunparse, urlparse
from distutils.spawn import find_executable

from tornado import web

from notebook.utils import url_path_join as ujoin
from notebook.base.handlers import IPythonHandler

from nbserverproxy.handlers import SuperviseAndProxyHandler


class AddSlashHandler(IPythonHandler):
    """Handler for adding trailing slash to URLs that need them"""
    @web.authenticated
    def get(self, *args):
        src = urlparse(self.request.uri)
        dest = src._replace(path=src.path + '/')
        self.redirect(urlunparse(dest))

class RServerAvail(IPythonHandler):
    """Handler to verify if rserver binary is available."""
    @web.authenticated
    def get(self, *args):
        self.write(json.dumps(find_executable(RServerProxyHandler.name) is not None))

class RServerProxyHandler(SuperviseAndProxyHandler):
    '''Manage an RStudio rserver instance.'''

    name = 'rserver'

    def get_env(self):
        env = {}

        # rserver needs USER to be set to something sensible,
        # otherwise it'll throw up an authentication page
        if not os.environ.get('USER', ''):
            env['USER'] = getpass.getuser()

        return env

    def get_cmd(self):
        # rserver command. Augmented with www-port.
        return [
            self.name,
            '--www-port=' + str(self.port)
        ]

def setup_handlers(web_app):
    web_app.add_handlers('.*', [
        (ujoin(web_app.settings['base_url'], 'rstudio/(.*)'), RServerProxyHandler, dict(state={})),
        (ujoin(web_app.settings['base_url'], 'rstudio'), AddSlashHandler),
        (ujoin(web_app.settings['base_url'], 'rstudio-avail'), RServerAvail),
    ])
