import pandas as pd
import time
import math
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
        Scrapes accession numbers from a page when given a cik

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
        Finds the account value for elements like total assets, liabilities, and net income in a filing

        Args:
            link (str): link to an xbrl for a 10-K filing

        Returns:
            dict: A dictionary of financial statement elements such as total assets, liabilities, and net income

        Raises:
            Exception: If the scraped Assets, Liabilities, and Equity fail the Accounting Equation
        """
        Financials = {}

        driver = webdriver.Chrome('chromedriver')
        driver.get(link)
        time.sleep(10)
        page = driver.page_source
        soup = bs(page, "html.parser")
        registrant = soup.find(attrs={'name': "dei:EntityRegistrantName"}).text
        TA_s = soup.find(attrs={'name': "us-gaap:Assets"}).text
        TL_s = soup.find(attrs={'name': "us-gaap:Liabilities"}).text
        NI_s = soup.find(attrs={'name': "us-gaap:NetIncomeLoss"}).text
        TE_s = soup.find(attrs={'name': "us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"}).text
        CA_s = soup.find(attrs={'name': "us-gaap:AssetsCurrent"}).text
        CL_s = soup.find(attrs={'name': "us-gaap:LiabilitiesCurrent"}).text
        LongTerm_Debt_s = soup.find(attrs={'name': "us-gaap:LongTermDebtNoncurrent"}).text
        Current_Debt_s = soup.find(attrs={'name': "us-gaap:DebtCurrent"}).text
        Inventory_s = soup.find(attrs={'name': "us-gaap:InventoryNet"}).text

        if '(' in TE_s and ')' in TE_s:
            TE_s = TE_s.replace('(', '').replace(')', '')
            TE_s = TE_s.insert(0, '-')

        if '(' in NI_s and ')' in NI_s:
            NI_s = NI_s.replace('(', '').replace(')', '')
            NI_s = NI_s.insert(0, '-')

        Financials['Total Assets'] = float(TA_s.replace(',', ''))
        Financials['Total Liabilities'] = float(TL_s.replace(',', ''))
        Financials['Total Equity'] = float(TE_s.replace(',', ''))

        Financials['Current Assets'] = float(CA_s.replace(',', ''))
        Financials['Current Liabilities'] = int(CL_s.replace(',', ''))

        Financials['Net Income'] = float(NI_s.replace(',', ''))

        Financials['Long Term Debt'] = float(LongTerm_Debt_s.replace(',', ''))
        Financials['Current Debt'] = float(Current_Debt_s.replace(',', ''))

        Financials['Inventory'] = float(Inventory_s.replace(',', ''))

        Financials['Registrant'] = registrant
        if not math.isclose(Financials['Total Assets'] - Financials['Total Liabilities'], Financials['Total Equity'], abs_tol=1):
            driver.quit()
            raise Exception("Total Assets and Liabilities not consistent with equity")

        driver.quit()

        return Financials

    def calculate_ratios(self, financials):
        """
        Calculates financial ratios relevant to balance sheet and income statements

        Args:
            financials (dict): a dictionary containg Asset and Liability information, as formatted by scrape_xrbl()

        Returns:
            dict: A dictionary of financial ratios relating to profitability, liquidity, and leverage

        Raises:
            ValueError: If `financials` is improperly formated and doesn't contain the requisite values
        """
        ratios = {}
        info = financials

        TA, TL, NI, TE, CA, CL, LtD, StD, Ivt = (
            info['Total Assets'],
            info['Total Liabilities'],
            info['Net Income'],
            info['Total Equity'],
            info['Current Assets'],
            info['Current Liabilities'],
            info['Long Term Debt'],
            info['Current Debt'],
            info['Inventory'],
        )

        values = (TA, TL, NI, TE, CA, CL, LtD, StD, Ivt)

        for v in values:
            if not isinstance(v, float) and not isinstance(v, int):
                print(type(v))
                raise ValueError("Improper Formatting of finanical values")

        if TE != 0:
            ratios['D/E'] = TL * 1.0 / TE
            ratios['ROE'] = NI * 1.0 / TE

        if CL != 0:
            ratios['Working Capital'] = CA * 1.0 / CL
            ratios['Quick'] = (CA - Ivt) * 1.0 / CL

        if TA != 0:
            ratios['TD/TA'] = (LtD + StD) * 1.0 / TA
            ratios['ROA'] = (NI * 1.0) / TA

        return ratios

    def summarize_10k(self, link, flag='raw'):
        """
        Creates dataframe that summarize information scraped from the 10-K filing

        Args:
            link (str): link to an xbrl for a 10-K filing
            flag (str): str indicating summary type, 'raw', 'liquidity', 'profitability', etc

        Returns:
            pandas.DataFrame: A dataframe of the companies scraped and the dates they filed
        """
        finances = self.scrape_xbrl(link)
        ratios = self.calculate_ratios(finances)

        if flag == 'raw':
            raw_df = pd.DataFrame(finances.items(), columns=['Account', 'Amount'])
            return raw_df

        elif flag == 'ratios':
            ratio_df = pd.DataFrame(ratios.items(), columns=['Ratio', 'Value'])
            return ratio_df

        elif flag == 'leverage':
            d2e = ratios['D/E']
            tdta = ratios['TD/TA']
            data = [['D/E', d2e], ['TD/TA', tdta]]
            lev_df = pd.DataFrame(data, columns=['Ratio', 'Value'])
            return lev_df

        elif flag == 'profitability':
            roa = ratios['ROA']
            roe = ratios['ROE']
            data = [['ROE', roe], ['ROA', roa]]
            profit_df = pd.DataFrame(data, columns=['Ratio', 'Value'])
            return profit_df

        elif flag == 'liquidity':
            quick = ratios['Quick']
            wcap = ratios['Working Capital']
            data = [['Quick', quick], ['Working Capital', wcap]]
            liq_df = pd.DataFrame(data, columns=['Ratio', 'Value'])
            return liq_df

        elif flag == 'totals':
            TA = finances['Total Assets']
            TL = finances['Total Liabilities']
            TE = finances['Total Equity']
            data = [['Total Assets', TA], ['Total Liabilities', TL], ['Total Equity', TE]]
            total_df = pd.DataFrame(data, columns=['Account', 'Amount'])
            return total_df

        elif flag == 'current':
            CA = finances['Current Assets']
            CL = finances['Current Liabilities']
            CD = finances['Current Debt']
            data = [['Current Assets', CA], ['Current Liabilities', CL], ['Current Debt', CD]]
            curr_df = pd.DataFrame(data, columns=['Account', 'Amount'])
            return curr_df

        elif flag == 'debt':
            LtD = finances['Long Term Debt']
            CD = finances['Current Debt']
            data = [['Long Term Debt', LtD], ['Current Debt', CD]]
            debt_df = pd.DataFrame(data, columns=['Account', 'Amount'])
            return debt_df

        return pd.DataFrame()
