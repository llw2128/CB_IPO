from CB_IPO import set_page, set_search_date,edgar_scrape,search_CB
from unittest.mock import patch
from pytest import mark

@mark.parameterize("input,output",[(5,"https://www.sec.gov/edgar/search/#/filter_forms=S-1&page=5"),(4,"https://www.sec.gov/edgar/search/#/filter_forms=S-1&page=4")])
def test_page_set(input,output):
    assert set_page() == output

@mark.parameterize("in_d1,in_d2,output",[('2018-03-04','sjldksfdj',"https://www.sec.gov/edgar/search/#/dateRange=custom&category=custom&startdt={}&enddt={}&filter_forms=S-1"),('2012-04-23','2022-04-23',"https://www.sec.gov/edgar/search/#/dateRange=custom&category=custom&startdt=2012-04-23&enddt=2022-04-23&filter_forms=S-1")])
def test_page_date(in_d1,in_d2,output):
    assert set_page() == output


@mark.parameterize("input,output",[])
def test_scraper():
    assert()
