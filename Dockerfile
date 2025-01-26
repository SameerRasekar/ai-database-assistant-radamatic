# Use an official Python image as the base
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application code to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 80

# Command to run the app
CMD ["uvicorn", "src.Controller.database_assistant_controller:app", "--host", "0.0.0.0", "--port", "80"]
