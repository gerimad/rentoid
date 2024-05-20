from typing import List, Dict
import abc
import sqlite3
from scraping import DataScraper
import pandas as pd
import os

class DataSaver(abc.ABC):   
    @abc.abstractmethod
    def saveDB(self):
        raise NotImplementedError

#FIXME add link and extras fix
class SQLSaver(DataSaver):
    def __init__(self, scraper: DataScraper, db_path: str = "dbase1"):
        self.__scraper = scraper
        self.__db_path = db_path
    
    def saveDB(self):
        if os.path.isfile(self.__db_path): 
            raise FileExistsError

        conn = sqlite3.connect(self.__db_path)
        tblcmd = 'create table listings (price int, location char(40), sqm int, extra char(2048), text char(2048))'
        conn.execute(tblcmd)

        listings = self.__scraper.scrape()
        curs = conn.cursor()

        for listing in listings:
            curs.execute('insert into listings values (?, ?, ?, ?, ?, ?)', listing)

        conn.commit()


class CSVSaver(DataSaver):
    def __init__(self, scraper: DataScraper, db_path: str = "db.csv"):
        self.__scraper = scraper
        self.__db_path = db_path

    def saveDB(self):
        if os.path.isfile(self.__db_path):
            raise FileExistsError
        
        listings = self.__scraper.scrape()

        df = pd.DataFrame(columns=['price', 'location', 'sqm', 'extra', 'text', 'link'], data=listings)

        df.to_csv(self.__db_path)
