import pandas as pd
import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver


class scrape:
    """
    This class creates an object that can scrape for various filings and and attributes of SEC filings

    Attributes:
        url_info: The url to be used for scraping the site
    """

    def __init__(self):
        """
        Instantiates a scraper object, with a default search space of recent S-1 filings

        """
        self.url_info = "https://www.sec.gov/edgar/search/#/filter_forms=S-1"

    def set_page(self, page_number):
        """
        Modifies the page number being opened from the search results, and modifies url_info as such

        Args:
            page_number (int): The page number in search results to be opened

        Returns:
            str: A string of the modified url
        """
        pstr = '&page={}'.format(page_number)

        i = self.url_info.find('&page=')
        if i < 0:
            self.url_info += pstr
        else:
            self.url_info = self.url_info[:i] + pstr
        return self.url_info

    def reset_url(self):
        """
        Resets the url to only search for the most recent S-1 forms, and modifies url_info as such

        Returns:
            str: A string of the original url
        """
        self.url_info = "https://www.sec.gov/edgar/search/#/filter_forms=S-1"
        return self.url_info

    def set_search_date(self, start_date, end_date):
        """
        Modified the search to look between two specific dates, and modifies url_info as such

        Args:
            start_date (str): Start of the date range YYYY-MM-DD format
            end_date (str): End of the date range YYYY-MM-DD format

        Returns:
            str: A string of the modified url
        """
        dates = 'dateRange=custom&category=custom&startdt={}&enddt={}&'.format(start_date, end_date)
        self.url_info = "https://www.sec.gov/edgar/search/#/{}filter_forms=S-1".format(dates)
        return self.url_info

    def edgar_scrape(self, num):
        """
        Finds the names, dates, and types of forms filed by different companies

        Args:
            num (int): The number of entities to be scraped from a page

        Returns:
            tuple: A list of company names, a list of filing dates, and a set of filing types in chronological order

        Raises:
            ValueError: If `num` is greater than 100
        """

        if num > 100:
            raise ValueError('Cannot find more than 100 entires per page')

        driver = webdriver.Chrome('chromedriver')

        c_names = []
        c_dates = []
        form_types = set()
        driver.get(self.url_info)
        time.sleep(10)

        source = driver.page_source
        html_s = bs(source, 'html.parser')

        i = 0
        for item in html_s.findAll(attrs={'class': 'entity-name'}):
            if i == num:
                break
            if item.text != 'Filing entity/person':
                c_names.append(item.text)
                i += 1

        i2 = 0
        for item in html_s.findAll(attrs={'class': 'filed'}):
            if i2 == num:
                break
            if 'Filed' not in item.text:
                c_dates.append(item.text)
                i2 += 1

        i3 = 0
        for item in html_s.findAll(attrs={'class': 'filetype'}):
            if i3 == num:
                break
            if item.text != 'Form & File':
                i = item.text.find(' ')
                form_types.add(item.text[:i])
                i3 += 1
        driver.quit()
        return (c_names, c_dates, form_types)

    def generate_df(self, num_entries=100, num_pages=1):
        """
        Finds the names, dates, and types of forms filed by different companies

        Args:
            num_entries (int): The number of entities to be scraped from a page
            num_pages (int): The number of pages to be scraped

        Returns:
            pandas.DataFrame: A dataframe of the companies scraped and the dates they filed

        Raises:
            ValueError: If `num_entries` is greater than 100
        """

        if num_entries > 100:
            raise ValueError('Cannot find more than 100 entires per page')

        ns, ds, form = self.edgar_scrape(num_entries)
        d = {'names': ns, 'filing date': ds}

        if num_pages > 1:
            for i in range(num_pages - 1):
                self.set_page(i + 2)
                ns2, ds2 = self.edgar_scrape(num_entries)
                d['names'] += ns2
                d['filing date'] += ds2

        df = pd.DataFrame(data=d)
        return df

    def add_forms(self, forms_list):
        """
        Updates query to include certain form types, and modifies url_info as such

        Args:
            forms_list (list): List of strings for forms to search for

        Returns:
            tuple: A tuple of the string for the new url, and the appended forms
        """
        i = self.url_info.find('filter_forms=')
        pstr = ''

        pstr += forms_list[0]
        for form in forms_list[1:]:
            pstr += '%252C'
            pstr += form
        self.url_info = self.url_info[:i] + 'forms=' + pstr

        return (self.url_info, pstr)

    def get_anums(self, cik, num):
        """
        scrapes accession numbers from a page when given a cik

        Args:
            cik (int): The cik id for a company
            num (int): The number of entities to be scraped from a page

        Returns:
            list: a list of accession numbers relating to files for a cik
        """
        annual10k_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type=10-k".format(cik)
        doc_links = []
        driver = webdriver.Chrome('chromedriver')
        driver.get(annual10k_url)
        time.sleep(10)
        page = driver.page_source
        soup = bs(page, "html.parser")

        i = 0
        for item in soup.findAll(id='interactiveDataBtn'):
            if i == num:
                break
            else:
                s_ind = str(item).find('accession_number=')
                e_ind = str(item).find('&amp;xbrl')
                doc_links.append(str(item)[s_ind + len('accession_number=') : e_ind].replace('-', ''))
                i += 1
        driver.quit()
        return doc_links

    def get_refs(self, cik, num):
        """
        Finds the reference numbers for filings and company name for a given cik

        Args:
            cik (int): The cik id for a company
            num (int): The number of entities to be scraped from a page

        Returns:
            tuple: A list of filing reference numbers and the name of the company associated with a cik
        """
        edgar_url = "https://www.sec.gov/edgar/search/#/ciks={}&forms=10-K".format(cik)
        refs = []
        driver = webdriver.Chrome('chromedriver')
        driver.get(edgar_url)
        time.sleep(10)
        page = driver.page_source
        soup = bs(page, "html.parser")
        comp_name = ''

        i = 0
        for item in soup.findAll(attrs={"class": "preview-file"}):
            if i == num:
                break
            else:
                refs.append(item['data-file-name'])
                i += 1

        i2 = 0
        for item in soup.findAll(attrs={'class': 'entity-name'}):
            if i2 == num:
                break
            elif item.text != 'Filing entity/person':
                comp_name = item.text
                i += 1
        driver.quit()
        return refs, comp_name

    def create_links(self, cik, num):
        """
        Finds the links for xrbl versions of filings for a given cik

        Args:
            cik (int): The cik id for a company
            num (int): The number of entities to be scraped from a page

        Returns:
            tuple: A list of links to filings and the name of the company associated with a cik
        """
        anum_list = self.get_anums(cik, num)
        reflist, c_name = self.get_refs(cik, num)
        link_list = []
        for i in range(num):
            a = anum_list[i]
            r = reflist[i]
            link_list.append('https://www.sec.gov/ix?doc=/Archives/edgar/data/{}/{}/{}'.format(cik, a, r))
        return link_list, c_name

    def scrape_xbrl(self, link):
        """
        Finds the total assets, liabilities, and net income in a filing
        Args:
            link (str): link to an xbrl for a 10-K filing

        Returns:
            tuple: A tuple of the balance sheet's total assets, liabilities, and income statement's net income
        """
        driver = webdriver.Chrome('chromedriver')
        driver.get(link)
        time.sleep(10)
        page = driver.page_source
        soup = bs(page, "html.parser")
        TA = soup.find(attrs={'name': "us-gaap:Assets"}).text
        TL = soup.find(attrs={'name': "us-gaap:Liabilities"}).text
        NI = soup.find(attrs={'name': "us-gaap:ProfitLoss"}).text
        driver.quit()
        return (TA, TL, NI)
