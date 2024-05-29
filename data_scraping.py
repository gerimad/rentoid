import requests
from bs4 import BeautifulSoup
import abc
import re
from typing import List, Dict
import copy
import collections
import os
import pandas as pd
import sqlite3

Listing = collections.namedtuple('Listing', 'price location sqm extra text link')

class DataScraper(abc.ABC):
    @abc.abstractmethod
    def scrape(self) -> List[Listing]:
        raise NotImplementedError

class AlberletHuScraper(DataScraper): 
    def __init__(self, start_url: str, limit):
        self.start_url = start_url
        self.listings: List[Listing] = []
        self.limit = limit
        self.counter = 0
        self.request_header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    def scrape(self) -> List[Listing]:
        links = self.__scrape_links(limit=self.limit)
        self.listings = [self.__scrape_listing(url) for url in links]
        return copy.deepcopy(self.listings) 

    def __scrape_listing(self, url: str) -> Listing:
        response = requests.get(url, headers=self.request_header)
        if response.status_code == 200:
            html_content = response.content
        else:
            print(url)
            print(f"failed to fetch page")
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.find('div', {"id" : "details-text"}).getText()

        price = soup.find('span', {'class':'price'}).getText()
        location = soup.find('div', {'class': 'address'}).get_text(' ')
        sqm = soup.find('div', {'class': 'rooms'}).getText()

        keys = [re.sub(r'\s+', ' ', e.getText()).strip() for e in soup.find_all('div', {"class": 'advert-info-title'})]
        values = [re.sub(r'\s+', ' ', e.getText()).strip() for e in soup.find_all('div', {'class': "advert-info-text"})]

        extra = {key: value for key, value in zip(keys, values)}
        self.counter += 1
        print(f'{self.counter}: SUCCESS')
        return Listing(text=text, price=price, location=location, sqm=sqm, extra=extra, link=url)


    def __scrape_links(self, limit = 5):

        collected = []
        next_page = True
        current_page_link = self.start_url

        for _ in range(limit):
            # get the current page content
            response = requests.get(current_page_link, headers=self.request_header)
            if response.status_code == 200:
                html_content = response.content
            else:
                print(current_page_link)
                print(f"failed to fetch page")
                print(response.status_code)
                break

            soup = BeautifulSoup(html_content, 'html.parser')

            # scrape all postings into links
            links = soup.find_all('a',  {'class' : 'item owl-lazy'})
            links = [link['href'] for link in links]
            collected.extend(links)

            # check if there's a next page
            next_page = soup.find('a', {'title': 'következő'})

            if next_page:
                next_page_link = 'https://www.alberlet.hu' + next_page['href']
                current_page_link = next_page_link
            else:
                break

        return list(set(['https://www.alberlet.hu' + link for link in collected]))
    
class DataSaver(abc.ABC):   
    @abc.abstractmethod
    def saveDB(self):
        raise NotImplementedError

class CSVSaver(DataSaver):
    def __init__(self, scraper: DataScraper,
                db_path: str = "db.csv",
                columns=['price', 'location', 'sqm', 'extra', 'text', 'link']):
        self.__scraper = scraper
        self.db_path = db_path
        self.columns = columns

    def saveDB(self):
        if os.path.isfile(self.db_path):
            raise FileExistsError
        
        listings = self.__scraper.scrape()

        df = pd.DataFrame(columns=self.columns, data=listings)

        df.to_csv(self.db_path)
    
class DataCleaner(abc.ABC):
    @abc.abstractmethod
    def cleanData(self):
        raise NotImplementedError
    
class AlberletHuDataCleaner(DataCleaner):
    def __init__(self, saver: DataSaver, cleaned_path):
        self.__saver = saver
        self.__cleaned_path = cleaned_path

    def cleanData(self):
        df = pd.read_csv(self.__saver.db_path)
        df['price'] = df['price'].apply(lambda x: int(x.replace(' ', '')))
        df['rooms'] = df['sqm'].apply(lambda row: self.sqm_splitting(row)[1])
        df['sqm'] = df['sqm'].apply(lambda row: self.sqm_splitting(row)[0])

        for index, row in df.iterrows():
            import ast
            extras = ast.literal_eval(row['extra'])
            for k, v in extras.items():
                df.loc[index, k] = v

        #df[self.__saver.columns].to_csv(self.__cleaned_path)

        conn = sqlite3.connect(f'{self.__cleaned_path}.sqlite')

        df[self.__saver.columns].to_sql('flats', conn, if_exists='replace', index=False )
        

        
    @staticmethod
    def sqm_splitting(s):
        parts = s.split(',')
        assert len(parts) == 2

        rooms = parts[0]
        sqm = parts[1]

        assert 'm2' in sqm
        assert 'szoba' in rooms

        import re
        sqm_pattern = r'\b\d+\b'
        true_sqm = int(re.findall(sqm_pattern, sqm)[0])

        szoba_pattern = r'(\b\d+)\s*szoba'
        szoba_count = int(re.findall(szoba_pattern, rooms)[0])

        felszoba_count = 0
        if 'félszoba' in rooms:
            felszoba_pattern = r'(\b\d+)\s*félszoba'
            felszoba_count = int(re.findall(felszoba_pattern, rooms)[0])
        
        true_rooms = szoba_count  + 0.5 * felszoba_count

        return true_sqm, true_rooms
    
if __name__ == "__main__":
    print('xd')
    scraper = AlberletHuScraper(start_url='https://www.alberlet.hu/kiado_alberlet/ingatlan-tipus:lakas/megye:budapest/keres:normal/limit:24', limit=5)
    saver = CSVSaver(scraper=scraper, db_path='testing.csv')
    saver.saveDB()
    cleaner = AlberletHuDataCleaner(saver, 'testing_cleaned').cleanData()
