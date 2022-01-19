import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_senators(n_th_congress):
    wiki_url = f"https://en.wikipedia.org/wiki/List_of_United_States_senators_in_the_{n_th_congress}th_Congress"
    df = pd.DataFrame({
            'first_name': [],
            'last_name': [],
           })

    r = requests.get(wiki_url)

    html = r.text
    bs = BeautifulSoup(html, "html.parser")

    tbody = bs.find('tbody')
    trs = tbody.find_all('tr')
    for tr in trs:
        td = tr.find('td')
        if td is not None:
            name = td.text
            first_name, last_name = name.split(' ')[0].replace('\n', '').split('[')[0], name.split(' ')[-1].replace('\n', '').split('[')[0]
            df.loc[len(df.index)] = [first_name, last_name]
        # name = td.data_sort_value
        pass
    return df


if __name__ == "__main__":
    df = get_senators(n_th_congress=116)
    pass
