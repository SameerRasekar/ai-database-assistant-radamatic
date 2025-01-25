import json
import os
import sys
from datetime import datetime

import logging

from fastapi import FastAPI, HTTPException, Response, Query, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

path = os.path.abspath("./src/")
sys.path.append(path)

from Service.database_assistant_service import DatabaseAssistantService
from Adapters.langchain_adapter import DatabaseAssistantLangchainAdapter
from Core.database_assistant_core import DatabaseAssistantCore
from Plugins.postgre_store import DatabaseAssistantPostgrePlugins
from Models.process_query_payload import ProcessQueryPayload


app = FastAPI()
log = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DatabaseAssistantController:
    def __init__(self,logger):
        self.logger = logger
        config = self._read_config()
        self.langchain_adapter = DatabaseAssistantLangchainAdapter(config, self.logger)
        self.postgre_plugin = DatabaseAssistantPostgrePlugins(config, self.logger)
        self.database_assistant_core = DatabaseAssistantCore(config, self.logger, self.langchain_adapter, self.postgre_plugin)
        self.database_assistant_service = DatabaseAssistantService(config, self.logger, self.database_assistant_core)
        
    
    def _read_config(self):
        self.logger.info("Identifying the config")

        return self._read_config_from_app_config()     

    
    def _read_config_from_app_config(self):
        environment = os.environ.get('APP_ENV', 'dev')
        config_file_name = f'{environment}_app_config.json'
        self.logger.info(f"The config file: {config_file_name}")
        # Get the current directory path
        current_dir = os.path.dirname(os.path.abspath(__file__))

        parent_dir = os.path.dirname(os.path.dirname(current_dir))

        # Combine the directory path with the config file name
        config_file_path = os.path.join(parent_dir, "config", config_file_name)
        with open(config_file_path, 'r') as file:
            config_data = json.load(file)
        
        return config_data
    
@app.post("/process_query")
async def process_query(payload: ProcessQueryPayload):
    if not payload:
        raise HTTPException(status_code=400, detail= "Query is missing.")
    
    try:
        log.info(f"Received request Payload: {payload}")
        response = controller.database_assistant_service.process_query(payload)
        return response
    except HTTPException as e:
        log.error(f"Error while adding credits -{str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")    

    
def setup_logger():
    logger = logging.getLogger()
    log_debug_flag = os.environ.get('DEBUG', 'false')
    if log_debug_flag == 'true':
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)
    # Configure the logging settings
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.logs'),
            logging.StreamHandler()
        ]
    )
    return logger

# logger
logger = setup_logger()

controller = DatabaseAssistantController(logger)

if __name__ == "__main__":
    try:
        import uvicorn

        uvicorn.run(app, host="127.0.0.1", port=80)
        logger = setup_logger()
        logger.info("The controller is initialize, you can start sending the requests.")

        # local_debug(controller)
    except Exception as ex:
        logger.error(f"Exception occurred while initializing the credit service controller. Exception:{ex}")
        logger.info("The controller failed to initialize, please view logs for more details")