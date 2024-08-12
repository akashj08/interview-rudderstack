# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
#EXPOSE 5000

# Define environment variable for Flask to run
ENV FLASK_APP=app.py

# Disable Python output buffering
ENV PYTHONUNBUFFERED=1


# Set default port (you can override this at runtime)
ENV APP_PORT=5000

# Use a shell form of CMD to allow environment variable substitution
CMD flask run --host=0.0.0.0 --port=$APP_PORT