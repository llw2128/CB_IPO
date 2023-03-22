import requests
import pandas as pd

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

# from pyvirtualdisplay import Display


# queryApi = QueryApi(api_key=API_KEY)
class scrape:
    def __init__(self):
        # self.browser = webdriver.Chrome('chromedriver')

        self.url_info = "https://www.sec.gov/edgar/search/#/filter_forms=S-1"

        # TEST
        """
        df_out = {
        'names': [
        "U.S. GoldMining Inc.  (USGO) ",
        "RingCentral, Inc.  (RNG) ",
        "MariaDB plc  (MRDB, MRDB-WT) ",
        "Kenvue Inc.  (KVUE) ",
        ],
        'filing date': ["2023-03-03", "2023-03-03", "2023-03-03", "2023-03-03"],
        }
        self.url_info = 'https://www.sec.gov/edgar/search/#/dateRange=cus
        tom&category=custom&startdt=2022-03-01&enddt=2023-03-03&filter_forms=S-1'
        outdf = pd.DataFrame(data=df_out)
        print(self.generate_df(4, 1).equals(outdf))
        print()
        print(outdf)"""

    def set_page(self, pNo):
        pstr = '&page={}'.format(pNo)

        i = self.url_info.find('&page=')
        if i < 0:
            self.url_info += pstr
            print(self.url_info)
        else:
            self.url_info = self.url_info[:i] + pstr
            print(self.url_info)
        return self.url_info

    def reset_url(self):
        self.url_info = "https://www.sec.gov/edgar/search/#/filter_forms=S-1"
        return self.url_info

    # Helper funciton to modify dates for webscraper
    def set_search_date(self, d1, d2):
        dates = 'dateRange=custom&category=custom&startdt={}&enddt={}&'.format(d1, d2)
        self.url_info = "https://www.sec.gov/edgar/search/#/{}filter_forms=S-1".format(dates)
        return self.url_info

    def document_initialised(self):
        return self.driver.execute_script("return initialised")

    def edgar_scrape(self, num):
        self.driver = webdriver.Chrome('chromedriver')  # new
        self.driver.implicitly_wait(300)
        self.driver.maximize_window()

        c_names = []
        c_dates = []
        form_types = set()

        print("my url is  :     ")
        print(self.url_info)

        self.driver.get(self.url_info)

        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "entity-name")))
        except TimeoutException:
            print("Page did not load")

        source = self.driver.page_source
        html_s = bs(source, 'html.parser')

        # find name for all recent S-1 filers with the  SEC
        i = 0
        for item in html_s.findAll(attrs={'class': 'entity-name'}):
            if i == num:
                break
            if item.text != 'Filing entity/person':
                c_names.append(item.text)
                i += 1

        # generate list of the  filing dates

        i2 = 0
        for item in html_s.findAll(attrs={'class': 'filed'}):
            if i2 == num:
                break
            if item.text != 'Filed':
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
        # print(c_names)
        self.driver.quit()
        return (c_names, c_dates, form_types)

    # argument is the number of pages to be pulled using scraper, deafult 1
    def generate_df(self, n=100, num_page=1):
        ns, ds, form = self.edgar_scrape(n)
        d = {'names': ns, 'filing date': ds}

        if num_page > 1:
            # adds values to dictionary from queried pages
            for i in range(num_page - 1):
                self.set_page(i + 2)
                ns2, ds2 = self.edgar_scrape(n)
                d['names'] += ns2
                d['filing date'] += ds2

        df = pd.DataFrame(data=d)
        # print(df)
        return df

    def add_forms(self, list):
        i = self.url_info.find('filter_forms=')
        pstr = ''

        pstr += list[0]
        for form in list[1:]:
            pstr += '%252C'
            pstr += form
        self.url_info = self.url_info[:i] + 'forms=' + pstr

        return (self.url_info, pstr)

    def get_ipo(self):
        """
        query = {
            "query": {"query_string": {"query": "formType:\"S-1\" AND filedAt:{2020-01-01 TO 2020-12-31}"}},
            "from": "0",
            "size": "10",
            "sort": [{"filedAt": {"order": "desc"}}],
        }"""
        # filings = q.get_filings(query)

    ########
    def search_CB(self, name):
        CB_key = input('Enter CB API: ')
        req = 'https://api.crunchbase.com/api/v4/autocompletes?query={}&limit=15&user_key={}'.format(name, CB_key)
        CB_info = requests.get(req).text
        print(CB_info)
        return CB_info[0]

    def add_CB(self, dframe):
        gen_descr = []

        for r in dframe.rows:
            gen_descr.append(self.search_CB(r['names']))
        dframe['CB Description'] = gen_descr

    # set_search_date('2018-02-20','2023-02-10')
    # print(url_info)
    # generate_df(3)

    """
    a =  {
                'names': [
                    "U.S. GoldMining Inc.  (USGO) ",
                    "RingCentral, Inc.  (RNG) ",
                    "MariaDB plc  (MRDB, MRDB-WT) ",
                    "Kenvue Inc.  (KVUE) ",
                ],
                'filing date': ["2023-03-03", "2023-03-03", "2023-03-03", "2023-03-03"],
            }


    outdf = pd.DataFrame(data=a)
    print(outdf.equals(generate_df(4, 1)))
    print()
    print(outdf)

    reset_url()
    add_forms(('10-Q', 'S-B', 'C'))
    ls1, ls2, forms = edgar_scrape(100)
    print(forms)"""


# n = scrape()
