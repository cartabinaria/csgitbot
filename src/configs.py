import configparser
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import pkg_resources

class JWTConfig(BaseModel):
    secret_key: str
    algorithm: str
    access_token_expiration: int

class BaseConfig(BaseModel):
    port: int
    repo_owner: str
    bot_name: str
    branch_blacklist: list[str]
    github_token: str
    cpu_count: int

    # oauth attributes
    client_id: str
    client_secret: str
    redirect_uri: str

    # jwt attributes
    jwt_config: JWTConfig

config = None 

def load_env_files(keys: list[str]):
    load_dotenv(pkg_resources.resource_filename("csgitbot", ".env"))

    for key in keys:
        if os.getenv(key) is None:
            print(f"{key} not found in .env file, exiting...")
            exit(1)

def init():
    global config

    config_path = pkg_resources.resource_filename("csgitbot", "config.ini")
    config = configparser.ConfigParser()
    config.read(config_path)

    repo_owner = config["DEFAULT"]["repo_owner"]
    bot_name = config["DEFAULT"]["bot_name"]
    branch_blacklist = config["DEFAULT"]["branch_blacklist"]
    redirect_uri = config["DEFAULT"]["redirect_uri"]

    port = int(config["server"]["port"])

    load_env_files(["GITHUB_TOKEN", "CLIENT_ID", "CLIENT_SECRET", "JWT_SECRET"])
    github_token = os.getenv("GITHUB_TOKEN")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    jwt_secret = os.getenv("JWT_SECRET")

    cpu_count = os.cpu_count()
    if cpu_count is None:
        cpu_count = 1 # i hope you have at least 1 cpu :D

    jwt_config = JWTConfig(
        secret_key=jwt_secret,
        algorithm=config["jwt"]["algorithm"],
        access_token_expiration=config["jwt"]["access_token_expiration"],
    )

    config = BaseConfig(port=port,
                  bot_name=bot_name,
                  repo_owner=repo_owner,
                  branch_blacklist=branch_blacklist.split(","),
                  cpu_count=cpu_count,
                  github_token=github_token,
                  client_id=client_id,
                  client_secret=client_secret,
                  redirect_uri=redirect_uri,

                  jwt_config=jwt_config,
    )