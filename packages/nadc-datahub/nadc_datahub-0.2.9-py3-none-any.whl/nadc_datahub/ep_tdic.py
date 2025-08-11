import logging
import os
from typing import Dict,Optional
import requests
from nadc_datahub.dataset import DataSet
import csdb
import csdb.api_base
from csdb import product
from unittest import mock

TDIC_URL = "https://ep.bao.ac.cn/ep"
CSDB_URL = "http://123.56.102.90:31502"
class EP_TDIC(DataSet):
    # additional methods specific to EP_TDIC dataset
    def auth(self, username="", password="", token=""):
        return super().auth(username, password, token)
    
    def authorized(self):
        return super().authorized()
    
    @classmethod
    def get_entry(cls, entry:str):
        return EP_TDIC_CSDB()

    @classmethod
    def get_datatypes(cls):
        return super().get_datatypes()
    
    
class EP_TDIC_API(EP_TDIC):
    tdic_token = ""
    csdb_token = ""
    def auth(self, username="", password="", token=""):
        try:
            resp = requests.post(f"{TDIC_URL}/api/v1/get_tokenp",data = {'email': username, 'password': password})
            token = resp.json()['token']
            self.tdic_token = token
        except Exception:
            logging.error("Failed to authenticate",stack_info=True)
    
    def authorized(self):
        resp = requests.post(f"{TDIC_URL}/data_center/api/wxt_obs_data/",data={'token':self.tdic_token,"obs_id":"08500000058"})
        if "error" in resp.json() :
            logging.error(f"Failed to authenticate: {resp.json()['error']}")
            return False
        return True
    
class EP_TDIC_CSDB(EP_TDIC):
    tdic_token = ""
    csdb_token = ""
    def auth(self, username="", password="", token=""):
        try:
            resp = requests.post(f"{TDIC_URL}/api/get_tokenp",json= {'email': username, 'password': password})
            token = resp.json()['token']
            self.tdic_token = token
            resp = requests.post(f"{TDIC_URL}/data_center/get_csdb_token", headers={"tdic-token": token},  
            data={"token":token})
            token = resp.json()['token']
            self.csdb_token = token
        except Exception as e:
            logging.error("Failed to authenticate",e,stack_info=True)
        
        # self.csdb_token = 'eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ6aGFuZ3poZW4iLCJ1c2VySWQiOiI3NjIiLCJuYW1lIjoi5byg6ZyHIiwiZXhwIjoxNzEzNDk0NDEyfQ.ALgSlXfc3sWk5FbuhCpn-dJ_hQ0vIke9Lqap616gppLzU8XVYks1AbC8_aLPbf_l1c-guqXEaoroU5yKOpp87wH7GDSe62YbQS2LcgeA74CG-q7IiceyOsaNZnS2haBtLa2g6zDBpELaVcTmReIqgCXgpUmSE3fmhqeGu_ZLnRw'
    
    def authorized(self):
        resp =  requests.get(f"{CSDB_URL}/user/auth/verify?token={self.csdb_token}")
        return resp.status_code==200

    def download(self, output, datatype, metadatas: Dict)->Optional[str]:
        
        # mock csdb.session.get_current_config，使其返回当前 self.csdb_token
        mock_config = {
            "config_name": "mock",
            "url": CSDB_URL,
            "username": "",
            "password": "",
        }
        patcher = mock.patch("csdb.session.get_current_config", return_value=mock_config)
        patcher.start()
        token_bak = csdb.api_base._auth["token"] = self.csdb_token
        
        search_result = product.adsearch(datatype,[{"co":"=","name":k,"value":v} for k,v in metadatas.items()])
        if len(search_result)==0:
            logging.warning(f"No data found for {datatype} with {metadatas}")
            return None
        if len(search_result)>1:
            logging.warning(f"Multiple data found for {datatype} with {metadatas}. Download the latest one.")
        
        output_file = os.path.join(output, search_result[0]['fileName'])
        product.download(search_result[0]['urn'],output_file)
        patcher.stop()
        csdb.api_base._auth["token"] = token_bak
        return output_file
        
    
    

