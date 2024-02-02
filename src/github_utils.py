from pydantic import BaseModel
from github import Github, Repository
import github
import datetime
from typing import Optional
from .logs import logging
from . import configs

logger = logging.getLogger("service")

class GithubUser(BaseModel):
    user: str
    email: str    
    date: datetime.datetime

    def to_input_git_author(self) -> github.InputGitAuthor:
        return github.InputGitAuthor(
            name=self.user,
            email=self.email,
            date=self.date.isoformat()
        )

class GithubUtils():
    github: Github
    repo: Repository.Repository
    repo_owner: str

    def __init__(self, github_token: str, repo_owner: str):
        self.github = Github(github_token)
        self.repo_owner = repo_owner

    def set_repo(self, repo_name: str) -> bool:
        """
        Check if the repo exists
        """
        try:
            logger.info(f"Checking repo: {self.repo_owner}/{repo_name}")
            self.repo = self.github.get_repo(f"{self.repo_owner}/{repo_name}")
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            return False
        
        return True

    def generate_branch_name(self) -> str:
        """
        Generate a new branch name as uuid
        """
    
    def create_branch(self, branch_name: str, base_branch: str = "main"):
        """
        Create a new branch
        """
        logger.info(f"Creating branch: {branch_name} on repo: {self.repo.name}")
        base_branch = self.repo.get_branch(base_branch)
        self.repo.create_git_ref(f"refs/heads/{branch_name}", base_branch.commit.sha)
    
    def branch_exists(self, branch_name: str) -> bool:
        """
        Get a branch
        """
        logger.info(f"Checking branch: '{branch_name}' on repo: '{self.repo.name}'")

        try:
            self.repo.get_branch(branch_name)
        except github.GithubException as e:
            if e.status == 404:
                return False
            raise e
        
        return True

    def create_file(self,
                    branch_name: str, 
                    file_path: str, 
                    file_content: bytes, 
                    author: Optional[GithubUser] = None):
        """
        Create a new file
        """
        logger.info(f"Creating file: '{file_path}' on repo: '{self.repo.name}' by '{author.user if author else 'unknown'}'")
        try:
            if self.repo.get_contents(file_path, ref=branch_name):
                logger.info(f"File: '{file_path}' already exists on repo: '{self.repo.name}'")
                return
        except github.UnknownObjectException as _:
            pass # file does not exist
        
        self.repo.create_file(file_path, 
                                    f"new file uploaded by {configs.config.bot_name}", 
                                    file_content, 
                                    branch_name, 
                                    author=author.to_input_git_author() if author else github.GithubObject.NotSet)

    def create_pr(self, src_branch: str, dst_branch: str, title: Optional[str], body: Optional[str] = None):
        """
        Create a new PR
        """
        if title is None:
            title = f"CSGITBOT: pr on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        if body is None:
            body = "pr created automatically"

        logger.info(f"Creating PR from {src_branch} to {dst_branch} on repo: {self.repo.name}")
        self.repo.create_pull(title=title, body=body, head=src_branch, base=dst_branch, maintainer_can_modify=github.GithubObject.NotSet, draft=False)

    def get_all_branches(self):
        """
        Get all branches
        """
        logger.info(f"Getting all branches on repo: {self.repo.name}")
        return self.repo.get_branches()

    def delete_branch(self, branch_name: str):
        logger.info(f"Deleting branch: '{branch_name}' on repo: '{self.repo.name}'")
        self.repo.get_git_ref(f"heads/{branch_name}").delete()