import requests
import sys
import pandas as pd 
import numpy as np 
#from sec_api import QueryApi
from bs4 import BeautifulSoup as bs
from selenium import webdriver


#queryApi = QueryApi(api_key=API_KEY) 

browser =  webdriver.Chrome('./chromedriver')

url_info = "https://www.sec.gov/edgar/search/#/filter_forms=S-1"

"""
Resets url for accessing pages of EDGAR table
"""

def set_page(pNo):
  pstr = '&page={}'.format(pNo)
  global url_info

  i = url_info.find('&page=')
  if i<0:
    url_info+=pstr
    print(url_info)
  else:
    url_info = url_info[:i]+pstr
    print(url_info)
    
#Helper funciton to modify dates for webscraper
def set_search_date(d1,d2):
  dates = 'dateRange=custom&category=custom&startdt={}&enddt={}&'.format(d1,d2)
  global url_info 
  url_info= "https://www.sec.gov/edgar/search/#/{}filter_forms=S-1".format(dates)


def edgar_scrape():
  c_names = []
  sada = browser.get(url_info)
  source = browser.page_source
  html_s = bs(source, 'html.parser')

  #find name for all recent S-1 filers with the  SEC
  for item in html_s.findAll( attrs={'class': 'entity-name'}):
    if item.text != 'Filing entity/person':
      c_names.append(item.text)

  #generate list of the  filing dates 
  c_dates = []
  for item in html_s.findAll( attrs={'class': 'filed'}):
    if item.text != 'Filed':
      c_dates.append(item.text)

  #print(c_names)
  return (c_names,c_dates)

#argument is the number of pages to be pulled using scraper, deafult 1
def generate_df(num_page=1):
  ns,ds = edgar_scrape()
  d = {'names':ns, 'filing date':ds}
  
  if num_page>1:
    #adds values to dictionary from queried pages
    for i in range(num_page-1):
      set_page(i+2)
      ns2,ds2 = edgar_scrape()
      d['names']+=ns2
      d['filing date']+=ds2

  df = pd.DataFrame(data=d)
  print(df)
  return  df

def get_ipo():

  query = {
      "query": { "query_string": { 
        "query": "formType:\"S-1\" AND filedAt:{2020-01-01 TO 2020-12-31}"
    } },
  "from": "0",
  "size": "10",
  "sort": [{ "filedAt": { "order": "desc" } }]}
  #filings = q.get_filings(query)

########
def search_CB(name):
  CB_key = input('Enter CB API: ')
  req = 'https://api.crunchbase.com/api/v4/autocompletes?query={}&limit=15&user_key={}'.format(name,CB_key)
  CB_info =  requests.get(req).text
  print(CB_info)
  return(CB_info[0])

def add_CB(dframe):
  gen_descr = []

  for r in dframe.rows:
    gen_descr.append(search_CB(r['names']))
  dframe['CB Description'] = gen_descr


#set_search_date('2018-02-20','2023-02-10')
#print(url_info)
generate_df(3)


