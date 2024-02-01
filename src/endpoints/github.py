from fastapi import Depends, HTTPException, Security, UploadFile, Form, File, exceptions, Request, responses, status
from typing import Union, Annotated, Optional
from pydantic import BaseModel

import src.configs as configs
from src.logs import logging
from src.service import MainService
from src.endpoints.oauth import decode_token, OAuthCallbackResponse

from fastapi import APIRouter
import os

router = APIRouter()
# service = MainService(configs.config.github_token, configs.config.repo_owner, configs.config)
service = None

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
async def upload_files(repository: str = "", path: str = "", files: list[UploadFile] = File(...), payload: OAuthCallbackResponse = Security(decode_token)):
    """
    Upload files to the specified repository and path, and create PR on this branch.

    :param repository: Local GitHub repository path.
    :param path: Path inside the root of the repository.
    :param files: List of files to upload.
    :return: Response message.
    """
    # Check if repository and path are provided
    if not repository or not path:
        raise HTTPException(status_code=400, detail="Repository and path must be provided.")

    upload_dir = os.path.join(repository, path)
    # Define the directory to save files
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    for file in files:
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

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