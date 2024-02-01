from fastapi import FastAPI, HTTPException, exceptions, Request, responses, status
from .logs import logging

from .endpoints import github, oauth, init_endpoints

    
app = FastAPI()

app.include_router(github.router, prefix="/api")
app.include_router(oauth.router, prefix="/oauth")

@app.exception_handler(HTTPException)
async def catch_exceptions_middleware(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return responses.RedirectResponse(url=app.url_path_for("login"))
    
    logging.error(f"{request}: {exc}")

    content = {'status_code': exc.status_code, 'message': exc.detail, 'data': None}
    return responses.JSONResponse(content=content, status_code=exc.status_code)

# https://github.com/tiangolo/fastapi/issues/3361
# @app.exception_handler(exceptions.RequestValidationError)
# async def validation_exception_handler(request: Request, exc: exceptions.RequestValidationError):
# 	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
# 	logging.error(f"{request}: {exc_str}")
# 	content = {'status_code': 422, 'message': exc_str, 'data': None}
# 	return responses.JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY

def init():
    logging.info("Initializing...")
    init_endpoints()
