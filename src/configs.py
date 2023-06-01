import configparser
from pydantic import BaseModel
from dotenv import load_dotenv
import os

class Data(BaseModel):
    port: int
    repo_owner: str
    token: str

config = None 

def init():
    global config

    config = configparser.ConfigParser()
    config.read("config.ini")

    repo_owner = config["DEFAULT"]["repo_owner"]
    port = int(config["server"]["port"])

    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")

    config = Data(port=port, repo_owner=repo_owner, token=token)