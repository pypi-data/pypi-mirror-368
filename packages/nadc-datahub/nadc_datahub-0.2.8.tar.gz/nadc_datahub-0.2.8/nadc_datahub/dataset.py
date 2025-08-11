from typing import Dict
from dataclasses import dataclass
from abc import ABC, abstractmethod

class DataSet(ABC):
    @abstractmethod
    def auth(self, username="", password="", token=""):
        # code for authentication
        raise NotImplementedError()

    @abstractmethod
    def download(self,output, datatype, metadatas: Dict):
        # code for downloading data
        raise NotImplementedError()

    @abstractmethod
    def authorized(self):
        # code for checking authentication
        raise NotImplementedError()
    
    @abstractmethod
    def get_datatypes(self):
        # code for getting datatypes
        raise NotImplementedError()
    
@dataclass
class DataType:
    name: str
    description: str
    metadatas: Dict

