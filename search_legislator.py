from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
global browser  # this will prevent the browser variable from being garbage collected

url = "https://efdsearch.senate.gov/search/"
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
driver.get(url)

# check the input box
inputElement = driver.find_element_by_id("agree_statement").click()

from get_legislators import get_senators

congress = 117
list_of_senators = get_senators(n_th_congress=congress)

# for index, row in list_of_senators.iterrows():
#     first_name = row['first_name']
#     last_name = row['last_name']

first_name = 'David'
last_name = 'Perdue'

# this will automatically let the page turn into serach
inputElement = driver.find_element_by_id('firstName').send_keys(first_name)
inputElement = driver.find_element_by_id('lastName').send_keys(last_name)

driver.find_element_by_css_selector('.btn.btn-primary').click()

import pandas as pd
df = pd.DataFrame({
    'firstname': [],
    'last_name': [],
    'periodic_transaction':[]
})


def scrape_one_page(df, driver):
    import time
    time.sleep(0.5)
    html = driver.page_source
    bs = BeautifulSoup(html, "html.parser")
    table = bs.find("table", {"id":"filedReports"})
    trs = table.find_all("tr")
    for tr in trs:
        tr.find
    hrefs = bs.find_all("a")
    url_prefix = "https://efdsearch.senate.gov/"
    for href in hrefs:
        if 'Periodic' in href.text:
            df.loc[len(df.index)] = [first_name, last_name, url_prefix + href['href']]

    next_btn = driver.find_elements_by_css_selector('.paginate_button.next')[0]
    next_btn_disabled = driver.find_elements_by_css_selector('.paginate_button.next.disabled')
    if len(next_btn_disabled) > 0:
        next_btn = None
    return next_btn


if __name__ == "__main__":
    next_btn = True
    while next_btn:
        next_btn = scrape_one_page(df, driver)
        if next_btn:
            next_btn.click()
    pass