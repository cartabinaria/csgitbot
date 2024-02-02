from fastapi import Depends, HTTPException, Security, UploadFile, Form, File, exceptions, Request, responses, status
from typing import Union, Annotated, Optional
from pydantic import BaseModel
from src.my_types import Autor

import src.configs as configs
from src.logs import logging
from src.service import MainService
from src.endpoints.oauth import decode_token, OAuthCallbackResponse
import src.services.repomanager as repomanager

from fastapi import APIRouter
import os

router = APIRouter()
# service = MainService(configs.config.github_token, configs.config.repo_owner, configs.config)
service = None
REPOS_PATH = "repos"

class BasicResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error: str

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
    OAuthCallbackResponse
    """
    # Check if repository and path are provided
    if not repository or not path:
        raise HTTPException(status_code=400, detail="Repository and path must be provided.")

    repository_path = os.path.join(REPOS_PATH, repository)
    if not repomanager.check_repo_exists(repository_path):
        raise HTTPException(status_code=400, detail=f"Requested repository {repository} does not exist.")

    print(payload, "------------")
    author: Autor = Autor(name=payload.username, email=payload.email)
    branch_name = repomanager.create_branch_name(author)
    repomanager.move_or_create_to_branch(repository_path, branch_name)
    upload_dir = os.path.join(repository_path, path)
    # Define the directory to save files
    os.makedirs(upload_dir, exist_ok=True)

    files_to_commit = [""] * len(files)
    for i, file in enumerate(files):
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        files_to_commit[i] = file_path

    commit_files = repomanager.commit_files(repository_path, files_to_commit, author)
    repomanager.move_or_create_to_branch(repository_path, "main")

    if not commit_files:
        raise HTTPException(status_code=500, detail="Failed to commit files to the repository.")

    return {"detail": f"{len(files)} files uploaded successfully"}

@router.post("/{reponame}")
async def upload_and_pr(
    reponame: str, 
    file: Annotated[UploadFile, File()],
    username: Annotated[str | None, Form()] = None,
    email: Annotated[str | None, Form()] = None,
    pr_title: Annotated[str | None, Form()] = None,
) -> Union[BasicResponse, ErrorResponse]:
    branch_name = service.generate_branch_name()

    try:
        assert isinstance(branch_name, str), "branch name is not a string"

        await service.upload_and_pr(
            reponame, 
            branch_name, 
            file,
            username,
            email,
            pr_title,
        )
    except Exception as e:
        logging.getLogger("github").error(f"Error occurred: {repr(e)}")
        return ErrorResponse(error=str(e))

    return BasicResponse(message="File uploaded")


@router.post("/{reponame}/{branch_name}")
async def upload_and_pr_with_branch_name(
    reponame: str, 
    branch_name: str, 
    file: Annotated[UploadFile, File()],
    username: Annotated[str | None, Form()] = None,
    email: Annotated[str | None, Form()] = None,
    pr_title: Annotated[str | None, Form()] = None,
) -> Union[BasicResponse, ErrorResponse]:
    # TODO: add path upload
    try:
        await service.upload_and_pr(
            reponame, 
            branch_name, 
            file,
            username,
            email,
            pr_title,
        )
    except Exception as e:
        logging.getLogger("github").error(f"Error occurred: {repr(e)}")
        return ErrorResponse(error=str(e))

    return BasicResponse(message="File uploaded")

@router.delete("/allbranches/{reponame}")
async def delete_all_branches(reponame: str) -> Union[BasicResponse, ErrorResponse]:
    try:
        service.delete_all_branches(reponame)
    except Exception as e:
        logging.getLogger("github").error(f"Error occurred: {repr(e)}")
        return ErrorResponse(error=str(e))

    return BasicResponse(message="All branches deleted")