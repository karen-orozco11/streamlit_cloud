# Use the official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY ./frontend/requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY ./frontend .
COPY ./common .
COPY ./frontend/views ./views
COPY ./frontend/components ./components
# Expose the port that Streamlit will run on
EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"] 