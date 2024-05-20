import abc
import os
import sqlite3
from typing import Dict ,Union, List

class DataLoader(abc.ABC):
    @abc.abstractmethod
    def loadDB(self):
        raise NotImplementedError
    
class SQLLoader(DataLoader):
    def __init__(self, db_path: str):
        if not os.path.isfile(db_path):
            raise FileNotFoundError

        self.__db_path = db_path
        self.__conn = sqlite3.connect(self.__db_path)

    def loadDB(self) -> List[Dict[str, Union[int, str]]]:
        curs = self.__conn.cursor()
        curs.execute('select * from listings')
        colnames = [desc[0] for desc in curs.description]
        rowdicts = [dict(zip(colnames, row)) for row in curs.fetchall()]
        return rowdicts
        
    
        


