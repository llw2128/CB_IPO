# CB_IPO
This is a library designed for quick webscraping in finding information on SEC filings with a focus on new IPOs and annual reports.

[![Build Status](https://github.com/llw2128/CB_IPO/workflows/Build%20Status/badge.svg?branch=main)](https://github.com/llw2128/CB_IPO/actions?query=workflow%3A%22Build+Status%22)
[![codecov](https://codecov.io/gh/llw2128/CB_IPO/branch/main/graph/badge.svg)](https://codecov.io/gh/llw2128/CB_IPO)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](https://opensource.org/licenses/Apache-2.0)  ![](https://img.shields.io/github/issues/llw2128/CB_IPO)

## Overview
Researching information on trends for companies can be incredibly tedious, this library will automate part of the proccess making DCF building and IPO research easier. CB_IPO is a library that will fetch information on recent and historical IPOs by scraping the SEC EDGAR database for S-1 filings. These queries can also be modified to search for certain dates, and additional forms. This data can subsequently be placed in a pandas dataframe for the sake of easy viewing. A second proccess this autmoates is finding the specific 10-K filings for a company. By inputing a cik, a list of 10-k filing links will be returned. With these links, the library also has a function for using a 10-k link and returning a list of info such as assets, liabilities, and income.

## Installation
`CB_IPO` can be installed via PyPi by running:
```
pip install CB_IPO
```

## Quick Start
To use `CB_IPO` instantiate an instance by calling 
```
instance = scrape()
``` 

To adjust search date ranges run (Dates in YYYY-MM-DD)
```
instance.set_search_date(START, END)
```

To add form types to the search run
```
instance.add_forms(['S-1','10-K'])
```

To get a dataframe with all companies filing within the specified paramateres and filing dates run

```
instance.generate_df(Number of entries per page, number of pages)
```

To get a list of links to 10-K filings by a company given CIK
```
instance.create_links(cik, number of files needed)
```

To scrape a 10-K link for assets, liabilities, and Net Income run
```
instance.scrape_xbrl(link)
```
## Details
This project is a pure python project using modern tooling. It uses a `Makefile` as a command registry, with the following commands:
- `make`: list available commands
- `make develop`: install and build this library and its dependencies using `pip`
- `make build`: build the library using `setuptools`
- `make lint`: perform static analysis of this library with `flake8` and `black`
- `make format`: autoformat this library using `black`
- `make annotate`: run type checking using `mypy`
- `make test`: run automated tests with `pytest`
- `make coverage`: run automated tests with `pytest` and collect coverage information
- `make dist`: package library for distribution
