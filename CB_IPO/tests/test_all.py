from CB_IPO import scrape
import pytest as pt
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
link3 = 'https://www.sec.gov/Archives/edgar/data/200406/000020040623000016/jnj-20230101.htm'

r1_dict = {'D/E': 1.0560073397556196, 'ROE': 0.3270778597939864, 'Working Capital': 1.216455455883051, 'Quick': 1.0033224168209218, 'TD/TA': 0.181684034380467, 'ROA': 0.1590831875459547}

r2_dict = {'D/E': 1.3427616121453099, 'ROE': 0.2837391236993623, 'Working Capital': 1.3989126104380023, 'Quick': 1.1866138595298914, 'TD/TA': 0.2117966012034649, 'ROA': 0.12111243360003526}

r3_dict = {'D/E': 1.4396906411124422, 'ROE': 0.233594604447685, 'Working Capital': 0.9908963836421634, 'Quick': 0.7671947242034336, 'TD/TA': 0.14356434586771125, 'ROA': 0.09574763312662106}

f_dict = {
    'Total Assets': 197205.0,
    'Total Liabilities': 101288.0,
    'Total Equity': 95916.0,
    'Current Assets': 51259.0,
    'Current Liabilities': 42138.0,
    'Net Income': 31372.0,
    'Long Term Debt': 32884.0,
    'Current Debt': 2945.0,
    'Inventory': 8981.0,
    'Registrant': 'PFIZER INC',
}

f_dict2 = {
    'Total Assets': 187378.0,
    'Total Liabilities': 110574,
    'Total Equity': 76804.0,
    'Current Assets': 55294.0,
    'Current Liabilities': 55802,
    'Net Income': 17941.0,
    'Long Term Debt': 26888.0,
    'Current Debt': 12.8,
    'Inventory': 12483.0,
    'Registrant': 'JOHNSON & JOHNSON',
}


@mark.parametrize("input, output", [((pfizer_cik, entries_ret), (['pfe-20221231.htm', 'pfe-20211231.htm', 'pfe-20201231.htm', 'pfe-12312019x10kshell.htm'], 'PFIZER INC  (PFE) '))])
def test_refs(input, output):
    assert tester.get_refs(input[0], input[1])[0] == output[0]
    assert tester.get_refs(input[0], input[1])[1] == output[1]


def test_dfErr():
    with pt.raises(ValueError, match='Cannot find more than 100 entires per page'):
        tester.generate_df(200, 2)


def test_scrapeErr():
    with pt.raises(ValueError, match='Cannot find more than 100 entires per page'):
        tester.edgar_scrape(109)


@mark.parametrize(
    "input, link, output",
    [
        ('non_existant', link3, pd.DataFrame()),
    ],
)
def test_unk_summary(input, link, output):
    result = tester.summarize_10k(link, flag=input)
    assert output.equals(result)


@mark.parametrize(
    "output, link",
    [
        (dict((key, f_dict[key]) for key in ('Total Assets', 'Total Liabilities', 'Total Equity')), test_file_link),
        (dict((key, f_dict2[key]) for key in ('Total Assets', 'Total Liabilities', 'Total Equity')), link3),
    ],
)
def test_totals_summary(link, output):
    expected = pd.DataFrame(output.items(), columns=['Account', 'Amount'])
    result = tester.summarize_10k(link, flag='totals')
    assert expected.equals(result)


@mark.parametrize(
    "output, link",
    [
        (dict((key, f_dict[key]) for key in ('Current Assets', 'Current Liabilities', 'Current Debt')), test_file_link),
        (dict((key, f_dict2[key]) for key in ('Current Assets', 'Current Liabilities', 'Current Debt')), link3),
    ],
)
def test_current_summary(link, output):
    expected = pd.DataFrame(output.items(), columns=['Account', 'Amount'])
    result = tester.summarize_10k(link, flag='current')
    assert expected.equals(result)


@mark.parametrize(
    "output, link",
    [
        (dict((key, f_dict[key]) for key in ('Long Term Debt', 'Current Debt')), test_file_link),
        (dict((key, f_dict2[key]) for key in ('Long Term Debt', 'Current Debt')), link3),
    ],
)
def test_debt_summary(link, output):
    expected = pd.DataFrame(output.items(), columns=['Account', 'Amount'])
    result = tester.summarize_10k(link, flag='debt')
    assert expected.equals(result)


