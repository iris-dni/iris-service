=============
IRIS Database
=============

The IRIS code uses elasticsearch to access data.

IRIS is using `crate <https://crate.io>`_ as its primary storage. `crate`
provides an SQL layer on top of elasticsearch.

Using crate allows us to use SQL for ad hock queries while the code is using
plain elasticsearch.


Table Creation
==============

Tables are created using SQL. The table definition files are defined in the
`etc/sql` folder.


Documents
=========

In the code documents are implemented using the package `lovely.esdb
<https://github.com/lovelysystems/lovely.esdb>`_ which
provides the class `Document` which is a base class for the documents stored
in tables.
