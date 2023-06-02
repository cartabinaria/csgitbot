from typing import Optional
from fastapi import UploadFile
from .configs import BaseConfig
from .github_utils import GithubUtils, GithubUser
import uuid
import multiprocessing
import datetime
    
class MainService():
    def __init__(self, github_token: str, repo_owner: str, config: BaseConfig):
        self.github_client = GithubUtils(github_token, repo_owner)
        self.config = config

    async def upload_and_pr(
        self,
        reponame: str, 
        branch_name: str, 
        file: UploadFile,
        username: Optional[str] = None,
        email: Optional[str] = None,
        pr_title: Optional[str] = None
    ):
        assert isinstance(self.github_client, GithubUtils), "github client is not initialized"
        assert isinstance(self.config, BaseConfig), "config is not initialized"

        if not self.github_client.set_repo(reponame):
            raise Exception(error="repo not found")
        elif branch_name in self.config.branch_blacklist:
            raise Exception(error="branch is blacklisted, cannot modify")

        author = None
        if username is not None and email is not None:
            author = GithubUser(user=username, email=email, date=datetime.datetime.now())

        if not self.github_client.branch_exists(branch_name):
            self.github_client.create_branch(branch_name)

        self.github_client.create_file(branch_name, file.filename, await file.read(), author)
        self.github_client.create_pr(branch_name, "main", title=pr_title)

    def generate_branch_name(self):
        return str(uuid.uuid4())
    
    def get_branches(self, reponame: str):
        if not self.github_client.set_repo(reponame):
            raise Exception(error="repo not found")
        
        return self.github_client.repo.get_branches()

    def delete_all_branches(self, reponame: str):
        if not self.github_client.set_repo(reponame):
            raise Exception(error="repo not found")
        
        branches = self.github_client.get_all_branches()
        branches = list(
                filter(lambda branch_name: branch_name not in self.config.branch_blacklist, 
                   map(lambda branch: branch.name, branches))
                )
        
        if len(branches) > 0:
            pool = multiprocessing.Pool(processes=min(self.config.cpu_count, len(branches)))
            pool.map(self.github_client.delete_branch, branches)

            pool.close()
            pool.join()
