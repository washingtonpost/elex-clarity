elex-clarity
============

A CLI tool for pulling in election results from sites using Clarity.


Usage
-----

Examples:
^^^^^^^^^

Pulling raw data:

* ``elexclarity 105369 GA --outputType=summary --style=raw``
* ``elexclarity 105369 GA --outputType=settings --style=raw``
* ``elexclarity 105369 GA --level=precinct --style=raw``

Getting formatted settings:

* ``elexclarity 105369 GA --outputType=settings --officeID=P``

Pulling formatted results:

Note: these require that you pass in county mapping as a JSON object. Sample formats can be found in the ``tests/fixtures`` folder `here <https://github.com/washingtonpost/elex-clarity/tree/develop/tests/fixtures/mappings>`_.

* ``elexclarity 105369 GA --level=precinct --countyMapping='{"Worth": "13321"}'``
* ``elexclarity 105369 GA --level=precinct``
* ``elexclarity 105369 GA --level=county``
* ``elexclarity 106210 WV --level=county --countyMapping='<mapping json>'``
* ``elexclarity 105369 WV --level=state``

Using a local file:

* ``elexclarity 105369 GA --level=precinct --filename="tests/fixtures/results/ga_atkinson_precincts_11-3.xml" --countyMapping='<mapping json>'``
* ``elexclarity 105369 GA --level=county --filename="tests/fixtures/ga_counties_11-3.xml" --countyMapping='<mapping json>'``

Installation
~~~~~~~~~~~~

* Ideally, set up a virtualenv and activate it (http://virtualenvwrapper.readthedocs.io/en/latest/)
* ``pip install -e . [dev]``
