Amazon Description Scraper
==========================

.. image:: https://img.shields.io/pypi/v/amazon-description-scraper.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/amazon-description-scraper/

.. image:: https://github.com/ryzanbui02/amazon-description-scraper/actions/workflows/test-and-deploy.yaml/badge.svg
    :target: https://github.com/ryzanbui02/amazon-description-scraper/actions/workflows/test-and-deploy.yaml

.. image:: https://codecov.io/gh/ryzanbui02/amazon-description-scraper/branch/main/graph/badge.svg
  :target: https://codecov.io/gh/ryzanbui02/amazon-description-scraper

Webscrape project to get Amazon products' descriptions.


Requirements
------------

This library is compatible with Python >= 3.9 and requires:

- ``bs4``
- ``fake-useragent``
- ``pandas``
- ``requests``
- ``selenium``


Installation
------------
Module can be installed from `PyPI <https://pypi.org/project/amazon-description-scraper>`_ with:

.. code::

  pip install amazon-description-scraper


Brief Example
-------------

.. code:: python

  from amzsc import AmazonScraper
  
  proxy_key = "XXXXXXXXXXX" # enter real proxy key here
  client = AmazonScraper(proxy_key=proxy_key, jsonl_output_path="data/output.jsonl")
  asins = ["B07WC4TDJJ"]
  results = client.scrape(asins=asins, marketplace="US")
  print(results)


Contributing
------------
Contribute to this repository by forking this repository and installing in
development mode with::

  git clone https://github.com/<USERNAME>/amazon-description-scraper
  pip install -e .[test]

You can then add your feature or commit your bug fix and then run your unit
testing with::

  pytest

Unit testing will automatically enforce minimum code coverage standards.

Next, to ensure your code meets minimum code styling standards, run::

  pre-commit run --all-files

Finally, `create a pull request <https://github.com/ryzanbui02/amazon-description-scraper/pulls>`_ from your fork and I'll be sure to review it.
