from fastapi import FastAPI, HTTPException, exceptions, Request, responses, status
from .logs import logging
from fastapi.middleware.cors import CORSMiddleware

from .endpoints import github, oauth, init_endpoints
import pkg_resources

    
app = FastAPI()
origins = [
    "http://localhost:5173",
    "https://dynamik.vercel.app/",
    # TODO: mettere le altre istanze di vercel e rimuovere localhost in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(github.router, prefix="/api")
app.include_router(oauth.router, prefix="/oauth")

@app.exception_handler(HTTPException)
async def catch_exceptions_middleware(request: Request, exc: HTTPException):
    logging.error(f"{request}: {exc}")

    content = {'status_code': exc.status_code, 'message': exc.detail, 'data': None}
    return responses.JSONResponse(content=content, status_code=exc.status_code)

@app.get("/", response_class=responses.FileResponse)
async def root():
    return pkg_resources.resource_filename("csgitbot", "static/index.html")

def init():
    logging.info("Initializing...")
    init_endpoints()
