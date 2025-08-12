from urllib.parse import urljoin

import webtest

from pyramid.config import Configurator
from cubicweb.devtools import BASE_URL
from cubicweb.devtools.testlib import CubicWebTC


ACCEPTED_ORIGINS = ["example.com"]


class CustomTestApp(webtest.TestApp):
    def _gen_request(self, verb, url, *args, **kwargs):
        if not url.startswith(BASE_URL) and not url.startswith(("http://", "https://")):
            url = urljoin(BASE_URL, url)

        return super()._gen_request(verb, url, *args, **kwargs)

    def get(self, url, *args, **kwargs):
        if not url.startswith(BASE_URL) and not url.startswith(("http://", "https://")):
            url = urljoin(BASE_URL, url)

        return super().get(url, *args, **kwargs)


class _BasePyramidCWTest(CubicWebTC):
    settings = {}

    @classmethod
    def init_config(cls, config):
        super().init_config(config)
        config.global_set_option("anonymous-user", "anon")

    def _generate_pyramid_config(self):
        settings = {
            "cubicweb.session.secret": "test",
        }
        settings.update(self.settings)
        pyramid_config = Configurator(settings=settings)

        pyramid_config.registry["cubicweb.repository"] = self.repo
        pyramid_config.registry.settings["pyramid.debug_routematch"] = True
        pyramid_config.include("cubicweb.pyramid")

        self.includeme(pyramid_config)
        self.pyr_registry = pyramid_config.registry

        return pyramid_config

    def login(self, user=None, password=None, **args):
        return self.webapp.login(user, password, additional_arguments=args)

    def logout(self):
        return self.webapp.logout()


class PyramidCWTest(_BasePyramidCWTest):
    def includeme(self, config):
        pass

    def build_webapp(self):
        self.webapp = CustomTestApp(
            self.pyramid_config.make_wsgi_app(),
            extra_environ={"wsgi.url_scheme": "https"},
        )

    def setUp(self):
        # Skip CubicWebTestTC setUp
        super().setUp()
        settings = {
            "cubicweb.session.secret": "test",
        }
        settings.update(self.settings)
        self.pyramid_config = Configurator(settings=settings)

        self.pyramid_config.registry["cubicweb.repository"] = self.repo
        self.pyramid_config.include("cubicweb.pyramid")

        self.includeme(self.pyramid_config)
        self.pyr_registry = self.pyramid_config.registry
        self.build_webapp()
