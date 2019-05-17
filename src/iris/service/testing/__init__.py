import os

here = os.path.abspath(os.path.dirname(__file__))

project_root = os.path.dirname(os.path.dirname(
    os.path.dirname(
        os.path.dirname(here)
    )))


def testing_path(*parts):
    return os.path.join(here, *parts)


def project_path(*parts):
    return os.path.join(project_root, *parts)
