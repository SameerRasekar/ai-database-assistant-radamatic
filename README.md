This repository provides an AI-driven application for student data management using LangChain and various AI APIs (including HuggingFace and OpenAI). The project connects to a PostgreSQL database and utilizes external AI APIs for advanced processing.

Prerequisites
Before setting up the application, ensure you have the following:

Python 3.7+
PostgreSQL (or any other database that fits the configuration)
HuggingFace API Key
OpenAI Azure API Key
Installation
Follow the steps below to set up the application.

Step 1: Clone the Repository
Clone this repository to your local machine.

git clone https://github.com/your-username/your-repo.git
cd your-repo
Step 2: Install Dependencies
Install the required dependencies by running the following command:

bash
Copy
Edit
pip install -r requirements.txt
This will install the necessary libraries, including those for PostgreSQL, HuggingFace, OpenAI, and LangChain.

Step 3: Set Up the .env File
Create a .env file in the root directory of the project and set the required environment variables. Below is the format for the .env file:

HUGGINGFACE_ACCESS_KEY="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"

DATABASE_URL="postgresql+asyncpg://postgres:root@db:5432/students_application"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="root"
POSTGRES_DB="students_application"

openai_api_type="azure"
openai_api_key="c0b3ac530cac45b9803aaf6b3a75cc20"
openai_api_base="https://sepia-ai.openai.azure.com/"
openai_api_version="2024-02-15-preview"
deployment_name="gpt-35-turbo-deployment"


Step 4: Configure PostgreSQL and LangChain
PostgreSQL:
Make sure that your PostgreSQL database is set up correctly. The .env file already includes default values for the database connection.
Modify the values in the .env file for DATABASE_URL, POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB according to your local or remote database configuration.

LangChain Configuration:
Adjust any LangChain-specific settings based on your use case. Make sure to enter your values as required.

Step 5: Start the Application
The application can be started using the controller script. Run the following command to start the application:

python database_assistant_controller.py


Step 6: Make a Request
Once the application is running, you can make a POST request to the appropriate endpoint (based on your implementation). The request should contain a question in the body as a string.

Example:

json
Copy
Edit
{
  "query": "What is the performance of students in Mathematics?"
}
The controller will process the question, retrieve the necessary data from the database, and respond accordingly using the specified AI APIs.

Conclusion
You now have the application set up and ready to process student data with AI-powered assistance. If you run into any issues, ensure that all values in the .env file are correctly configured and that all dependencies are properly installed.

Feel free to contribute and modify the code as per your requirements.