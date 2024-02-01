from fastapi import FastAPI, UploadFile, Form, File, exceptions, Request, responses, status
from typing import Union, Annotated, Optional
from pydantic import BaseModel

from .. import configs
from ..logs import logging
from ..service import MainService


from fastapi import APIRouter

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