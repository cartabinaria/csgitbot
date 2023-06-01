""" main AKA controller file! """
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import configs 

app = FastAPI()
app.router.prefix = "/api"

class Reponame(BaseModel):
    reponame: str

@app.get("/{reponame}")
async def upload(reponame: str) -> Reponame:
    reponame = Reponame(reponame=reponame) 
    return reponame

def start():
    configs.init()
    uvicorn.run(app, host="0.0.0.0", port=configs.config.port)

if __name__ == "__main__":
    start()

"""
1. il fatto di dover fare le cose autenticate (quindi farlo a nome di qualcuno un autore e cose simili)
2. fare un check se la repo è presente o meno
3. caricare settings
nei settings caricare come tipo nome del base repo
"""

