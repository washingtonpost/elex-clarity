elex-clarity
============

.. image:: https://img.shields.io/pypi/v/elex-clarity.svg
    :target: https://pypi.org/project/elex-clarity/

.. image:: https://img.shields.io/pypi/pyversions/elex-clarity.svg
    :target: https://pypi.org/project/elex-clarity/

.. image:: https://circleci.com/gh/washingtonpost/elex-clarity.svg?style=shield
    :target: https://circleci.com/gh/washingtonpost/elex-clarity

.. image:: https://img.shields.io/pypi/l/elex-clarity.svg
    :target: https://pypi.python.org/pypi/elex-clarity/

A CLI tool for pulling in election results from sites using Clarity (the "election night reporting" product described `here <https://www.scytl.com/en/election-night-reporting/>`_). This package is hosted on pypi.

Please use the `Github issue tracker <https://github.com/washingtonpost/elex-clarity/issues>`_ to submit bugs or request features.

.. contents:: **Table of Contents**
    :depth: 1


Overview
------------

This library

* Provides a simple CLI tool for pulling in and formatting election results from a Clarity-backed website or local file
* Separates data retrieval from data formatting
* By default, returns results formatted like so

    .. code-block:: python

        {
            "2020-11-03_GA_G_P": {
                "id": "2020-11-03_GA_G_P",
                "source": "clarity",
                "precinctsReportingPct": 100.0,
                "counts": {
                    "donald_j_trump_i_rep": 2461837,
                    "joseph_r_biden_dem": 2474507,
                    "jo_jorgensen_lib": 62138
                },
                "office": "P",
                "lastUpdated": "2020-11-20T20:37:06Z",
                "subunits": {
                    "appling": {
                        "id": "appling",
                        "counts": {
                            "donald_j_trump_i_rep": 6526,
                            "joseph_r_biden_dem": 1779,
                            "jo_jorgensen_lib": 36
                        }
                    },
                    ...
                }
            }
        }


Installation
------------

* Make sure you have python 3.7+ installed
* Optional: we recommend that you set up a `virtualenv <http://virtualenvwrapper.readthedocs.io/en/latest/>`_ and activate it
* ``pip install elex-clarity``


Usage
---------

All CLI commands require a Clarity election ID and state postal code. For example

``elexclarity 105369 GA``

The election ID can be found by navigating to the election in question in whichever results site you're viewing. For example, for Georgia, the Secretary of State's website links to `election results <https://sos.ga.gov/page/georgia-election-results>`_. Following the `Current Election Results` link you get to a clarity page with many election results pages. Looking at the 2020-current results will lead to ``https://results.enr.clarityelections.com/GA/105369/web.264614/#/summary``, which contains the election ID right after the state postal code.

Other parameters
~~~~~~~~~~~~~~~~

.. list-table:: Title
   :header-rows: 1

   * - Name
     - Description
     - Type
     - Required?
     - Default
   * - style
     - what broad type of formatting should be done?
     - one of [default, raw]
     - N
     - default
   * - outputType
     - what specific type of formatting should be done?
     - one of [results, settings, summary]
     - N 
     - results
   * - level
     - what level of data should be fetched/returned?
     - one of [precinct, county, state]
     - N
     - county
   * - countyName
     - Name of county to get results from if counties have their own pages
     - string
     - N
     - --
   * - officeID
     - what office ID(s) should be returned?
     - a comma separated list of office IDs
     - N
     - --
   * - countyMapping
     - an object with race names (as provided via Clarity) mapped to some other identifier that should be used in results formatting. Sample formats can be found in the ``tests/fixtures`` `folder <https://github.com/washingtonpost/elex-clarity/tree/develop/tests/fixtures/mappings>`_
     - object
     - N
     - -- 
   * - voteCompletionMode
     - the method that should be used to determine whether a precinct is fully reporting 
     - string
     - N
     - percentReporting
   * - filename
     - the path to read results from (if you don't want to ping a Clarity site)
     - string
     - N
     - -- 


Example invocations
~~~~~~~~~~~~~~~~~~~

Retrieving raw data:

* ``elexclarity 105369 GA --outputType=summary --style=raw``
* ``elexclarity 105369 GA --outputType=settings --style=raw``
* ``elexclarity 105369 GA --level=precinct --style=raw``
* ``elexclarity 106043 CA --countyName Santa_Clara --level=precinct``

Retrieving + formatting settings (for presidential races):

* ``elexclarity 105369 GA --outputType=settings --officeID=P``

Retrieving + formatting results:

* ``elexclarity 105369 GA --level=precinct --countyMapping='{"Worth": "13321"}'``
* ``elexclarity 105369 GA --level=precinct``
* ``elexclarity 105369 GA --level=precinct --voteCompletionMode=voteTypes``
* ``elexclarity 105369 GA --level=county``
* ``elexclarity 106210 WV --level=county --countyMapping='<mapping json>'``
* ``elexclarity 105369 WV --level=state``

Formatting data from a local file:

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
