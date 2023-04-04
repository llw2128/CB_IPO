import pandas as pd
import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver


class scrape:
    def __init__(self):
        self.url_info = "https://www.sec.gov/edgar/search/#/filter_forms=S-1"

    def set_page(self, pNo):
        pstr = '&page={}'.format(pNo)

        i = self.url_info.find('&page=')
        if i < 0:
            self.url_info += pstr
        else:
            self.url_info = self.url_info[:i] + pstr
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
        driver = webdriver.Chrome('chromedriver')

        c_names = []
        c_dates = []
        form_types = set()
        driver.get(self.url_info)
        time.sleep(10)

        source = driver.page_source
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
        driver.quit()
        return (c_names, c_dates, form_types)

    # argument is the number of pages to be pulled using scraper, deafult 1
    def generate_df(self, n=100, num_page=1):
        ns, ds, form = self.edgar_scrape(n)
        d = {'names': ns, 'filing date': ds}

        if num_page > 1:
            for i in range(num_page - 1):
                self.set_page(i + 2)
                ns2, ds2 = self.edgar_scrape(n)
                d['names'] += ns2
                d['filing date'] += ds2

        df = pd.DataFrame(data=d)
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

    def get_anums(self, cik, num):
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

        print(doc_links)
        driver.quit()
        return doc_links

    def get_refs(self, cik, num):
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
        anum_list = self.get_anums(cik, num)
        reflist, c_name = self.get_refs(cik, num)
        link_list = []
        for i in range(num):
            a = anum_list[i]
            r = reflist[i]
            link_list.append('https://www.sec.gov/ix?doc=/Archives/edgar/data/{}/{}/{}'.format(cik, a, r))
        return link_list, c_name

    def scrape_xbrl(self, link):
        driver = webdriver.Chrome('chromedriver')
        driver.get(link)
        time.sleep(10)
        page = driver.page_source
        soup = bs(page, "html.parser")
        TA = soup.find(attrs={'name': "us-gaap:Assets"}).text
        TL = soup.find(attrs={'name': "us-gaap:Liabilities"}).text
        NI = soup.find(attrs={'name': "us-gaap:ProfitLoss"}).text
        driver.quit()
        return [TA, TL, NI]
