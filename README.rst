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
That is the goal of “Project Iris”, with source code be released to the
public domain.


Development
===========

Setup the project
-----------------

Libmagic needs to be installed.

Install using Macports::

    $ port install libmagic

Or install using brew::

    $ brew install libmagic

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

To start a fully working local environment a supervisor is available::

    $ bin/supervisord

This starts a crate instance on port 8042 and the iris app on port 8080.

To setup the crate database run::

    $ bin/setup_db --setting etc/sql/sql.py --host localhost:8042 etc/sql/sql.sql

Documentation is now available::

    $ open http://localhost:8080/docs

Swagger client UI::

    $ open http://localhost:8080/swaggerui

Explore with: http://localhost:8080/api.json


Sample Data
-----------

Sample data can be loaded into the database from the samples directory::

    $ curl -s -XPOST localhost:8042/_bulk?pretty= --data-binary "@samples/sample.bulk"; echo
