from typing import Dict, List, TypedDict, Literal
from nadc_datahub.dataset import DataSet
import requests
import os

class Metadata(TypedDict):
    dataset_name: str
    ra: float
    dec: float
    fov: float
    width: int
    height: int

class ImageCutout(DataSet):
    
    def __init__(self):
        self.token = ""
    def auth(self, username="", password="", token=""):
        self.token = token
    
    def authorized(self):
        return True
    
    def get_datatypes(self):
        return [
            'PNG',
            'FITS'
        ]
    
    def download(self, output, datatype: Literal['PNG','FITS'], metadatas: Metadata):
        
        """下载HiPS数据集的图片
        Args:
            output (str): 输出文件
            datatype (str):  PNG/FITS
            metadatas (Dict): 
                ra (float): 赤经
                dec (float): 赤纬
                fov (float): 视场
                width (int): 宽度
                height (int): 高度

        Raises:
            Exception: 下载失败

        Returns:
            _type_: _description_
        """
        
        # Construct URL with metadata parameters
        base_url = "https://hips.china-vo.org/generate"
        params = {
            "dataset_name": metadatas.get("dataset_name", ""),
            "format": datatype,
            "ra": metadatas.get("ra", ""),
            "dec": metadatas.get("dec", ""),
            "fov": metadatas.get("fov", ""),
            "width": metadatas.get("width", ""),
            "height": metadatas.get("height", "")
        }
        
        # Make request
        response = requests.get(base_url, params=params, headers={"hips-token": self.token})
        
        if response.status_code != 200 or response.json().get("success")!="ok":
            raise Exception(f"Failed to download image: {response.status_code}")
        image_path = response.json().get("image_path")
        if not image_path:
            raise Exception(f"Failed to download image: {response.status_code}")
        
        # Download image content
        img_response = requests.get(image_path, headers={"hips-token": self.token})
        if img_response.status_code != 200:
            raise Exception(f"Failed to download image content: {img_response.status_code}")
        image_content = img_response.content
        
        # Save to output file
        
        with open(output, "wb") as f:
            f.write(image_content)
            
        return output
    
    def get_datasets(self)->List[str]:
        url = 'https://hips.china-vo.org/generate/list-dataset'
        resp = requests.get(url)
        return resp.json()
        
    