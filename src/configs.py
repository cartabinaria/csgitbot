import configparser
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import pkg_resources
from typing import Literal

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
    environment: Literal["development", "production"]
    key_path: str
    is_github_app: bool = False

    # oauth attributes
    client_id: str
    client_secret: str
    redirect_uri: str
    app_id: str

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
    # TODO: refactorare, .ini è meglio che sia json così pydantic fa in automatico

    global config

    config_path = pkg_resources.resource_filename("csgitbot", "config.ini")
    config = configparser.ConfigParser()
    config.read(config_path)

    repo_owner = config["DEFAULT"]["repo_owner"]
    bot_name = config["DEFAULT"]["bot_name"]
    branch_blacklist = config["DEFAULT"]["branch_blacklist"]
    redirect_uri = config["DEFAULT"]["redirect_uri"]
    environment = config["DEFAULT"]["environment"]
    key_path = config["server"]["key_path"]
    port = int(config["server"]["port"])
    is_github_app = config["server"].getboolean("is_github_app")

    load_env_files(["GITHUB_TOKEN", "CLIENT_ID", "CLIENT_SECRET", "JWT_SECRET", "GITHUB_APP_ID"])
    github_token = os.getenv("GITHUB_TOKEN")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    jwt_secret = os.getenv("JWT_SECRET")
    app_id = os.getenv("GITHUB_APP_ID")

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
                  environment=environment,
                  key_path=key_path,
                  is_github_app=is_github_app,

                  github_token=github_token,
                  client_id=client_id,
                  client_secret=client_secret,
                  redirect_uri=redirect_uri,
                  app_id=app_id,

                  jwt_config=jwt_config,
    )