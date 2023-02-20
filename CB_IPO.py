import requests
import sys
import pandas as pd 
import numpy as np 
#from sec_api import QueryApi
from bs4 import BeautifulSoup as bs
from selenium import webdriver

#API_KEY = "99d839ea83f2e31b7b116a03f51087fada8ac3ef32abaa8e7d702b1d037487fc"

#queryApi = QueryApi(api_key=API_KEY)
browser =  webdriver.Chrome('./chromedriver')

url_info = "https://www.sec.gov/edgar/search/#/filter_forms=S-1"


def set_search_date(d1,d2):
  dates = 'dateRange=custom&category=custom&startdt={}&enddt={}&'.format(d1,d2)
  global url_info 
  url_info= "https://www.sec.gov/edgar/search/#/{}filter_forms=S-1".format(dates)

def edgar_scrape():
  e_data = []
  sada = browser.get(url_info)
  source = browser.page_source
  html_s = bs(source, 'html.parser')

  for item in html_s.findAll( attrs={'class': 'entity-name'}):
    if item.text != 'Filing entity/person':
      e_data.append([item.text])

  i =0
  for item in html_s.findAll( attrs={'class': 'filed'}):
    if item.text != 'Filed':
      e_data[i].append(item.text)
      i+=1
  print(e_data)

def generate_df(comp_arr):
  

def get_ipo():

  query = {
      "query": { "query_string": { 
        "query": "formType:\"S-1\" AND filedAt:{2020-01-01 TO 2020-12-31}"
    } },
  "from": "0",
  "size": "10",
  "sort": [{ "filedAt": { "order": "desc" } }]}
  #filings = q.get_filings(query)
  #print(filings)

#set_search_date('2018-02-20','2023-02-10')
#print(url_info)
edgar_scrape()