@mark.parametrize(
    "output, link",
    [
        (dict((key, r1_dict[key]) for key in ('Quick', 'Working Capital')), test_file_link),
        (dict((key, r2_dict[key]) for key in ('Quick', 'Working Capital')), link2),
        (dict((key, r3_dict[key]) for key in ('Quick', 'Working Capital')), link3),
    ],
)
def test_liquidity_summary(link, output):
    expected = pd.DataFrame(output.items(), columns=['Ratio', 'Value'])
    result = tester.summarize_10k(link, flag='liquidity')
    assert expected.equals(result)


@mark.parametrize(
    "output, link",
    [(dict((key, r1_dict[key]) for key in ('ROE', 'ROA')), test_file_link), (dict((key, r2_dict[key]) for key in ('ROE', 'ROA')), link2), (dict((key, r3_dict[key]) for key in ('ROE', 'ROA')), link3)],
)
def test_profitability_summary(link, output):
    expected = pd.DataFrame(output.items(), columns=['Ratio', 'Value'])
    result = tester.summarize_10k(link, flag='profitability')
    assert expected.equals(result)


@mark.parametrize(
    "output, link",
    [
        (dict((key, r1_dict[key]) for key in ('D/E', 'TD/TA')), test_file_link),
        (dict((key, r2_dict[key]) for key in ('D/E', 'TD/TA')), link2),
        (dict((key, r3_dict[key]) for key in ('D/E', 'TD/TA')), link3),
    ],
)
def test_leverage_summary(link, output):
    expected = pd.DataFrame(output.items(), columns=['Ratio', 'Value'])
    result = tester.summarize_10k(link, flag='leverage')
    assert expected.equals(result)


@mark.parametrize("output, link", [(r1_dict, test_file_link), (r2_dict, link2), (r3_dict, link3)])
def test_ratio_summary(link, output):
    expected = pd.DataFrame(output.items(), columns=['Ratio', 'Value'])
    result = tester.summarize_10k(link, flag='ratios')
    assert expected.equals(result)


@mark.parametrize(
    "link, output",
    [
        (
            test_file_link,
            {
                'Total Assets': 197205,
                'Total Liabilities': 101288,
                'Total Equity': 95916,
                'Current Assets': 51259,
                'Current Liabilities': 42138,
                'Net Income': 31372,
                'Long Term Debt': 32884,
                'Current Debt': 2945,
                'Inventory': 8981,
                'Registrant': 'PFIZER INC',
            },
        ),
        (
            link2,
            {
                'Total Assets': 181476,
                'Total Liabilities': 104013,
                'Total Equity': 77462,
                'Current Assets': 59693,
                'Current Liabilities': 42671,
                'Net Income': 21979,
                'Long Term Debt': 36195,
                'Current Debt': 2241,
                'Inventory': 9059,
                'Registrant': 'PFIZER INC',
            },
        ),
        (
            link3,
            {
                'Total Assets': 187378.0,
                'Total Liabilities': 110574,
                'Total Equity': 76804.0,
                'Current Assets': 55294.0,
                'Current Liabilities': 55802,
                'Net Income': 17941.0,
                'Long Term Debt': 26888.0,
                'Current Debt': 12.8,
                'Inventory': 12483.0,
                'Registrant': 'JOHNSON & JOHNSON',
            },
        ),
    ],
)
def test_raw_summary(link, output):
    expected = pd.DataFrame(output.items(), columns=['Account', 'Amount'])
    result = tester.summarize_10k(link, flag='raw')
    assert expected.equals(result)


