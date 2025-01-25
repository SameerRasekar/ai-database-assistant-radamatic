from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import HuggingFacePipeline
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from huggingface_hub import login

class DatabaseAssistantLangchainAdapter:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.table_schema = self.config["table_schema"]
        self.postgres_table_name = self.config["postgres_table_name"]
        self.huggingface_access_token  = self.config["huggingface_access_token"]
        login(self.huggingface_access_token)

    def _setup_classification_model(self):
        """Load the classification model for intent recognition."""
        model_name = "distilbert-base-uncased-finetuned-sst-2-english"  # Example model for sentiment analysis
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
        return classifier
    
    def _setup_sql_generation_chain(self):
        """Setup LangChain chain for SQL generation."""
        sql_prompt = PromptTemplate(
            input_variables=["query", "table_schema", "postgres_table_name"],
            template=(
                "Generate an SQL query for the following: {query} "
                "where table schema is: {table_schema} and table name is: {postgres_table_name}"
            ),
        )

        # Use OpenAI's GPT-3.5-turbo or GPT-4
        llm_sql = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        sql_chain = LLMChain(llm=llm_sql, prompt=sql_prompt)
        return sql_chain
    
    def setup_summarization_model(self):
        """Setup Hugging Face summarization model."""
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        return summarizer
    
    def process_query_intent(self, query):
        """Classify the query type (SQL or Summarization)."""
        classifier = self._setup_classification_model()
        result = classifier(query)
        if result[0]['label'] == 'POSITIVE':  # Example, this could be adjusted for SQL or Summarization
            return "SQLOperation"
        else:
            return "Summarization"
        
    def generate_sql_query_from_user_input(self, query):
        """Generate SQL query from the input query using LangChain."""
        sql_chain = self._setup_sql_generation_chain()

        # Add table schema and table name to the input
        inputs = {
            "query": query,
            "table_schema": self.table_schema,
            "postgres_table_name": self.postgres_table_name,
        }

        # Run the chain and handle errors
        sql_query = sql_chain.run(inputs)
        if not sql_query or len(sql_query) == 0:
            raise ValueError("Generated SQL query is empty or invalid.")
        return sql_query
    
    def generate_summarization_of_query(self, query, fetched_details):
        """Generate a summary for the query using the summarization model."""
        summarizer = self._setup_summarization_model()
        context = f"Summarize the following details:\n{fetched_details} with respect to {query}"
        summary = summarizer(context, max_length=100, min_length=30, do_sample=False)
        return summary[0]['summary_text']