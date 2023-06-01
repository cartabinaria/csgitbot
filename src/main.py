""" main AKA controller file! """
from fastapi import FastAPI, UploadFile, Form, File
import uvicorn
import configs 
from logs import logging
from typing import Union, Annotated, Optional
from service import MainService
from pydantic import BaseModel

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


def start():
    logging.getLogger("main").info("Loading configuration...")
    configs.init()

    global service
    service = MainService(configs.config.github_token, configs.config.repo_owner, configs.config)

    logging.getLogger("main").info("starting service...")
    uvicorn.run(app, host="0.0.0.0", port=configs.config.port)

if __name__ == "__main__":
    start()

# dop andare a spostare in service e utilities di github in altro file.