import os
import argparse
import tempfile

from jinja2 import Template


def load(f):
    l = {}
    g = {}
    exec(f, g, l)
    if '__all__' in l:
        # only attributes listed in __all__ are allowed
        allowed = set(l['__all__'])
        for k in list(l.keys()):
            if k not in allowed:
                del l[k]
    else:
        # remove all keys starting with _
        for k in list(l.keys()):
            if k.startswith('_'):
                del l[k]
    return l


def get_jinja_tmpl_params(args):
    tmpl_args = {}
    if args.settings:
        # parse the file as python module
        with file(args.settings, 'rb') as f:
            tmpl_args = load(f)
    return tmpl_args


def execute_sql_files(args):
    """Create all tables based on sql files

    Searches all *.sql files in the input dir and executes them.

    Files are first executed as jinja templates. The output is then used as
    sql.
    """
    tmpl_args = get_jinja_tmpl_params(args)
    for filename in args.files:
        print 'Executing file "%s" for "%s"' % (filename, args.host)
        with file(filename, 'rb') as f:
            template = Template(unicode(f.read(), 'utf-8'))
            sql = template.render(**tmpl_args)
            temp, name = tempfile.mkstemp()
            with file(name, 'wb') as o:
                o.write(sql.encode('utf-8'))
            os.system("cat %s | %s --host %s" % (name, args.crash, args.host))


def main(args=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
          Create database tables.
          The input is an sql file which will be executed using 'crash'.
          Before the sql file is executed it is processed as a jinja template
          with settings from a python file.
        """
    )
    parser.add_argument(
        '--host',
        help="The crate host",
    )
    parser.add_argument(
        '--crash',
        default='bin/crash',
        help="The crash client",
    )
    parser.add_argument(
        '--settings',
        default=None,
        help="The settings file for the jinja renderer",
    )
    parser.add_argument(
        'files',
        nargs='*',
        help="The sql files to execute",
    )
    args = parser.parse_args(args)
    execute_sql_files(args)
