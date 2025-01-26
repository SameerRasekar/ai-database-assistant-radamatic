import os
import time
import openai
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

class DatabaseAssistantLangchainAdapter:
    def __init__(self, config, logger, prompt_template_helper):
        self.config = config
        self.logger = logger
        self.prompt_template_helper = prompt_template_helper
        self.table_schema = self.config["table_schema"]
        self.postgres_table_name = self.config["postgres_table_name"]
        self.huggingface_access_token = os.getenv("HUGGINGFACE_ACCESS_KEY")

        # Azure OpenAI Deployment Configuration
        self.openai_api_type = os.getenv("openai_api_type")
        self.openai_api_key = os.getenv("openai_api_key")
        self.openai_api_base = os.getenv("openai_api_base")
        self.openai_api_version = os.getenv("openai_api_version")
        self.deployment_name = os.getenv("deployment_name")

        # self.openai_api_type = self.config.get("openai_api_type")
        # self.openai_api_key = self.config.get("openai_api_key")
        # self.openai_api_base = self.config.get("openai_api_base")
        # self.openai_api_version = self.config.get("openai_api_version")
        # self.deployment_name = self.config.get("deployment_name")

        self._configure_openai()

    def _configure_openai(self):
        openai.api_type = self.openai_api_type
        openai.api_key = self.openai_api_key
        openai.api_base = self.openai_api_base
        openai.api_version = self.openai_api_version

    def _generate_response(self, system_message, user_message, temperature=0, max_tokens=200, retries=3, delay=2):
        attempt = 0
        while attempt < retries:
            try:
                self.logger.info(f"Sending request to OpenAI. Attempt {attempt + 1}. User message: {user_message}")
                response = openai.ChatCompletion.create(
                    engine=self.deployment_name,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                self.logger.info(f"OpenAI response received: {response}")
                return response['choices'][0]['message']['content'].strip()
            except openai.error.OpenAIError as e:
                self.logger.error(f"OpenAI API Error on attempt {attempt + 1}: {e}. Retrying...")
                attempt += 1
                if attempt >= retries:
                    self.logger.error("Max retries reached for OpenAI API request.")
                    raise Exception(f"Max retries reached. Could not get response: {e}")
                time.sleep(delay * attempt)  # Exponential backoff
            except Exception as e:
                self.logger.error(f"Unexpected error on attempt {attempt + 1}: {e}. Retrying...")
                attempt += 1
                if attempt >= retries:
                    self.logger.error("Max retries reached for unexpected error.")
                    raise Exception(f"Max retries reached. Could not get response: {e}")
                time.sleep(delay * attempt)


    def process_query_intent(self, question):
        if not question:
            self.logger.error("Received an empty question in process_query_intent.")
            raise ValueError("Query must be a non-empty string.")

        try:
            self.logger.info(f"Processing query intent for question: {question}")

            intent_prompt_template = self.prompt_template_helper.load_template("intent_classification_prompt")
            intent_prompt_template = intent_prompt_template.substitute(question=question, table_name=self.postgres_table_name)

            self.logger.info(f"Generated intent classification prompt: {intent_prompt_template}")

            response = self._generate_response(
                system_message="You are an expert in identifying the real intent behind the questions.",
                user_message=intent_prompt_template
            )

            self.logger.info(f"Intent classification response: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Error in process_query_intent: {e}")
            raise


    def generate_sql_query_from_user_input(self, question):
        """
        Generate a valid SQL query based on the user input question.
        """
        try:
            sql_prompt_template = self.prompt_template_helper.load_template("text_to_sql_prompt")
            sql_prompt_template = sql_prompt_template.substitute(question=question, table_name=self.postgres_table_name, table_schema=self.table_schema)

            response = self._generate_response(
                system_message="You are an AI that writes SQL queries.",
                user_message=sql_prompt_template
            )
            return response
        except Exception as e:
            self.logger.error(f"Error generating SQL query: {e}")
            return None

    def generate_summarization_of_query(self, question, sql_response):
        """
        Summarize the SQL response in the context of the user question.
        """
        try:
            summarization_prompt_template = self.prompt_template_helper.load_template("summarization_prompt")
            summarization_prompt_template = summarization_prompt_template.substitute(question=question, sql_response=sql_response)

            response = self._generate_response(
                system_message="You are an AI assistant expert in summarization.",
                user_message=summarization_prompt_template
            )
            return response
        except Exception as e:
            self.logger.error(f"Error generating summarization: {e}")
            return None
    
    def generate_sql_query_from_user_input_for_summarization(self, question):
        """
        Generate a valid SQL query based on the user input question.
        """
        try:
            sql_prompt_template = self.prompt_template_helper.load_template("text_to_sql_summarization_prompt")
            sql_prompt_template = sql_prompt_template.substitute(question=question, table_name=self.postgres_table_name, table_schema=self.table_schema)

            response = self._generate_response(
                system_message="You are an AI that writes SQL queries.",
                user_message=sql_prompt_template
            )
            return response
        except Exception as e:
            self.logger.error(f"Error generating SQL query for summarization: {e}")
            return None
