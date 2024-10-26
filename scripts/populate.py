"""Script used to populate the repos repository with the data from the repos.json file"""
from pydantic import BaseModel
import dotenv
import os
import git

dotenv.load_dotenv()
github_token = os.getenv("GITHUB_TOKEN")

BASE = f"https://cartabinaria-access:{github_token}@github.com/cartabinaria/"

class TeachingsList(BaseModel):
    mandatory: list[str]
    elective: list[str] | None

class YearModel(BaseModel):
    year: int
    chat: str | None
    teachings: TeachingsList

class RepoJson(BaseModel):
    id: str
    name: str
    icon: str
    years: list[YearModel] | None

def get_main_json():
    url = "https://github.com/cartabinaria/config/raw/main/degrees.json"

    import requests
    response = requests.get(url)
    return response.json()

def download_repo(reponames: list[str]):
    for reponame in reponames:
        try:
            print(f"Cloning {reponame}")
            git.Repo.clone_from(f"{BASE}{reponame}.git", f"repos/{reponame}")
        except git.exc.GitCommandError as e:
            print(e)


def get_repo_json():
    jsons = get_main_json()
    for json in jsons:
        repo_el = RepoJson(**json)
        if repo_el.years:
            for year in repo_el.years:
                if year.teachings.elective:
                    download_repo(year.teachings.elective)
                download_repo(year.teachings.mandatory)

    # repo_list: list[RepoJson] = [RepoJson(x) for x in jsons]
    # print(repo_list)

if __name__ == "__main__":
    get_repo_json()

    # download_repos(["test"])
