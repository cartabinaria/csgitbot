import configparser
from pydantic import BaseModel
from dotenv import load_dotenv
import os

class BaseConfig(BaseModel):
    port: int
    repo_owner: str
    bot_name: str
    branch_blacklist: list[str]
    github_token: str
    cpu_count: int

config = None 

def init():
    global config

    config = configparser.ConfigParser()
    config.read("config.ini")

    repo_owner = config["DEFAULT"]["repo_owner"]
    bot_name = config["DEFAULT"]["bot_name"]
    branch_blacklist = config["DEFAULT"]["branch_blacklist"]

    port = int(config["server"]["port"])

    load_dotenv(".env")
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token is None:
        print("GITHUB_TOKEN not found in .env file, exiting...")
        exit(1)

    cpu_count = os.cpu_count()
    if cpu_count is None:
        cpu_count = 1 # i hope you have at least 1 cpu :D

    print(cpu_count)
    
    config = BaseConfig(port=port, 
                  bot_name=bot_name,
                  repo_owner=repo_owner, 
                  branch_blacklist=branch_blacklist.split(","),
                  cpu_count=cpu_count,
                  github_token=github_token)