from typing import Optional
from fastapi import UploadFile
from .logs import logging
from .configs import BaseConfig
from .github_utils import GithubUtils, GithubUser

    
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
            author = GithubUser(user=username, email=email)

        if not self.github_client.branch_exists(branch_name):
            self.github_client.create_branch(branch_name)

        self.github_client.create_file(branch_name, file.filename, await file.read(), author)
        self.github_client.create_pr(branch_name, "main", title=pr_title)
