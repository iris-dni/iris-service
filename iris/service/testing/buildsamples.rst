==============
Sample Builder
==============

Build samples::

    >>> samples.users(100)
    >>> samples.cities(50)
    >>> samples.petitions(50)

Dump the samples::

    >>> from iris.service.scripts import dump
    >>> from iris.service.testing import layer
    >>> import os.path
    >>> with open(os.path.join(layer.buildout_dir, 'samples', 'sample.bulk'), 'w') as f:
    ...     dump.dump(['dump', layer.crate_host], f)
