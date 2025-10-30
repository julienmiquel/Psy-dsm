# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for poetry
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to the PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy the dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-dev

# Copy the application code
COPY src/ ./src/

# Expose the port the app runs on
EXPOSE 8501

# Define the command to run the application
CMD ["poetry", "run", "streamlit", "run", "src/app/main.py", "--server.port", "8501", "--server.enableCORS", "false"]
