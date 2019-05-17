from setuptools import setup, find_packages

def get_version():
    import os
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION.txt")
    with open(p) as f:
        return f.read().strip()

requires = [
    'tldextract==2.0.1',
    'boto3==1.4.1',
    'WebSmsComToolkit==1.0.2',
    'BeautifulSoup4==4.6.0',
    'Pillow==5.4.1',
    'croniter==0.3.4',
    'pytz==2019.1',
    'gevent==1.0.2',
    'jinja2==2.8',
    'pyramid==1.7.0',
    'pyramid-jinja2==2.5',
    'pyramid-swagger==2.3.1rc1',
    'bravado-core==4.2.3rc7',
    'enum34==1.0.4',
    'six==1.11.0',
    'pyyaml==3.11',
    'jsonschema==2.5.1',
    'jsonpickle==0.9.3',
    'requests==2.7.0',
    'transitions==0.4.1',
    'python-dateutil==2.4.2',
    'short_url==1.2.2',
    'elasticsearch==1.9.0',
    'crate==0.16.1',
    'crash==0.17.1',
    'lovely.pyrest==2.1.1',
    'lovely.esdb==0.3.8',
    'lovely.essequence==0.1.0',
    'swagger-spec-validator==2.0.2',
    'functools32==3.2.3.post2',
    'simplejson==3.8.2',
    'rfc3987==1.3.1',
    'webcolors==1.5',
    'strict-rfc3339==0.7',
    'phonenumbers==8.0.0',
    'python-magic==0.4.15',
    'mandrill==1.0.57',
    'python-twitter==3.4.1',
    'exifread==2.1.2',
]

setup(
    name='iris.service',
    version=get_version(),
    author='Lovely Systems',
    author_email='hello@lovelysystems.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['iris'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
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
            'cleanup_s3=iris.scripts.cleanup_s3:main',
        ],
    },
)
