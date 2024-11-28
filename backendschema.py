from pydantic import BaseModel

class TakeAttedenceInput(BaseModel):
    dep:str
    sem:str
    presents:dict

class DownloadInput(BaseModel):
    data:dict
    