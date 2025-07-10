import json
import os
import sys
import logging

from fastapi import FastAPI, HTTPException, Response, Query, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

path = os.path.abspath("./src/")
sys.path.append(path)

from Service.database_assistant_service import DatabaseAssistantService
from Adapters.langchain_adapter import DatabaseAssistantLangchainAdapter
from Core.database_assistant_core import DatabaseAssistantCore
from Plugins.postgre_store import DatabaseAssistantPostgrePlugins
from Models.process_query_payload import ProcessQueryPayload
from Utilities.prompt_template_helper import PromptTemplateHelper


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
        self.prompt_template_helper = PromptTemplateHelper(logger)
        self.langchain_adapter = DatabaseAssistantLangchainAdapter(config, self.logger, self.prompt_template_helper)
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
            config_content = file.read()
        
        # Replace environment variable placeholders with actual values
        import re
        def replace_env_vars(match):
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))
        
        config_content = re.sub(r'\$\{([^}]+)\}', replace_env_vars, config_content)
        config_data = json.loads(config_content)
        
        return config_data
    
@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}
    
@app.post("/process_query")
async def process_query(payload: ProcessQueryPayload):
    if not payload.query:
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
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    
    # Ensure logs directory exists
    import os
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
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
        
        logger = setup_logger()
        logger.info("The controller is initialized, you can start sending the requests.")
        
        uvicorn.run(app, host="127.0.0.1", port=8000)

        # local_debug(controller)
    except Exception as ex:
        logger.error(f"Exception occurred while initializing the database assistant controller. Exception:{ex}")
        logger.info("The controller failed to initialize, please view logs for more details")