# Makes sure that the ratios are correctly calculated
@mark.parametrize(
    "output, input",
    [
        (
            {'D/E': 1.0560073397556196, 'ROE': 0.3270778597939864, 'Working Capital': 1.216455455883051, 'Quick': 1.0033224168209218, 'TD/TA': 0.181684034380467, 'ROA': 0.1590831875459547},
            {
                'Total Assets': 197205,
                'Total Liabilities': 101288,
                'Total Equity': 95916,
                'Current Assets': 51259,
                'Current Liabilities': 42138,
                'Net Income': 31372,
                'Long Term Debt': 32884,
                'Current Debt': 2945,
                'Inventory': 8981,
                'Registrant': 'PFIZER INC',
            },
        ),
        (
            {'D/E': 1.3427616121453099, 'ROE': 0.2837391236993623, 'Working Capital': 1.3989126104380023, 'Quick': 1.1866138595298914, 'TD/TA': 0.2117966012034649, 'ROA': 0.12111243360003526},
            {
                'Total Assets': 181476,
                'Total Liabilities': 104013,
                'Total Equity': 77462,
                'Current Assets': 59693,
                'Current Liabilities': 42671,
                'Net Income': 21979,
                'Long Term Debt': 36195,
                'Current Debt': 2241,
                'Inventory': 9059,
                'Registrant': 'PFIZER INC',
            },
        ),
        (
            {'D/E': 1.4396906411124422, 'ROE': 0.233594604447685, 'Working Capital': 0.9908963836421634, 'Quick': 0.7671947242034336, 'TD/TA': 0.14356434586771125, 'ROA': 0.09574763312662106},
            {
                'Total Assets': 187378.0,
                'Total Liabilities': 110574,
                'Total Equity': 76804.0,
                'Current Assets': 55294.0,
                'Current Liabilities': 55802,
                'Net Income': 17941.0,
                'Long Term Debt': 26888.0,
                'Current Debt': 12.8,
                'Inventory': 12483.0,
                'Registrant': 'JOHNSON & JOHNSON',
            },
        ),
    ],
)
def test_ratios(input, output):
    assert tester.calculate_ratios(input) == output


# Makes sure that the proper data gets scraped
@mark.parametrize(
    "input, output",
    [
        (
            test_file_link,
            {
                'Total Assets': 197205,
                'Total Liabilities': 101288,
                'Total Equity': 95916,
                'Current Assets': 51259,
                'Current Liabilities': 42138,
                'Net Income': 31372,
                'Long Term Debt': 32884,
                'Current Debt': 2945,
                'Inventory': 8981,
                'Registrant': 'PFIZER INC',
            },
        ),
        (
            link2,
            {
                'Total Assets': 181476,
                'Total Liabilities': 104013,
                'Total Equity': 77462,
                'Current Assets': 59693,
                'Current Liabilities': 42671,
                'Net Income': 21979,
                'Long Term Debt': 36195,
                'Current Debt': 2241,
                'Inventory': 9059,
                'Registrant': 'PFIZER INC',
            },
        ),
        (
            link3,
            {
                'Total Assets': 187378.0,
                'Total Liabilities': 110574,
                'Total Equity': 76804.0,
                'Current Assets': 55294.0,
                'Current Liabilities': 55802,
                'Net Income': 17941.0,
                'Long Term Debt': 26888.0,
                'Current Debt': 12.8,
                'Inventory': 12483.0,
                'Registrant': 'JOHNSON & JOHNSON',
            },
        ),
    ],
)
def test_10kScraper(input, output):
    result = tester.scrape_xbrl(input)
    for val in result.values():
        if not isinstance(val, str):
            assert val > 0
    assert result == output


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


@mark.parametrize("input,output", [(('S-B', '10-K'), 'S-B%252C10-K'), (('10-Q', 'S-B', 'C'), '10-Q%252CS-B%252CC')])
def test_add_forms(input, output):
    tester.reset_url()
    out = tester.add_forms(input)
    for i in input:
        assert i in out[1]
    assert out[1] == output


# Forms scraper integration test
@mark.parametrize("input,d1,d2", [(('20-F', 'S-1', 'S-1/A'), '2023-05-02', '2023-05-03')])
def test_add_forms_EDGAR(input, d1, d2):
    tester.reset_url()
    tester.set_search_date(d1, d2)
    a = tester.add_forms(input)
    print(a[0])
    ls1, ls2, form_found = tester.edgar_scrape(100)
    for i in input:
        assert i in form_found
