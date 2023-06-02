import uvicorn
from src.logs import logging
from src import configs, controller

def start():
    logging.getLogger("main").info("Loading configuration...")
    configs.init()
    controller.init()

    logging.getLogger("main").info("starting service...")
    uvicorn.run("src.controller:app", host="0.0.0.0", port=configs.config.port)
