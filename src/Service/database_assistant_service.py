from Models.process_query_payload import ProcessQueryPayload

class DatabaseAssistantService:
    def __init__(self, config, logger, database_assistant_core):
        self.config = config
        self.logger = logger
        self.database_assistant_core = database_assistant_core
        
    def process_query(self, payload: ProcessQueryPayload):
        if not payload.query:
            self.logger.error("The query is missing. Please provide a valid query.")
            raise ValueError("Query must be a non-empty string.")

        self.logger.info(f"Service received query: {payload.query}")

        try:
            response = self.database_assistant_core.process_query(payload.query)
            self.logger.info(f"Service successfully processed query. Response: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Error in service while processing query: {e}")
            raise
    