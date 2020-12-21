elex-clarity
============

A CLI tool for pulling in election results from sites using Clarity. This package is hosted on pypi.

Please use the `Github issue tracker <https://github.com/washingtonpost/elex-clarity/issues>`_ to submit bugs or request features.

.. contents:: **Table of Contents**
    :depth: 1

Installation
------------

* Ideally, set up a `virtualenv <http://virtualenvwrapper.readthedocs.io/en/latest/>`_ and activate it
* ``pip install elex-clarity``


Usage
---------

Pass in a Clarity election ID and state postal code (and optionally, other parameters) to the cli, e.g.:

``elexclarity 105369 GA``

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

Development
------------

* Clone this repository
* ``pip install -r requirements.txt``
* ``tox``
* You should see some code coverage info and test results
* If the above was successful, you are ready for development

Releasing a New Version
------------------------

In preparation for a new release:

* Decide what the next version will be per semantic versioning
* Make a new branch named ``release/<version number>``
* Update the changelog with all changes that will be included in the release
* Commit your changes and make a PR against ``main``
* Once the changes are merged, tag ``main`` (or ``develop`` for a beta release) with the release's version number and push that tag (``git push --tags``)
* Merge ``main`` into ``develop``
