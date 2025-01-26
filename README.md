# AI-Driven Student Data Management Application

This repository provides an AI-driven application for student data management using **LangChain** and various AI APIs (including **HuggingFace** and **OpenAI**). The project connects to a **PostgreSQL database** and utilizes external AI APIs for advanced processing.

---

## Prerequisites

Before setting up the application, ensure you have the following:

- **Python 3.7+**
- **PostgreSQL** (or any other database that fits the configuration)
- **HuggingFace API Key**
- **OpenAI Azure API Key**

---

## Installation

## Step 1: Clone the Repository
Clone this repository to your local machine:

git clone https://github.com/SameerRasekar/ai-database-assistant-radamatic.git


## Step 2: Install Dependencies
Install the required dependencies by running the following command:
pip install -r requirements.txt

This will install the necessary libraries, including those for PostgreSQL, HuggingFace, OpenAI, and LangChain.

## Configuration

## Step 3: Set Up the .env File

HUGGINGFACE_ACCESS_KEY="ENTER_YOUR_HUGGINGFACE_ACCESS_KEY"
DATABASE_URL="postgresql://<ENTER_YOUR_POSTGRES_USER>:<ENTER_YOUR_POSTGRES_PASSWORD>@<ENTER_YOUR_POSTGRES_HOST>:<ENTER_YOUR_POSTGRES_PORT>/<ENTER_YOUR_POSTGRES_DB>"
POSTGRES_USER="ENTER_YOUR_POSTGRES_USER"
POSTGRES_PASSWORD="ENTER_YOUR_POSTGRES_PASSWORD"
POSTGRES_HOST="ENTER_YOUR_POSTGRES_HOST"
POSTGRES_PORT="ENTER_YOUR_POSTGRES_PORT"
POSTGRES_TABLE_NAME="ENTER_YOUR_POSTGRES_TABLE_NAME"
POSTGRES_DB="ENTER_YOUR_POSTGRES_DB"
openai_api_type="ENTER_YOUR_OPENAI_API_TYPE"
openai_api_key="ENTER_YOUR_OPENAI_API_KEY"
openai_api_base="ENTER_YOUR_OPENAI_API_BASE"
openai_api_version="ENTER_YOUR_OPENAI_API_VERSION"
deployment_name="ENTER_YOUR_DEPLOYMENT_NAME"


## Step 4: Configure PostgreSQL and LangChain

### PostgreSQL Configuration:
Ensure your PostgreSQL database is set up and running.
Modify the values in the .env file for DATABASE_URL, POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB according to your local or remote database configuration.

# LangChain Configuration:
Adjust LangChain-specific settings in your code or configuration file as required by your use case.


# Running the Application

## Run Locally

1. To run the application locally, use the following command:

python controller/database_assistant_controller.py

2. Use Postman or Swagger UI to send a request.

#### Example Request:
{
  "query": "Insert a marks for Sameer who scored 85 in Physics and have id 1234"
}


## Run on Docker

### Follow these commands to run the application on Docker:

1. Stop and clean up existing containers and volumes usinf following commands:

docker-compose down --volumes
docker system prune -af

2. Build and start the Docker containers:
docker-compose up --build

3. Use Postman or Swagger UI to send a request.

#### Example Request:

{
  "query": "Insert a marks for Sameer who scored 85 in Physics and have id 1234"
}

# Usage


## Make a Request
Once the application is running, you can make a POST request to the appropriate endpoint (based on your implementation). The request body should contain the query as a string.

Example Request:

{
  "query": "Insert a marks for Sameer who scored 85 in Physics and have id 1234"
}
The controller will process the query, retrieve the necessary data from the database, and respond accordingly using the specified AI APIs.



# Note

1. Local Configuration:

When running locally, set POSTGRES_HOST="localhost" in the .env file.
Docker Configuration:

2. When running inside Docker, set POSTGRES_HOST="db" (the service name for the database container) in the .env file.





# Viewing Database Details in Docker
To view database-related details when running in the Docker environment, follow these steps:

1. Access the PostgreSQL container:

docker exec -it postgres_db bash
Connect to the PostgreSQL database:

2. Connect to the PostgreSQL database:

psql -U postgres -d ${POSTGRES_DB}

3. View data from a table:

select * from your_table_name;
Replace your_table_name with the name of the table you wish to query.