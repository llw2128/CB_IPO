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


To scrape a 10-K link for assets, liabilities, and net income and format into dictionary run
::
    
    instance.scrape_xbrl(link)

To quickly calculate the financial ratios for a dictionary of elements run
::
    
    instance.calculate_ratios(balance_sheet_dict)

To generate a dataframe summarizing the info in a 10-K run
::
    
    instance.summarize_10k(link, flag)
    
``flag`` can be a string that is set to: 
``'raw'``, ``'ratios'``, ``'debt'``, ``'liquidity'``, 
``'current'``, ``'total'``, ``'leverage'``, or ``'profitability'``
