
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
import httpx

from ..logs import logging
from .. import configs

CLIENT_ID: str = None
CLIENT_SECRET: str = None
REDIRECT_URI: str = None
SCOPE = "user"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()

@router.get("/login")
async def login():
    github_oauth_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}"
    logging.info(f"Redirecting to {github_oauth_url}")
    return RedirectResponse(url=github_oauth_url)

@router.get("/redirect")
async def redirect(code: str = Query(...)):
    access_token = await get_access_token(code)
    user_data = await get_user_data(access_token)
    return user_data

async def get_access_token(code: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code
            }
        )
        data = response.json()
        if "access_token" not in data:
            raise HTTPException(status_code=400, detail="Failed to obtain access token")
        return data["access_token"]


async def get_user_data(access_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {access_token}"}
        )
        user_data = response.json()
        return user_data

def init_globals():
    global CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
    CLIENT_ID = configs.config.client_id
    CLIENT_SECRET = configs.config.client_secret
    REDIRECT_URI = configs.config.redirect_uri