import psycopg2
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
from dateutil import parser
from lobbyview.db import PostgresqlManager


def scrape_one_page(df, driver):
    sql_insert_client_name_and_url = """
    INSERT INTO financial_disclosures.senate(first_name, last_name, office, report_type, report_type_url, date_received)
    VALUES(%s, %s, %s, %s, %s, %s)
    """

    url_prefix = "https://efdsearch.senate.gov/"
    import time

    time.sleep(0.5)
    html = driver.page_source
    bs = BeautifulSoup(html, "html.parser")
    table = bs.find("table", {"id": "filedReports"})
    trs = table.find_all("tr")
    for tr in trs:
        tds = tr.find_all("td")
        if len(tds) > 1:
            first_name = tds[0].text
            last_name = tds[1].text
            office = tds[2].text
            report_type = tds[3].text
            report_type_url = tds[3].find("a")["href"]
            date_received = parser.parse(tds[4].text)
            df.loc[len(df.index)] = [
                first_name,
                last_name,
                office,
                report_type,
                url_prefix + report_type_url,
                date_received,
            ]
            pm = PostgresqlManager(dotenv_path="/Users/syyun/financial-disclosure/.env")
            try:
                pm.execute_sql(
                    sql=sql_insert_client_name_and_url,
                    parameters=(
                        first_name,
                        last_name,
                        office,
                        report_type,
                        url_prefix + report_type_url,
                        date_received,
                    ),
                    commit=True,
                )
                print("insert", (
                        first_name,
                        last_name,
                        office,
                        report_type,
                        url_prefix + report_type_url,
                        date_received,
                    ))
            except psycopg2.errors.UniqueViolation:
                pass
            pass
        else:
            pass
    try:
        next_btn = driver.find_elements_by_css_selector(".paginate_button.next")[0]
    except IndexError:
        next_btn = None

    next_btn_disabled = driver.find_elements_by_css_selector(
        ".paginate_button.next.disabled"
    )
    if len(next_btn_disabled) > 0:
        next_btn = None

    return next_btn


def scrape_insert_one_legislator(first_name, last_name):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    global browser  # this will prevent the browser variable from being garbage collected
    from lobbyview.db import PostgresqlManager

    url = "https://efdsearch.senate.gov/search/"
    driver = webdriver.Chrome(
        ChromeDriverManager().install(), chrome_options=chrome_options
    )
    driver.get(url)

    # check the input box
    inputElement = driver.find_element_by_id("agree_statement").click()
    # this will automatically let the page turn into serach
    inputElement = driver.find_element_by_id("firstName").send_keys(first_name)
    inputElement = driver.find_element_by_id("lastName").send_keys(last_name)

    driver.find_element_by_css_selector(".btn.btn-primary").click()

    import pandas as pd

    df = pd.DataFrame(
        {
            "firstname": [],
            "last_name": [],
            "office": [],
            "report_type": [],
            "report_type_url": [],
            "date_received": [],
        }
    )

    next_btn = True
    while next_btn:
        next_btn = scrape_one_page(df, driver)
        if next_btn:
            next_btn.click()
    driver.close()


if __name__ == "__main__":
    from get_legislators import get_senators
    congress = 117
    list_of_senators_df = get_senators(n_th_congress=congress)

    for row in list_of_senators_df.itertuples():
        print(row.first_name, row.last_name)
        scrape_insert_one_legislator(row.first_name,  row.last_name)
    pass
