import logging
import traceback
from fastapi import Request

# Configure logging to include the file name
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)

class Logger:
    @staticmethod
    def log_request(request: Request):
        logging.info(f"Request: {request.method} {request.url}")

    @staticmethod
    def log_info(message: str):
        logging.info(f"Info: {message}")

    @staticmethod
    def log_success(message: str):
        logging.info(f"Success: {message}")

    @staticmethod
    def log_error(error: Exception):
        logging.error(f"Error: {str(error)}")
        logging.error(traceback.format_exc()) 