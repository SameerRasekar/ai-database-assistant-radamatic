import psycopg2


class DatabaseAssistantPostgrePlugins:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.postgres_host = self.config.get("postgres_host")
        self.postgres_port = self.config.get("postgres_port")
        self.postgres_database = self.config.get("postgres_database")
        self.postgres_table_name = self.config.get("postgres_table_name")
        self.postgres_user = self.config.get("postgres_user")
        self.postgres_pass = self.config.get("postgres_password")


    def _connect_to_postgresql(self):
        """
        Connects to the PostgreSQL database and returns the connection object.
        """
        try:
            # Establish the connection
            connection = psycopg2.connect(
                host=self.postgres_host,
                port=self.postgres_port,
                database=self.postgres_database,
                user=self.postgres_user,
                password=self.postgres_pass
            )
            self.logger.info("Connection to PostgreSQL database successful!")
            return connection
        except psycopg2.Error as e:
            self.logger.error(f"Error while connecting to PostgreSQL: {e}")
            return None


    def _disconnect_from_postgresql(self, connection):
        """
        Closes the PostgreSQL database connection.
        """
        try:
            if connection:
                connection.close()
                self.logger.info("PostgreSQL connection closed.")
        except psycopg2.Error as e:
            self.logger.error(f"Error while closing the connection: {e}")


    def execute_sql_query(self, query):
        """
        Executes a SQL query string on the connected PostgreSQL database and returns the results.
        
        Parameters:
        - query (str): The SQL query to be executed.
        
        Returns:
        - tuple: The query results (for SELECT queries) or a success message (for INSERT/UPDATE/DELETE).
        """
        try:
            connection = self._connect_to_postgresql()

            if connection is None:
                return "Failed to connect to the database."

            try:
                cursor = connection.cursor()

                # Check if the query is a SELECT query
                if query.strip().lower().startswith('select'):
                    cursor.execute(query)
                    results = cursor.fetchall()
                    self.logger.info(f"Query executed successfully. Retrieved {len(results)} rows.")
                    cursor.close()
                    return results  # Return the fetched results
                
                # For INSERT, UPDATE, DELETE (non-select queries)
                else:
                    cursor.execute(query)
                    connection.commit()
                    cursor.close()
                    self.logger.info("Query executed successfully.")
                    return f"Query executed successfully: {query}"

            except psycopg2.Error as e:
                self.logger.error(f"Error executing query: {e}")
                return f"Error executing query: {e}"

            finally:
                self._disconnect_from_postgresql(connection)

        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
            return f"Unexpected error occurred: {e}"

