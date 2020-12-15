elex-clarity
============

A CLI tool for pulling in election results from sites using Clarity.


Usage
-----

Examples:
^^^^^^^^^

Pulling raw data from Clarity (still needs formatting work):

* ``elexclarity 105369 GA --outputType=summary``
* ``elexclarity 105369 GA --outputType=settings``

Pulling formatted data from Clarity:

* ``elexclarity 105369 GA --level=precinct``
* ``elexclarity 105369 GA --level=county``
* ``elexclarity 106210 WV --level=county``
* ``elexclarity 105369 GA --level=county --countymapping="tests/fixtures/alternate_GA_county_mapping.json"``

Using a local file:

* ``elexclarity 105369 GA --level=precinct --filename="tests/fixtures/atkinson_precincts_11-3.xml"``
* ``elexclarity 105369 GA --level=county --filename="tests/fixtures/2020-11-03_GA.xml"``

State-level formatting has not been implemented yet.

Installation
~~~~~~~~~~~~

* Ideally, set up a virtualenv and activate it (http://virtualenvwrapper.readthedocs.io/en/latest/)
* ``pip install -e . [dev]``
