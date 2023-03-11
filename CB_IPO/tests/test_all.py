from CB_IPO import (
    set_page,
    set_search_date,
    edgar_scrape,
    generate_df,
    # get_ipo,
    # search_CB,
    # add_CB,
    reset_url,
    add_forms,
)
from pytest import mark
import pandas as pd


@mark.parametrize(
    "input,output",
    [
        (5, "https://www.sec.gov/edgar/search/#/filter_forms=S-1&page=5"),
        (4, "https://www.sec.gov/edgar/search/#/filter_forms=S-1&page=4"),
    ],
)
def test_page_set(input, output):
    reset_url()
    assert set_page(input) == output


@mark.parametrize(
    "in_d1,in_d2,output",
    [
        (
            '2014-03-04',
            '2015-03-04',
            "https://www.sec.gov/edgar/search/#/dateRange=custom&category=custom&startdt=2014-03-04&enddt=2015-03-04&filter_forms=S-1",
        ),
        (
            '2012-04-23',
            '2022-04-23',
            "https://www.sec.gov/edgar/search/#/dateRange=custom&category=custom&startdt=2012-04-23&enddt=2022-04-23&filter_forms=S-1",
        ),
    ],
)
def test_page_date(in_d1, in_d2, output):
    assert set_search_date(in_d1, in_d2) == output


@mark.parametrize(
    "input, output",
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
        )
    ],
)
def test_scraper(input, output):
    reset_url()
    set_search_date('2023-03-01', '2023-03-03')
    ns, ds, forms = edgar_scrape(input)
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
    "input, df_out", [([4, 1], test_d)],
)
def test_dfgen(input, df_out):
    reset_url()
    set_search_date('2023-03-01', '2023-03-03')
    a1, a2 = input

    outdf = pd.DataFrame(data=df_out)

    assert generate_df(a1, a2).equals(outdf)


@mark.parametrize("input,output", [(('S-B', '10-K'), 'S-B%252C10-K'), (('10-Q', 'S-B', 'C'), '10-Q%252CS-B%252CC')])
def test_add_forms(input, output):
    reset_url()
    out = add_forms(input)
    for i in input:
        assert i in out[1]
    assert out[1] == output


# Forms scraper integration test
@mark.parametrize("input", [('S-1')])  # , '10-K'), ('10-Q', 'S-1', 'C')])
def test_add_forms_EDGAR(input):
    reset_url()
    a = add_forms(input)
    print(a[0])
    ls1, ls2, form_found = edgar_scrape(100)
    # for i in forms:
    # assert i in input
    reset_url()
    for og in input:
        assert og in form_found
