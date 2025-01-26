class DatabaseAssistantCore:
    def __init__(self, config, logger, langchain_adapter, postgre_plugin):
        self.config = config
        self.logger = logger
        self.langchain_adapter = langchain_adapter
        self.postgre_plugin = postgre_plugin

    def process_query(self, query):
        if not query:
            self.logger.error("Received an empty query in core.py.")
            raise ValueError("Query must be a non-empty string.")

        self.logger.info(f"Core received query: {query}")

        try:
            query_intent = self.langchain_adapter.process_query_intent(query)
            self.logger.info(f"Determined query intent: {query_intent}")

            if query_intent != "SQLOperation":
                self.logger.info("Intent classified as Summarization. Generating SQL summarization query.")
                sql_query = self.langchain_adapter.generate_sql_query_from_user_input_for_summarization(query)
                self.logger.info(f"Generated summarization SQL query: {sql_query}")

                sql_query_response = self.postgre_plugin.execute_sql_query(sql_query)
                self.logger.info(f"PostgreSQL query response: {sql_query_response}")

                sql_response = self.langchain_adapter.generate_summarization_of_query(query, sql_query_response)
                self.logger.info(f"Summarization response: {sql_response}")
                return sql_response

            self.logger.info("Intent classified as SQL Operation. Generating SQL operation query.")
            sql_query = self.langchain_adapter.generate_sql_query_from_user_input(query)
            self.logger.info(f"Generated SQL query: {sql_query}")

            sql_response = self.postgre_plugin.execute_sql_query(sql_query)
            self.logger.info(f"SQL operation response: {sql_response}")
            return sql_response

        except Exception as e:
            self.logger.error(f"Error in core while processing query: {e}")
            raise

    