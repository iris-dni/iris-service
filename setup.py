import os
import re
import ConfigParser

from setuptools import setup, find_packages


VERSION = "?"
execfile(os.path.join(os.path.dirname(__file__),
                      'iris/service/__init__.py'))


def get_versions():
    """picks the versions from version.cfg and returns them as dict"""
    versions_cfg = os.path.join(os.path.dirname(__file__), 'versions.cfg')
    config = ConfigParser.ConfigParser()
    config.optionxform = str
    config.readfp(open(versions_cfg))
    return dict(config.items('versions'))


def nailed_requires(requirements, pat=re.compile(r'^(.+)(\[.+\])?$')):
    """returns the requirements list with nailed versions"""
    versions = get_versions()
    res = []
    for req in requirements:
        if '[' in req:
            name = req.split('[', 1)[0]
        else:
            name = req
        if name in versions:
            res.append('%s==%s' % (req, versions[name]))
        else:
            res.append(req)
    return res

requires = [
    'tldextract',
    'boto3',
    'WebSmsComToolkit',
    'BeautifulSoup4',
    'Pillow',
    'croniter',
    'pytz',
    'gevent',
    'jinja2',
    'pyramid',
    'pyramid-jinja2',
    'pyramid-swagger',
    'bravado-core',
    'enum34',
    'six',
    'pyyaml',
    'jsonschema',
    'jsonpickle',
    'requests',
    'transitions',
    'python-dateutil',
    'short_url',
    'elasticsearch',
    'crate',
    'crash',
    'lovely.pyrest',
    'lovely.esdb',
    'lovely.essequence',
    'bravado-core',
    'pyramid-swagger',
    'swagger-spec-validator',
    'functools32',
    'jsonschema',
    'simplejson',
    'rfc3987',
    'webcolors',
    'strict-rfc3339',
    'python-magic',
    'mandrill',
    'exifread',
]

setup(
    name='iris.service',
    version=VERSION,
    author='Lovely Systems',
    author_email='hello@lovelysystems.com',
    packages=find_packages(),
    include_package_data=True,
    extras_require=dict(
        test=nailed_requires([
            'httmock',
            'collective.xmltestreport',
            'webtest',
            'fake-factory',
            'lovely.testlayers',
        ]),
        stategraph=nailed_requires([
            'pygraphviz',
        ]),
        documentation=nailed_requires([
            'sphinx',
            'sphinx-rtd-theme',
        ]),
    ),
    zip_safe=False,
    install_requires=nailed_requires(requires),
    test_suite="iris.service",
    entry_points={
        'paste.app_factory': [
            'main=iris.service.server:app_factory',
        ],
        'paste.server_factory': [
            'server=iris.service.server:server_factory',
        ],
        'console_scripts': [
            'iris-service=pyramid.scripts.pserve:main',
            'dump=iris.service.scripts.dump:dump',
            'setup_db=iris.service.scripts.setup_db:main',
        ],
    },
)
