Usage
=====

Filing Searches
---------------

To use `CB_IPO` instantiate an instance by calling 
::

    instance = scrape()


To adjust search date ranges run (Dates in YYYY-MM-DD)
::

    instance.set_search_date(START, END)


To add form types to the search run
::

    instance.add_forms(['S-1','10-K'])


To get a dataframe with all companies filing within the specified paramateres and filing dates run

::

    instance.generate_df(Number of entries per page, number of pages)


10-K Document Research
----------------------
To get a list of links to 10-K filings by a company given CIK
::

    instance.create_links(cik, number of files needed)


To scrape a 10-K link for assets, liabilities, and Net Income run
::
    
    instance.scrape_xbrl(link)
