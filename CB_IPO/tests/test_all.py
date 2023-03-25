from CB_IPO import scrape
from pytest import mark
import pandas as pd
import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver


tester = scrape()
pfizer_cik = '0000078003'
entries_ret = 4
test_file_link = 'https://www.sec.gov/ix?doc=/Archives/edgar/data/78003/000007800323000024/pfe-20221231.htm'
link2 = 'https://www.sec.gov/Archives/edgar/data/78003/000007800322000027/pfe-20211231.htm'


# Makes sure that the proper data gets scraped
@mark.parametrize("input, output", [(test_file_link, ['197,205', '101,288', '31,407']), (link2, ['181,476', '104,013', '22,025'])])
def test_10kScraper(input, output):
    assert tester.scrape_xbrl(input) == output


# checks that links are valid and expected
@mark.parametrize(
    "input, output",
    [
        (
            (pfizer_cik, entries_ret),
            (
                [
                    'https://www.sec.gov/ix?doc=/Archives/edgar/data/0000078003/000007800323000024/pfe-20221231.htm',
                    'https://www.sec.gov/ix?doc=/Archives/edgar/data/0000078003/000007800322000027/pfe-20211231.htm',
                    'https://www.sec.gov/ix?doc=/Archives/edgar/data/0000078003/000007800321000038/pfe-20201231.htm',
                    'https://www.sec.gov/ix?doc=/Archives/edgar/data/0000078003/000007800320000014/pfe-12312019x10kshell.htm',
                ],
                'PFIZER INC  (PFE) ',
            ),
        )
    ],
)
def test_create_links(input, output):
    driver = webdriver.Chrome('chromedriver')
    results = tester.create_links(input[0], input[1])
    for i in results[0]:
        driver.get(i)
        time.sleep(10)
        page = driver.page_source
        soup = bs(page, "html.parser")
        assert soup.findAll(text='10-K') != []
    assert results[0] == output[0]
    assert results[1] == output[1]
    driver.quit()


@mark.parametrize("input, output", [((pfizer_cik, entries_ret), (['pfe-20221231.htm', 'pfe-20211231.htm', 'pfe-20201231.htm', 'pfe-12312019x10kshell.htm'], 'PFIZER INC  (PFE) '))])
def test_refs(input, output):
    assert tester.get_refs(input[0], input[1])[0] == output[0]
    assert tester.get_refs(input[0], input[1])[1] == output[1]


@mark.parametrize("input, output", [((pfizer_cik, entries_ret), ['000007800323000024', '000007800322000027', '000007800321000038', '000007800320000014'])])
def test_anums(input, output):
    assert tester.get_anums(input[0], input[1]) == output


@mark.parametrize(
    "input,output",
    [
        (5, "https://www.sec.gov/edgar/search/#/filter_forms=S-1&page=5"),
        (4, "https://www.sec.gov/edgar/search/#/filter_forms=S-1&page=4"),
    ],
)
def test_page_set(input, output):
    tester.reset_url()
    assert tester.set_page(input) == output


@mark.parametrize(
    "in_d1,in_d2,output",
    [
        (
            '2014-03-04',
            '2015-03-04',
            "https://www.sec.gov/edgar/search/#/dateRange=custom&category=custom&startdt=2014-03-04&enddt=2015-03-04&filter_forms=S-1",
        ),
        (
            '2022-04-03',
            '2023-04-03',
            "https://www.sec.gov/edgar/search/#/dateRange=custom&category=custom&startdt=2022-04-03&enddt=2023-04-03&filter_forms=S-1",
        ),
    ],
)
def test_page_date(in_d1, in_d2, output):
    tester.reset_url()
    assert tester.set_search_date(in_d1, in_d2) == output


@mark.parametrize(
    "input, output, url",
    [
        (
            4,
            (
                [
                    "U.S. GoldMining Inc.  (USGO) ",
                    "RingCentral, Inc.  (RNG) ",
                    "MariaDB plc  (MRDB, MRDB-WT) ",
                    "Kenvue Inc.  (KVUE) ",
                ],
                ["2023-03-03", "2023-03-03", "2023-03-03", "2023-03-03"],
            ),
            'https://www.sec.gov/edgar/search/#/dateRange=custom&category=custom&startdt=2022-03-01&enddt=2023-03-03&filter_forms=S-1',
        )
    ],
)
def test_scraper(input, output, url):
    tester.url_info = url
    ns, ds, forms = tester.edgar_scrape(input)
    assert ns == output[0]
    assert ds == output[1]
    assert len(ns) == input
    assert len(ds) == input


test_d = {
    'names': [
        "U.S. GoldMining Inc.  (USGO) ",
        "RingCentral, Inc.  (RNG) ",
        "MariaDB plc  (MRDB, MRDB-WT) ",
        "Kenvue Inc.  (KVUE) ",
    ],
    'filing date': ["2023-03-03", "2023-03-03", "2023-03-03", "2023-03-03"],
}


@mark.parametrize(
    "input, df_out, url",
    [([4, 1], test_d, 'https://www.sec.gov/edgar/search/#/dateRange=custom&category=custom&startdt=2022-03-01&enddt=2023-03-03&filter_forms=S-1')],
)
def test_dfgen(input, df_out, url):
    tester.url_info = url
    a1, a2 = input
    outdf = pd.DataFrame(data=df_out)
    assert tester.generate_df(a1, a2).equals(outdf)


@mark.parametrize("input,output", [(('S-B', '10-K'), 'S-B%252C10-K'), (('10-Q', 'S-B', 'C'), '10-Q%252CS-B%252CC')])
def test_add_forms(input, output):
    tester.reset_url()
    out = tester.add_forms(input)
    for i in input:
        assert i in out[1]
    assert out[1] == output


# Forms scraper integration test
@mark.parametrize("input", [('10-Q', 'S-1', 'C')])
def test_add_forms_EDGAR(input):
    tester.reset_url()
    a = tester.add_forms(input)
    print(a[0])
    ls1, ls2, form_found = tester.edgar_scrape(100)
    for i in input:
        assert i in form_found
