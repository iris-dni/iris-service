====
IRIS
====

What Is IRIS
============

There are many topics that local communities regard as particularly pressing,
but journalists usually only discover them by accident. This problem inspired
our idea to create a platform where citizens’ concerns can be collected and
rated on a municipal level. That way a newspaper can create space for those
topics, host a discussion and bring additional value to the local community.
That is the goal of “Project Iris”, which source code be released to the
public domain.


Development
===========

Setup the project
-----------------

We are using buildout::

    $ python-27 bootstrap.py
    $ bin/buildout -N


Run tests
---------

To run the tests of the project execute::

    $ bin/test

To test for any PEP8 issues run::

    $ bin/flake8


Start the app locally
---------------------

To start the app in foreground just run the command::

    $ bin/app

The api of the app is now available on the port defined in buildout.cfg (8080
by default)::

    $ open localhost:8080/v1/sample
