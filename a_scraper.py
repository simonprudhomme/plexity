import numpy as np
import pandas as pd
from selenium import webdriver
from tqdm import tqdm
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from datetime import date, timedelta
import json, os, re, time, unicodedata, requests
import os


# 1. functions
def get_urls():
    #chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Run Selenium in background
    #chrome_options.add_experimental_option("prefs", {"profile.default_content_settings.cookies": 2})
    #driver = webdriver.Chrome()#options=chrome_options)

    from selenium import webdriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1420,1080')
    chrome_options.add_argument('--headless') # uncomment
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_experimental_option("prefs", {"profile.default_content_settings.cookies": 2})
    driver = webdriver.Chrome(options=chrome_options)

    # Open Plexes WebPage
    plex_urls = 'https://www.centris.ca/fr/plex~a-vendre?view=Thumbnail'
    driver.get(plex_urls)
    time.sleep(5)

    # Get Total Number of Pages to Loop On
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    number_pages = soup.find('li', {'class': 'pager-current'})
    total_pages = number_pages.text.split('/')[1].strip()
    print('Number of pages to loop on :',total_pages)

    folder = 'json_files'
    if not os.path.exists(folder):
        os.makedirs(folder)
        print("Directory ", folder, " Created ")
    else:
        print("Directory ", folder, " already exists")

    # Get Plexes Urls on Each Page
    links_total = []
    print('Getting urls...')
    for page in tqdm(range(int(total_pages) +1)):
        soup = BeautifulSoup(driver.page_source, parse_only=SoupStrainer('a')) #TODO: fix this code !
        links = []
        for link in soup:
            if link.has_attr('href'):
                links.append(link['href'])
        links = list(set(links))
        links = [i for i in links if 'plex' in i]

        # Saved Urls in links_total
        links_total = links_total + links

        # Go on Next Page
        driver.find_element_by_xpath('/html/body/main/div[6]/div/div/div[1]/div/div/ul/li[4]/a').click()
        time.sleep(2)

    urls_today = pd.DataFrame(links_total, columns={'urls'})
    urls_today = urls_today.drop_duplicates()
    urls_today.to_csv('urls_today.csv', index=False)
    urls_today['date'] = str(date.today())

    urls_yesterday = pd.read_csv('urls_yesterday.csv')

    urls_to_get = pd.DataFrame(list(set(urls_yesterday['urls']) - set(urls_today['urls'])), columns={'urls'})
    urls_to_get.to_csv('urls_to_get.csv', index=False)

    urls_yesterday = pd.concat([urls_to_get,urls_yesterday],axis=0).reset_index()
    urls_yesterday.to_csv('urls_yesterday.csv',index=False)

    driver.quit()
    return


def unicode(text):
    '''
    Unicode Normalizer
    '''
    text_clear = unicodedata.normalize("NFKD", text)
    return text_clear


def get_data(url):
    """
    Get Plex data
    URL : Plex url on www.centris.ca/fr
    """

    time.sleep(1)
    print(url)
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        titles = soup.find_all('div', {'class': 'carac-title'})
        values = soup.find_all('div', {'class': 'carac-value'})

        # Create dictionnary to store information
        data = {}

        data['building_type'] = unicode(soup.find('h1', {'itemprop': 'category'}).text.strip())
        data['adresse'] = soup.find('h2', {'itemprop': 'address'}).text
        data['url'] = url

        mls = re.sub("[^0-9]", "", unicode(soup.find('span', {'class': 'mls'}).text.strip()))
        data['mls_number'] = mls

        for a, b in zip(titles, values):
            data[unicode(a.text)] = unicode(b.text)
        try:
            data['description'] = soup.find('div', {'itemprop': 'description'}).text.strip()
        except Exception:
            data['description'] = None
        try:
            data['price'] = soup.find('span', {'itemprop': 'price'}).text.strip()
        except Exception:
            data['description'] = None

        with open('json_files' + '/' + str(mls) + '.json', 'w') as fp:
            json.dump(data, fp)
    except Exception as e:
        pass
    return


def run_get_data():
    urls = pd.read_csv('urls_to_get.csv')

    print(urls.shape)
    urls = urls.drop_duplicates()
    urls['urls'] = 'https://www.centris.ca' + urls['urls']
    to_delete = ['/fr/plex~a-vendre?view=Thumbnail', '/fr/plex~a-vendre?view=Map', '/en/plexes~for-sale?view=Thumbnail',
        '/en/plexes~for-sale?view=Map', '/fr/plex~a-vendre?view=Map&geolocalization=enabled']
    urls = urls[~urls['urls'].isin(to_delete)]
    print('Getting Plexs information as JSON...')

    for url in tqdm(urls['urls']):
        get_data(url)
    return


def get_json_file():
    print('Merge JSON in a CSV File...')
    folder = 'json_files'
    json_files_list = [pos_json for pos_json in os.listdir(folder) if pos_json.endswith('.json')]
    print(len(json_files_list))

    # Define the Dataframe with the columns used
    jsons_data = pd.DataFrame(columns=['utilisation', 'style', 'annee', 'superficie_terrain', 'superficie_batiment', 'stationnement','unitees', 'unitee_res', 'revenus', 'building_type', 'autres', 'adresse', 'description', 'url', 'mls_number', 'price'])

    # Check if key exist in the JSON
    def check_value(x, json_text_file):
        if x in json_text_file:
            return json_text_file[x]
        else:
            return None

    # Gather data in the JSON, we need both the json and an index number so use enumerate()
    for index, js in tqdm(enumerate(json_files_list)):
        with open(os.path.join(folder, js)) as json_file:
            json_text = json.load(json_file)

            utilisation = check_value('Utilisation de la propriété', json_text)
            style = check_value('Style de bâtiment', json_text)
            annee = check_value('Année de construction', json_text)
            superficie_terrain = check_value('Superficie du terrain', json_text)
            superficie_batiment = check_value('Superficie du bâtiment (au sol)', json_text)
            stationnement = check_value('Stationnement total', json_text)
            unitees = check_value('Nombre d’unités', json_text)
            unitee_res = check_value('\r\nUnités résidentielles                ', json_text)
            revenus = check_value('Revenus bruts potentiels', json_text)
            building_type = check_value('building_type', json_text)
            autres = check_value('Caractéristiques additionnelles', json_text)
            adresse = check_value('adresse', json_text)
            description = check_value('description', json_text)
            url = check_value('url', json_text)
            mls_number = check_value('mls_number', json_text)
            price = check_value('price', json_text)

            jsons_data.loc[index] = [utilisation, style, annee, superficie_terrain, superficie_batiment, stationnement,
                unitees, unitee_res, revenus, building_type, autres, adresse, description, url, mls_number, price]

    jsons_data = jsons_data.drop_duplicates()
    jsons_data.to_csv('plex.csv', index=False)

# 2. main_scraper
def main_scraper():
    get_urls()
    run_get_data()
    get_json_file()
    return

# 3. run main_scraper
if __name__ == '__main__':
    main_scraper()
