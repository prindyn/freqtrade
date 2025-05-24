# Use a lightweight Python 3.9 image as the base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /service

# Copy the requirements file into the container and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./app /service/app

# Copy additional files (e.g., scripts, data) into the container
COPY start.sh migrate_bot_table.py ./

# Make the start script executable
RUN chmod +x start.sh

# Set the default command to run when the container starts
CMD ["./start.sh"]
