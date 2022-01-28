import psycopg2
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
from dateutil import parser
from lobbyview.db import PostgresqlManager
import pandas as pd


def scrape_one_periodoc_transaction_page(url):
    print(url)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("detach", True)
    # for memory save
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-application-cache')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--disable-dev-shm-usage")
    ##

    from lobbyview.db import PostgresqlManager

    driver = webdriver.Chrome(
        ChromeDriverManager().install(), chrome_options=chrome_options
    )
    starting_url = "https://efdsearch.senate.gov/search/home/"
    driver.get(starting_url)

    # check the input box
    inputElement = driver.find_element_by_id("agree_statement").click()
    driver.get(url)

    df = pd.DataFrame(
        {
            "transaction_date": [],
            "owner": [],
            "ticker": [],
            "ticker_url": [],
            "asset_name": [],
            "asset_type": [],
            "type": [],
            "amount": [],
        }
    )

    sql_insert_client_name_and_url = """
    INSERT INTO financial_disclosures.senate_periodic_transaction_report(transaction_date, owner, ticker, ticker_url, asset_name, asset_type, type, amount)
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
    """

    html = driver.page_source
    bs = BeautifulSoup(html, "html.parser")
    table = bs.find("table")
    if table is not None:
        trs = table.find_all("tr")
        for tr in trs:
            tds = tr.find_all("td")
            if len(tds) > 0:
                print(tds)

                def _parse_ticker_asset_name(text):
                    return text.replace("\n", "").strip()

                transaction_date = parser.parse(tds[1].text)
                owner = tds[2].text
                ticker = _parse_ticker_asset_name(tds[3].text)
                try:
                    ticker_url = tds[3].find("a")["href"]
                except TypeError:
                    ticker_url = ""
                asset_name = _parse_ticker_asset_name(tds[4].text)
                asset_type = tds[5].text
                type = tds[6].text

                def _parse_amount(text):
                    min, max = text.split("-")
                    min = int(min.replace("$", "").replace(",", "")) - 1
                    max = int(max.replace("$", "").replace(",", ""))
                    return f"({min},{max})"

                amount = _parse_amount(tds[7].text)

                df.loc[len(df.index)] = [
                    transaction_date,
                    owner,
                    ticker,
                    ticker_url,
                    asset_name,
                    asset_type,
                    type,
                    amount,
                ]
                pm = PostgresqlManager(
                    dotenv_path="/Users/syyun/financial-disclosure/.env"
                )
                try:
                    pm.execute_sql(
                        sql=sql_insert_client_name_and_url,
                        parameters=(
                            transaction_date,
                            owner,
                            ticker,
                            ticker_url,
                            asset_name,
                            asset_type,
                            type,
                            amount,
                        ),
                        commit=True,
                    )
                except psycopg2.errors.UniqueViolation:
                    pass
                pass
            else:
                pass
    driver.close()
    driver.quit()


if __name__ == "__main__":
    sql_select_periodic_record_url_to_scrape = """
    select report_type_url from financial_disclosures.senate s
where report_type ilike 'Period%'
order by date_received desc    
    """
    pm = PostgresqlManager()
    data = pm.execute_sql(
        sql=sql_select_periodic_record_url_to_scrape, fetchall=True, commit=False
    )
    df = pm.convert_fetchall_to_pd(data)
    print(df)
    df.rename(columns={0: "report_type_url"}, inplace=True)
    index = df.index[df['report_type_url'] == 'https://efdsearch.senate.gov//search/view/ptr/21f72e24-9365-46e8-8cfc-c5a5a2a4ca99/'].tolist()
    print(index)
    for idx, row in enumerate(df.itertuples()):
        if idx >= index[0]:
            scrape_one_periodoc_transaction_page(row.report_type_url)
    pass
