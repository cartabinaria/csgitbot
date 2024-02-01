from fastapi import FastAPI, exceptions, Request, responses, status
from .logs import logging

from .endpoints import github, oauth, init_endpoints

app = FastAPI()

app.include_router(github.router, prefix="/github")
app.include_router(oauth.router, prefix="/oauth")

# https://github.com/tiangolo/fastapi/issues/3361
# @app.exception_handler(exceptions.RequestValidationError)
# async def validation_exception_handler(request: Request, exc: exceptions.RequestValidationError):
# 	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
# 	logging.error(f"{request}: {exc_str}")
# 	content = {'status_code': 422, 'message': exc_str, 'data': None}
# 	return responses.JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

def init():
    logging.info("Initializing...")
    init_endpoints()
