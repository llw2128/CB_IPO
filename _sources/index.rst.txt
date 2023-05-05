.. CB_IPO documentation master file, created by
   sphinx-quickstart on Tue Apr  4 15:22:10 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to CB_IPO's documentation!
==================================

This is a library designed for quick webscraping in finding information on SEC filings with a focus on new IPOs and annual reports.


..  image:: https://github.com/llw2128/CB_IPO/workflows/Build%20Status/badge.svg?branch=main
   :target: https://github.com/llw2128/CB_IPO/actions?query=workflow%3A%22Build+Status%22

..  image:: https://codecov.io/gh/llw2128/CB_IPO/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/llw2128/CB_IPO

..  image:: https://img.shields.io/badge/License-Apache_2.0-green.svg
   :target: https://opensource.org/licenses/Apache-2.0

..  image:: https://img.shields.io/github/issues/llw2128/CB_IPO
   :target: https://img.shields.io/github/issues/llw2128/CB_IPO

..  image:: https://img.shields.io/pypi/v/CB_IPO
   :target: https://pypi.org/project/CB-IPO/

.. toctree::
   :maxdepth: 1
   :caption: Quick Start:

   installation
   usage
   methods
   examples

Overview
--------
Researching information on trends for companies can be incredibly tedious, this library will automate part of the proccess making DCF building and IPO research easier. 
CB_IPO is a library that will fetch information on recent and historical IPOs by scraping the SEC EDGAR database for S-1 filings.
With these links, the library also has a function for using a 10-k link and returning a dictionary or dataframe of info such as assets, liabilities, and income.

Example
-------
Suppose I want to find companies that have filed either an S-1, 10-K or 10-Q between January 2021 and March 2023
::

   sc = scrape()
   sc.set_search_date("2021-01-01", "2023-03-31")
   sc.add_forms(['S-1','10-K', '10-Q'])
   dataframe = sc.generate_df(10, 1)

Then this pandas.DataFrame is returned
::

                                                   names filing date
   0               Inhibikase Therapeutics, Inc.  (IKT)   2023-03-31
   1                       AMERINST INSURANCE GROUP LTD   2023-03-31
   2                      SLM Student Loan Trust 2013-5   2023-03-31
   3   Games & Esports Experience Acquisition Corp.  ...  2023-03-31
   4   Bilander Acquisition Corp.  (TWCB, TWCBU, TWCBW)   2023-03-31
   5                                VirTra, Inc  (VTSI)   2023-03-31
   6             Actinium Pharmaceuticals, Inc.  (ATNM)   2023-03-31
   7                              Genprex, Inc.  (GNPX)   2023-03-31
   8                           Mega Matrix Corp.  (MPU)   2023-03-31
   9       Digital Media Solutions, Inc.  (DMS, DMS-WT)   2023-03-31

Details
-------
This project is a pure python project using modern tooling. It uses a ``Makefile`` as a command registry, with the following commands:

* ``make``: list available commands.
* ``make develop``: install and build this library and its dependencies using ``pip``.
* ``make build``: build the library using ``setuptools``
* ``make lint``: perform static analysis of this library with ``flake8`` and ``black``
* ``make format``: autoformat this library using ``black``
* ``make annotate``: run type checking using ``mypy``
* ``make test``: run automated tests with ``pytest``
* ``make coverage``: run automated tests with ``pytest`` and collect coverage information
* ``make dist``: package library for distribution
