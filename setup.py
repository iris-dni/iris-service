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
    'pytz',
    'gevent',
    'pyramid',
    'pyramid-jinja2',
    'pyramid-swagger',
    'bravado-core',
    'enum34',
    'jsonschema',
    'rfc3987',
    'requests',
    'python-dateutil',
    'crate',
    'crash',
    'lovely.pyrest',
    'lovely.esdb',
    'lovely.essequence',
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
            'collective.xmltestreport',
            'webtest',
            'fake-factory',
            'lovely.testlayers',
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
        ],
    },
)
