from fastapi import Depends, HTTPException, Security, UploadFile, Form, File
from pydantic import BaseModel
from fastapi import APIRouter
import os

from src.github_utils import GithubUtils
from src.my_types import Author, BranchName
import src.configs as configs
from src.logs import logging
from src.endpoints.oauth import decode_token, OAuthCallbackResponse
import src.services.repomanager as repomanager


router = APIRouter()
REPOS_PATH = "repos"

class BasicResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error: str

class UploadFilesResponse(BaseModel):
    detail: str
    branch_name: str

class CreateFilesResponse(BaseModel):
    detail: str
    url: str

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/data")
async def get_data(payload: OAuthCallbackResponse = Security(decode_token)):
    print(payload)
    return {"message": "Here is your data", "user": payload}

@router.post("/uploadfiles/")
async def upload_files(repository: str = Form(...), path: str = Form(...), files: list[UploadFile] = File(...), payload: OAuthCallbackResponse = Security(decode_token)):
    """Upload files to the specified repository and path, and create PR on this branch.

    Args
    ----
    repository: str
        Local GitHub repository path.
    path: str
        Path inside the root of the repository.

    Returns
    -------
    """
    # Check if repository and path are provided
    if not repository or not path:
        raise HTTPException(status_code=400, detail="Repository and path must be provided.")

    repository_path = os.path.join(REPOS_PATH, repository)
    if not repomanager.check_path_exists(repository_path):
        raise HTTPException(status_code=400, detail=f"Requested repository {repository} does not exist.")

    curr_repo = repomanager.LocalRepo(repository_path)
    if not curr_repo.is_initialized():
        raise HTTPException(status_code=500, detail=f"Repository {repository} is not correctly configured in the system.")
    
    try:
        logging.getLogger("github").info(f"Pulling the repository {repository}")
        curr_repo.pull()
        author: Author = Author(name=payload.username, email=payload.email)
        branch_name = repomanager.create_branch_name(author)
        curr_repo.create_branch(branch_name)
        curr_repo.move_to_branch(branch_name)

        upload_dir = os.path.join(repository_path, path)
        os.makedirs(upload_dir, exist_ok=True)

        logging.getLogger("github").info(f"Uploading {len(files)} files to the repository {repository}")
        files_to_commit = [""] * len(files)
        for i, file in enumerate(files):
            file_path = os.path.join(upload_dir, file.filename)
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())

            repo_relative_path = os.path.join(path, file.filename)
            files_to_commit[i] = repo_relative_path

        logging.getLogger("github").info(f"Committing and pushing files to the repository {repository}")
        curr_repo.commit_files(files_to_commit, author)
        curr_repo.push()
        curr_repo.move_to_default()

    except Exception as e:
        curr_repo.move_to_default()
        logging.getLogger("github").error(f"Error occurred: {repr(e)}")
        raise HTTPException(status_code=500, detail="Failed to commit and push files to the repository.")

    # see https://gitpython.readthedocs.io/en/stable/intro.html#limitations
    del curr_repo
    return UploadFilesResponse(detail=f"{len(files)} files uploaded successfully", branch_name=branch_name)

@router.post("/create-pr/")
async def create_pr(repository: str = Form(...), branch_name: str = Form(...), title: str = Form(...), payload: OAuthCallbackResponse = Security(decode_token)):
    """Create a PR on the specified repository and branch.
    Note: only the owner of the branch can create a PR from this API.
    You are the owner of the branch if it starts with your username.

    Args
    ----
    repository: str
        Local GitHub repository path.
    branch_name: str
        Branch name to create the PR from.
    title: str
        Title of the PR.

    Returns
    -------
    """
    # Check if repository and branch_name are provided
    if not repository or not branch_name:
        raise HTTPException(status_code=400, detail="Repository and branch name must be provided.")

    repository_path = os.path.join(REPOS_PATH, repository)
    if not repomanager.check_path_exists(repository_path):
        raise HTTPException(status_code=400, detail=f"Requested repository {repository} does not exist.")

    curr_repo = repomanager.LocalRepo(repository_path)
    if not curr_repo.is_initialized():
        raise HTTPException(status_code=500, detail=f"Repository {repository} is not correctly configured in the system.")
    
    # check if remote has the branch
    github_client = GithubUtils()
    github_client.set_repo(repository)
    if not github_client.branch_exists(branch_name):
        raise HTTPException(status_code=400, detail=f"Branch {branch_name} does not exist in the repository.")

    branch_name_object = BranchName.from_str(branch_name)
    if branch_name_object.username != payload.username:
        raise HTTPException(status_code=403, detail="You are not allowed to create PR from this branch.")

    try:
        pull_request = github_client.create_pr(branch_name, "main", title=title)
        html_url = pull_request.html_url
    except Exception as e:
        logging.getLogger("github").error(f"Error occurred: {repr(e)}")
        raise HTTPException(status_code=500, detail="Failed to create PR.")

    return CreateFilesResponse(detail=f"PR created successfully", url=html_url)
    
def init_github_service():
    # check key path is present
    # TODO: also check it has correct format.
    if configs.config.is_github_app and not os.path.exists(configs.config.key_path):
        logging.getLogger("github").error(f"Key path {configs.config.key_path} does not exist.")
        raise FileNotFoundError(f"Key path {configs.config.key_path} does not exist.")

    # DEPRECATED, should be removed
    pass
