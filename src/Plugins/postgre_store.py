import psycopg2
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()


class DatabaseAssistantPostgrePlugins:
    def __init__(self, config, logger):
        """
        Initialize the DatabaseAssistantPostgrePlugins instance.

        Parameters:
        - config (dict): A dictionary containing the PostgreSQL connection configurations.
        - logger (logging.Logger): A logger instance for logging information and errors.
        """
        self.config = config
        self.logger = logger

        # # Extract PostgreSQL configuration from the provided config dictionary
        # self.postgres_host = self.config.get("postgres_host")
        # self.postgres_port = self.config.get("postgres_port")
        # self.postgres_database = self.config.get("postgres_database")
        # self.postgres_table_name = self.config.get("postgres_table_name", None)
        # self.postgres_user = self.config.get("postgres_user")
        # self.postgres_pass = self.config.get("postgres_password")

        # Extract PostgreSQL configuration from the provided .env file
        self.postgres_host = os.getenv("POSTGRES_HOST")
        self.postgres_port = os.getenv("POSTGRES_PORT")
        self.postgres_database = os.getenv("POSTGRES_DB")
        self.postgres_table_name = os.getenv("POSTGRES_TABLE_NAME", None)
        self.postgres_user = os.getenv("POSTGRES_USER")
        self.postgres_pass = os.getenv("POSTGRES_PASSWORD")

        # Validate essential configurations
        if not all([self.postgres_host, self.postgres_port, self.postgres_database, self.postgres_user, self.postgres_pass]):
            raise ValueError("Missing essential PostgreSQL connection configurations.")

    def _connect_to_postgresql(self):
        """
        Connects to the PostgreSQL database and returns the connection object.
        Raises:
        - psycopg2.Error: If connection fails.
        """
        self.logger.info("Attempting to connect to PostgreSQL database...")
        try:
            connection = psycopg2.connect(
                host=self.postgres_host,
                port=self.postgres_port,
                database=self.postgres_database,
                user=self.postgres_user,
                password=self.postgres_pass,
            )
            self.logger.info("Connection to PostgreSQL database successful.")
            return connection
        except psycopg2.Error as e:
            self.logger.error(f"Failed to connect to PostgreSQL database: {e}")
            raise

    def _disconnect_from_postgresql(self, connection):
        """
        Closes the PostgreSQL database connection.
        """
        try:
            if connection:
                connection.close()
                self.logger.info("PostgreSQL connection successfully closed.")
        except psycopg2.Error as e:
            self.logger.error(f"Error while closing the PostgreSQL connection: {e}")
            raise

    def _check_primary_key_exists(self, table_name, primary_key_column, primary_key_value):
        """
        Checks if a record with the given primary key already exists in the table.
        
        Parameters:
        - table_name (str): The name of the table to query.
        - primary_key_column (str): The primary key column name.
        - primary_key_value: The value of the primary key to check.

        Returns:
        - bool: True if the primary key exists, False otherwise.
        """
        query = f"SELECT EXISTS (SELECT 1 FROM {table_name} WHERE {primary_key_column} = %s)"
        self.logger.debug(f"Checking if primary key exists with query: {query} and value: {primary_key_value}")

        connection = None
        try:
            connection = self._connect_to_postgresql()
            cursor = connection.cursor()
            cursor.execute(query, (primary_key_value,))
            exists = cursor.fetchone()[0]
            self.logger.info(f"Primary key check completed: Exists = {exists}")
            return exists
        except psycopg2.Error as e:
            self.logger.error(f"Error during primary key check: {e}")
            raise
        finally:
            if connection:
                self._disconnect_from_postgresql(connection)

    def execute_sql_query(self, query, table_name=None, primary_key_column=None, primary_key_value=None):
        """
        Executes a SQL query string on the PostgreSQL database and handles primary key conflicts.

        Parameters:
        - query (str): The SQL query to be executed.
        - table_name (str, optional): The table name for primary key check.
        - primary_key_column (str, optional): The primary key column name for primary key check.
        - primary_key_value (optional): The primary key value for primary key check.

        Returns:
        - list: Query results for SELECT queries.
        - str: Success message for non-SELECT queries.

        Raises:
        - ValueError: If the query is invalid or fails to execute.
        - psycopg2.Error: For database-related errors.
        """
        if not query or not isinstance(query, str):
            self.logger.error("Invalid query provided. Query must be a non-empty string.")
            raise ValueError("Query must be a non-empty string.")

        query_type = self._get_query_type(query)
        self.logger.info(f"Preparing to execute query of type: {query_type}")
        self.logger.debug(f"Query to execute: {query}")

        if query_type == "INSERT" and table_name and primary_key_column and primary_key_value is not None:
            self.logger.info(f"Checking for primary key conflict before executing INSERT query...")
            if self._check_primary_key_exists(table_name, primary_key_column, primary_key_value):
                self.logger.warning(
                    f"Primary key conflict detected: Table '{table_name}', Column '{primary_key_column}', Value '{primary_key_value}'"
                )
                return f"Primary key conflict: A record with {primary_key_column} = {primary_key_value} already exists in table {table_name}."

        connection = None

        try:
            # Connect to the database
            connection = self._connect_to_postgresql()
            cursor = connection.cursor()

            # Handle SELECT queries
            if query_type == "SELECT":
                self.logger.debug("Detected SELECT query. Executing and fetching results...")
                cursor.execute(query)
                results = cursor.fetchall()
                self.logger.info(f"Query executed successfully. Retrieved {len(results)} rows.")
                return results

            # Handle non-SELECT queries (INSERT, UPDATE, DELETE)
            else:
                self.logger.debug(f"Detected {query_type} query. Executing and committing changes...")
                cursor.execute(query)
                connection.commit()
                self.logger.info(f"Query executed successfully: {query}")
                return "Query executed successfully."

        except psycopg2.ProgrammingError as pe:
            self.logger.error(f"Programming error while executing query: {pe}")
            raise ValueError(f"Programming error in query: {pe}")
        except psycopg2.Error as e:
            self.logger.error(f"Database error while executing query: {e}")
            raise
        except Exception as ex:
            self.logger.error(f"Unexpected error while executing query: {ex}")
            raise
        finally:
            if connection:
                self._disconnect_from_postgresql(connection)
            self.logger.info("Database operation completed.")

    def _get_query_type(self, query):
        """
        Determines the type of the query based on the SQL command.
        
        Parameters:
        - query (str): The SQL query string.
        
        Returns:
        - str: The query type (e.g., SELECT, INSERT, UPDATE, DELETE, or UNKNOWN).
        """
        first_word = query.strip().split(" ", 1)[0].upper()
        if first_word in ["SELECT", "INSERT", "UPDATE", "DELETE"]:
            return first_word
        return "UNKNOWN"
