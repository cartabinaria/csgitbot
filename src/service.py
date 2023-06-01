from pydantic import BaseModel
from github import Github
from logs import logging
import datetime
from typing import Optional
import configs
import uuid

class GithubUser(BaseModel):
    user: str
    email: str    
    date: datetime.datetime

class MainService(BaseModel):
    github: Github
    repo_owner: str

    def check_repo(self, repo_name: str) -> bool:
        """
        Check if the repo exists
        """
        try:
            self.github.get_repo(f"{self.repo_owner}/{repo_name}")
        except Exception as e:
            logging.error(f"Error occurred: {str(e)}")
            return False

        return True
    
    def generate_branch_name(self) -> str:
        """
        Generate a new branch name as uuid
        """
        return str(uuid.uuid4())
    
    def create_branch(self, repo_name: str, branch_name: str) -> bool:
        """
        Create a new branch
        """
        try:
            repo = self.github.get_repo(f"{self.repo_owner}/{repo_name}")
            base_branch = repo.get_branch("main")
            repo.create_git_ref(f"refs/heads/{branch_name}", base_branch.commit.sha)
            logging.info(f"Created branch: {branch_name} on repo: {repo_name}")
        except Exception as e:
            logging.error(f"Error occurred: {str(e)}")
            return False

        return True
    
    def create_file(self,
                    repo_name: str, 
                    branch_name: str, 
                    file_path: str, 
                    file_content: bytes, 
                    author: Optional[GithubUser] = None) -> bool:
        """
        Create a new file
        """
        try:
            repo = self.github.get_repo(f"{self.repo_owner}/{repo_name}")
            new_file = repo.create_file(file_path, 
                                        f"new file uploaded by {configs.config.bot_name}", 
                                        file_content, 
                                        branch_name, 
                                        author=author.dict() if author else None)
            logging.info(f"New file created: {new_file} on repo: {repo_name} by {author.user if author else 'unknown'}")
        except Exception as e:
            logging.error(f"Error occurred: {str(e)}")
            return False

        return True