from CB_IPO import scrape
from pytest import mark
import pandas as pd

tester = scrape()


@mark.parametrize(
    "input,output", [(5, "https://www.sec.gov/edgar/search/#/filter_forms=S-1&page=5"), (4, "https://www.sec.gov/edgar/search/#/filter_forms=S-1&page=4"),],
)
def test_page_set(input, output):
    tester.reset_url()
    assert tester.set_page(input) == output


@mark.parametrize(
    "in_d1,in_d2,output",
    [
        ('2014-03-04', '2015-03-04', "https://www.sec.gov/edgar/search/#/dateRange=custom&category=custom&startdt=2014-03-04&enddt=2015-03-04&filter_forms=S-1",),
        ('2012-04-23', '2022-04-23', "https://www.sec.gov/edgar/search/#/dateRange=custom&category=custom&startdt=2012-04-23&enddt=2022-04-23&filter_forms=S-1",),
    ],
)
def test_page_date(in_d1, in_d2, output):
    assert tester.set_search_date(in_d1, in_d2) == output


@mark.parametrize(
    "input, output",
    [(4, (["U.S. GoldMining Inc.  (USGO) ", "RingCentral, Inc.  (RNG) ", "MariaDB plc  (MRDB, MRDB-WT) ", "Kenvue Inc.  (KVUE) ",], ["2023-03-03", "2023-03-03", "2023-03-03", "2023-03-03"],),)],
)
def test_scraper(input, output):
    tester.reset_url()
    tester.set_search_date('2022-03-01', '2023-03-03')
    ns, ds, forms = tester.edgar_scrape(input)
    assert ns == output[0]
    assert ds == output[1]
    assert len(ns) == input
    assert len(ds) == input


test_d = {
    'names': ["U.S. GoldMining Inc.  (USGO) ", "RingCentral, Inc.  (RNG) ", "MariaDB plc  (MRDB, MRDB-WT) ", "Kenvue Inc.  (KVUE) ",],
    'filing date': ["2023-03-03", "2023-03-03", "2023-03-03", "2023-03-03"],
}


@mark.parametrize(
    "input, df_out", [([4, 1], test_d)],
)
def test_dfgen(input, df_out):
    tester.reset_url()
    tester.set_search_date('2023-03-01', '2023-03-03')
    a1, a2 = input

    outdf = pd.DataFrame(data=df_out)
    print(outdf)
    assert tester.generate_df(a1, a2).equals(outdf)


@mark.parametrize("input,output", [(('S-B', '10-K'), 'S-B%252C10-K'), (('10-Q', 'S-B', 'C'), '10-Q%252CS-B%252CC')])
def test_add_forms(input, output):
    tester.reset_url()
    out = tester.add_forms(input)
    for i in input:
        assert i in out[1]
    assert out[1] == output


# Forms scraper integration test
@mark.parametrize("input", [('S-1')])  # , '10-K'), ('10-Q', 'S-1', 'C')])
def test_add_forms_EDGAR(input):
    tester.reset_url()
    a = tester.add_forms(input)
    print(a[0])
    ls1, ls2, form_found = tester.edgar_scrape(100)
    # for i in input:
    #    assert i in form_found
    # t2.reset_url()
    assert input in form_found
