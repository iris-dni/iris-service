import argparse

from crate import client
from crate.client.exceptions import ProgrammingError
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
        with open(args.settings, 'rb') as f:
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
        with open(filename, 'rb') as f:
            template = Template(unicode(f.read(), 'utf-8'))
            sql = template.render(**tmpl_args)
            with client.connect(args.host) as conn:
                c = conn.cursor()
                for stmt in _parse_statements(sql.split('\n')):
                    try:
                        c.execute(stmt)
                    except ProgrammingError as e:
                        raise RuntimeError("Failed to execute statement: %s error=%s" % (stmt, e))
                c.close()


def _parse_statements(lines):
    """Return a generator of statements.

    Args: A list of strings that can contain one or more statements.
          Statements are separated using ';' at the end of a line
          Everything after the last ';' will be treated as the last statement.
    """
    lines = (l.strip() for l in lines if l)
    lines = (l for l in lines if not l.startswith('--'))
    parts = []
    for line in lines:
        parts.append(line.rstrip(';'))
        if line.endswith(';'):
            yield ' '.join(parts)
            parts[:] = []
    if parts:
        yield ' '.join(parts)


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
