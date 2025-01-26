import os
from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import openai
from langchain.prompts import PromptTemplate

class DatabaseAssistantLangchainAdapter:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.table_schema = self.config["table_schema"]
        self.postgres_table_name = self.config["postgres_table_name"]
        self.huggingface_access_token  = os.getenv("HUGGINGFACE_ACCESS_KEY")        


    def process_query_intent(self, question):
        """
        Classify the intent of the given question as either "SQL Operation" or "Summarization"
        using LangChain with a Hugging Face model.

        Args:
            question (str): The user-provided question to classify.
            model_name (str): The Hugging Face model to use (default: bloomz-560m).

        Returns:
            str: The predicted intent ("SQL Operation" or "Summarization").
        """
        # Azure OpenAI Deployment Configuration
        openai.api_type = "azure"  # This is mandatory for Azure OpenAI
        openai.api_key = "c0b3ac530cac45b9803aaf6b3a75cc20"  # Your Azure OpenAI API key
        openai.api_base = "https://sepia-ai.openai.azure.com/"  # Your Azure OpenAI endpoint
        openai.api_version = "2024-02-15-preview"   # The API version you're using
        deployment_name = "gpt-35-turbo-deployment"

        # Define the LangChain prompt template
        prompt_template = f"""
        Given the following question, Please identify the intent of that considering whether it is for the SQLOperation or Summarization.:
        Question: {question}
        Table Name : {self.postgres_table_name}
        If the intent is SQLOperation, return "SQLOperation"
        else return "Summarization".
        The reponse should just return single word "SQLOperation" or "Summarization".
        The justification is not required.

        """

        # Create a LangChain PromptTemplate instance
        prompt = PromptTemplate(input_variables=["question"], template=prompt_template)

        # Format the prompt with the question using LangChain
        formatted_prompt = prompt.format(question=question)

        # Use Azure OpenAI's ChatCompletion API
        response = openai.ChatCompletion.create(
            engine=deployment_name,  # Azure deployment name
            messages=[
                {"role": "system", "content": "You are expert in Identification of real intent behind the questions."},
                {"role": "user", "content": formatted_prompt}
            ],
            temperature=0,  # Set temperature to 0 for deterministic output
            max_tokens=200  # Adjust max tokens for your response size
        )

        # Extract the SQL query from the response
        intent = response['choices'][0]['message']['content'].strip()
        return intent
    
    def generate_sql_query_from_user_input(self, question):

        # Azure OpenAI Deployment Configuration
        openai.api_type = "azure"  # This is mandatory for Azure OpenAI
        openai.api_key = "c0b3ac530cac45b9803aaf6b3a75cc20"  # Your Azure OpenAI API key
        openai.api_base = "https://sepia-ai.openai.azure.com/"  # Your Azure OpenAI endpoint
        openai.api_version = "2024-02-15-preview"   # The API version you're using
        deployment_name = "gpt-35-turbo-deployment"

        # Define the LangChain prompt template
        prompt_template = f"""
        Given the following question, create a valid SQL query:
        In case of Query generation, Let the queries be case insensitive. i.e Physics and physics will mean the same thing.
        Mathematics, maths and math will mean the same thing.

        Question: {question}
        Table Name : {self.postgres_table_name}
        Table Creation Query : {self.table_schema}
        SQL Query:
        """

        # Create a LangChain PromptTemplate instance
        prompt = PromptTemplate(input_variables=["question"], template=prompt_template)

        # Format the prompt with the question using LangChain
        formatted_prompt = prompt.format(question=question)

        # Use Azure OpenAI's ChatCompletion API
        response = openai.ChatCompletion.create(
            engine=deployment_name,  # Azure deployment name
            messages=[
                {"role": "system", "content": "You are an AI that writes SQL queries."},
                {"role": "user", "content": formatted_prompt}
            ],
            temperature=0,  # Set temperature to 0 for deterministic output
            max_tokens=200  # Adjust max tokens for your response size
        )

        # Extract the SQL query from the response
        sql_query = response['choices'][0]['message']['content'].strip()
        return sql_query
    
    def generate_summarization_of_query(self, question, sql_response):

        # Azure OpenAI Deployment Configuration
        openai.api_type = "azure"  # This is mandatory for Azure OpenAI
        openai.api_key = "c0b3ac530cac45b9803aaf6b3a75cc20"  # Your Azure OpenAI API key
        openai.api_base = "https://sepia-ai.openai.azure.com/"  # Your Azure OpenAI endpoint
        openai.api_version = "2024-02-15-preview"   # The API version you're using
        deployment_name = "gpt-35-turbo-deployment"

        # Define the LangChain prompt template
        prompt_template = f"""
        Given the following question and the SQL response for the Question. create a valid SQL query:
        Please provide a summary of the SQL response with respect to Question
        Question: {question}
        SQL response : {sql_response}

        Please provide crisp and clear summary.
        In case of summarization, Let the queries be case insensitive. i.e Physics and physics will mean the same thing.
        Mathematics, maths and math will mean the same thing.
        """

        # Create a LangChain PromptTemplate instance
        prompt = PromptTemplate(input_variables=["question"], template=prompt_template)

        # Format the prompt with the question using LangChain
        formatted_prompt = prompt.format(question=question)

        # Use Azure OpenAI's ChatCompletion API
        response = openai.ChatCompletion.create(
            engine=deployment_name,  # Azure deployment name
            messages=[
                {"role": "system", "content": "You are an AI assistant expert in Summarization."},
                {"role": "user", "content": formatted_prompt}
            ],
            temperature=0,  # Set temperature to 0 for deterministic output
            max_tokens=200  # Adjust max tokens for your response size
        )

        # Extract the SQL query from the response
        sql_query = response['choices'][0]['message']['content'].strip()
        return sql_query