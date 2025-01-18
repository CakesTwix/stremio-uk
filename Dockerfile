FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy all files from your project into the container
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Set the command to start the application
CMD ["uvicorn", "app.stremio:app", "--host", "0.0.0.0", "--port", "8000"]
