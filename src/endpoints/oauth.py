
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import JSONResponse, RedirectResponse
import httpx
from pydantic import BaseModel
from jose import JWTError, jwt
import datetime

from ..logs import logging
from .. import configs

CLIENT_ID: str = None
CLIENT_SECRET: str = None
REDIRECT_URI: str = None
SCOPE = "read:user,user:email"

router = APIRouter()

class OAuthCallbackResponse(BaseModel):
    access_token: str
    username: str
    email: str

@router.post("/login", name="login")
@router.get("/login", name="login")
async def login():
    github_oauth_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}&original_url=prova"
    logging.info(f"Redirecting to {github_oauth_url}")
    return RedirectResponse(url=github_oauth_url)

@router.get("/redirect")
async def redirect(code: str = Query(...)) -> OAuthCallbackResponse:
    access_token = await get_access_token(code)
    user_data = await get_user_data(access_token)

    # user_data["email"] could be null sometimes, check https://github.com/nextauthjs/next-auth/issues/374

    if user_data["email"] is None:
        user_email = await get_user_email(access_token)
        try:
            first_email = user_email[0]["email"]
        except IndexError:
            raise HTTPException(status_code=400, detail="Failed to obtain user email")

        user_data["email"] = first_email

    callback_response = OAuthCallbackResponse(
        access_token=access_token,
        username=user_data["login"],
        email=user_data["email"],
        expiration=datetime.datetime.utcnow() + datetime.timedelta(minutes=configs.config.jwt_config.access_token_expiration)
    )

    response = JSONResponse(content=callback_response.dict())

    response.set_cookie(
        key="access_token",
        value=create_access_token(callback_response.dict()),
        httponly=True,
        samesite="none",
        secure=True
    )

    return response

async def get_token_or_throw(request: Request):
    token = request.cookies.get("access_token")
    if token is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return token

async def decode_token(token: str = Depends(get_token_or_throw)):
    try:
        # Add your JWT secret key used for encoding here
        secret_key = configs.config.jwt_config.secret_key
        payload = jwt.decode(token, secret_key, algorithms=[configs.config.jwt_config.algorithm])
        return OAuthCallbackResponse(**payload)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=configs.config.jwt_config.access_token_expiration)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, configs.config.jwt_config.secret_key, algorithm=configs.config.jwt_config.algorithm)

    return encoded_jwt

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

async def get_user_email(access_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"token {access_token}"}
        )
        user_data = response.json()
        return user_data

def init_globals():
    global CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
    CLIENT_ID = configs.config.client_id
    CLIENT_SECRET = configs.config.client_secret
    REDIRECT_URI = configs.config.redirect_uri