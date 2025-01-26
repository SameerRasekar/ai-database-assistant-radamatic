class DatabaseAssistantService:
    def __init__(self, config, logger, database_assistant_core):
        self.config = config
        self.logger = logger
        self.database_assistant_core = database_assistant_core
        
    def process_query(self, payload):
        if payload.query is None:
            self.logger.error("The query is missing. Please provide query.")

        self.logger.info(f"The query looks fine. Query processing initialised. The Query : {payload.query}")

        response = self.database_assistant_core.process_query(payload.query)
        return response
    