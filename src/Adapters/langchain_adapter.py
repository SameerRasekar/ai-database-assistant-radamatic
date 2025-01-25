import openai
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.agents import AgentExecutor
import os
from string import Template
import time



class DatabaseAssistantLangchainAdapter:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.openai_access_key = self.config["openai_access_key"]
        self.table_schema = self.config["table_schema"]
        self.postgres_table_name = self.config["postgres_table_name"]
        # self.llm = OpenAI(temperature=0.6, openai_api_key=self.openai_access_key)
        openai.api_key = self.openai_access_key

    def process_query_intent(self, query):
        """
        Detects the intent of the user's query using OpenAI.
        It classifies the query into categories such as 'SQL Operation' or 'Summarization'.
        """
        intent_classification_prompt = self._load_template("intent_classification_prompt")
        intent_classification_prompt = intent_classification_prompt.substitute(query=query)

        llm = OpenAI(temperature=0.6, openai_api_key=self.openai_access_key)
        max_retries = 3
        initial_delay = 2  # seconds
        retries = 0
        delay = initial_delay

        while retries < max_retries:
            try:
                # Send the prompt to OpenAI LLM
                response = llm.predict(intent_classification_prompt)
                query_intent = response.strip().lower()
                return query_intent
            except Exception as e:
                # Log and retry on rate limit errors
                self.logger.warning(f"Rate limit exceeded. Retrying in {delay} seconds... (Attempt {retries + 1}/{max_retries})")
                retries += 1
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            except Exception as e:
                # Catch all other exceptions, log them, and re-raise
                self.logger.error(f"An error occurred: {e}")
                raise

        # Raise an exception if all retries are exhausted
        raise RuntimeError("Exceeded maximum retry attempts.")

    def generate_sql_query_from_user_input(self, user_query) -> str:
        """
        Converts a user's query into a proper PostgreSQL SQL query.
        
        Parameters:
        - user_query (str): The input query from the user.
        - openai_api_key (str): Your OpenAI API key for generating SQL.
        
        Returns:
        - str: The generated PostgreSQL SQL query.
        """
        # Define a prompt template for SQL generation
        text_to_sql_prompt = self._load_template("text_to_sql_prompt")
        text_to_sql_prompt = text_to_sql_prompt.substitute(query=user_query, table_schema = self.table_schema, table_name = self.postgres_table_name)
        
        # Initialize the LLM (large language model) using OpenAI API
        llm = OpenAI(temperature=0, openai_api_key=self.openai_access_key)
        
        # Create the prompt template and LLMChain
        prompt_template = PromptTemplate(input_variables=["query"], template=text_to_sql_prompt)
        sql_chain = LLMChain(llm=llm, prompt=prompt_template)
        
        # Generate the SQL query using the LLMChain
        sql_query = sql_chain.run(query=user_query)
        
        return sql_query
    
    def generate_summarization_of_query(self, sql_response, query):
        summarization_prompt = self._load_template("summarization_prompt")
        summarization_prompt = summarization_prompt.substitute(data=sql_response, query =query)
        llm = OpenAI(temperature=0.7, openai_api_key=self.openai_access_key)
        prompt_template = PromptTemplate(input_variables=["query"], template=summarization_prompt)
        summarization = LLMChain(llm=llm, prompt=prompt_template)
        return summarization
    

    def _load_template(self, name="default"):
        # file path
        lib_path = os.path.dirname(__file__)
        parent_dir  = os.path.dirname(lib_path)
        file_path = "%s/templates/%s.txt" % (parent_dir, name)
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Template {name} does not exist.")
            with open(file_path, 'r', encoding='utf-8') as f:
                template = Template(f.read())
        except Exception as ex:
            self.logger.error(f"Exception while loading the template : {ex}")
            template = None

        return template