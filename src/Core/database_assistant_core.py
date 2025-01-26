class DatabaseAssistantCore:
    def __init__(self, config, logger, langchain_adapter, postgre_plugin):
        self.config = config
        self.logger = logger
        self.langchain_adapter = langchain_adapter
        self.postgre_plugin = postgre_plugin

    def process_query(self, query):
        query_intent  = self.langchain_adapter.process_query_intent(query)        
        # sql_response = self.postgre_plugin.execute_sql_query(sql_query)
        if query_intent != "SQLOperation":
            sql_query = self.langchain_adapter.generate_sql_query_from_user_input_for_summarization(query)
            sql_query_response = self.postgre_plugin.execute_sql_query(sql_query)
            sql_response = self.langchain_adapter.generate_summarization_of_query(query, sql_query_response)
            return sql_response
        sql_query = self.langchain_adapter.generate_sql_query_from_user_input(query)
        sql_response = self.postgre_plugin.execute_sql_query(sql_query)
        return sql_response
    