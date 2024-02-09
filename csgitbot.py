import uvicorn
from src.logs import logging
from src import configs, controller

def start():
    logging.getLogger("main").info("Loading configuration...")
    configs.init()
    controller.init()

    logging.getLogger("main").info("starting service...")

    if configs.config.environment == "production":
        # NOTE: could be a good idea to put forwards_allow_ips in a config file, but for our usecase it's just this ip.
        uvicorn.run("src.controller:app", host="0.0.0.0", port=configs.config.port, forwarded_allow_ips="130.136.3.11")
    else:
        uvicorn.run("src.controller:app", host="0.0.0.0", port=configs.config.port)

if __name__ == "__main__":
    start()