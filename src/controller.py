from fastapi import FastAPI, UploadFile, Form, File
from typing import Union, Annotated, Optional
from pydantic import BaseModel
from . import configs
from .logs import logging
from .service import MainService

app = FastAPI()
app.router.prefix = "/api"

class BasicResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error: str

@app.post("/{reponame}")
async def upload_and_pr(
    reponame: str, 
    file: Annotated[UploadFile, File()],
    username: Optional[Annotated[str, Form()]] = None,
    email: Optional[Annotated[str, Form()]] = None,
    pr_title: Optional[Annotated[str, Form()]] = None
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
        logging.getLogger("controller").error(f"Error occurred: {repr(e)}")
        return ErrorResponse(error=str(e))

    return BasicResponse(message="File uploaded")


@app.post("/{reponame}/{branch_name}")
async def upload_and_pr_with_branch_name(
    reponame: str, 
    branch_name: str, 
    file: Annotated[UploadFile, File()],
    username: Optional[Annotated[str, Form()]] = None,
    email: Optional[Annotated[str, Form()]] = None,
    pr_title: Optional[Annotated[str, Form()]] = None,
) -> Union[BasicResponse, ErrorResponse]:

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
        logging.getLogger("controller").error(f"Error occurred: {repr(e)}")
        return ErrorResponse(error=str(e))

    return BasicResponse(message="File uploaded")

@app.delete("/allbranches/{reponame}")
async def delete_all_branches(reponame: str) -> Union[BasicResponse, ErrorResponse]:
    try:
        service.delete_all_branches(reponame)
    except Exception as e:
        logging.getLogger("controller").error(f"Error occurred: {repr(e)}")
        return ErrorResponse(error=str(e))

    return BasicResponse(message="All branches deleted")

def init():
    global service
    service = MainService(configs.config.github_token, configs.config.repo_owner, configs.config)
