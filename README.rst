elex-clarity
============

A CLI tool for pulling in election results from sites using Clarity.


Usage
-----

Examples:
^^^^^^^^^

Pulling data from Clarity:

* ``elexclarity 105369 GA --outputType=summary``
* ``eelexclarity 105369 GA --outputType=settings``
* ``elexclarity 105369 GA --level=precinct``
* ``elexclarity 105369 GA --level=county``

Using a local file:

* ``elexclarity 105369 GA --level=precinct --filename="tests/fixtures/atkinson_precincts_11-3.xml"``
* ``elexclarity 105369 GA --level=county --filename="tests/fixtures/2020-11-03_GA.xml"``

State-level formatting has not been implemented yet.

Installation
~~~~~~~~~~~~

* Ideally, set up a virtualenv and activate it (http://virtualenvwrapper.readthedocs.io/en/latest/)
* ``pip install -e . [dev]``
