import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import boto3
import botocore
from logger import Logger
from aws_helper import AWSHelper
from openai_helper import OpenAIHelper
import traceback
from datetime import datetime

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize helpers
aws_region = os.getenv("AWS_REGION", "us-west-2")  # Default to 'us-west-2' if not set
aws_helper = AWSHelper(region_name=aws_region)
openai_helper = OpenAIHelper(api_key=os.getenv("OPENAI_API_KEY"))

# Configure logging to include the file name
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)

# Suppress boto3 and botocore debug logs
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)

# Suppress other AWS-related debug logs
logging.getLogger('s3transfer').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)

class Question(BaseModel):
    question: str

class OnboardingData(BaseModel):
    email: str
    name: str
    dream_role: str
    resume: bytes

# Define a data model for the check_user request
class CheckUserRequest(BaseModel):
    email: str

# Define a data model for the validate_session request
class ValidateSessionRequest(BaseModel):
    session_id: str

@app.middleware("http")
async def log_requests(request: Request, call_next):
    Logger.log_request(request)
    try:
        response = await call_next(request)
        Logger.log_success(f"Processed request for {request.url}")
        return response
    except Exception as e:
        Logger.log_error(e)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.post("/ask")
async def ask_question(question: Question, request: Request):
    user_id = request.headers.get('user_id')
    conversation_id = request.headers.get('conversation_id')
    
    if not user_id:
        raise HTTPException(status_code=400, detail="User-ID header is missing")
    if not conversation_id:
        raise HTTPException(status_code=400, detail="Conversation-ID header is missing")

    try:
        # Save the user's question
        logging.info(f"Saving conversation for user_id: {user_id}, conversation_id: {conversation_id} with question: {question.question}")
        aws_helper.save_conversation(user_id, conversation_id, 'user', question.question)

        # Retrieve conversation history
        conversation_history = aws_helper.get_conversation_history(user_id, conversation_id)

        # Get the answer from OpenAI with full conversation context
        answer = openai_helper.get_response(question.question, conversation_history)

        # Save the adviser's answer
        aws_helper.save_conversation(user_id, conversation_id, 'adviser', answer)

        Logger.log_success(f"Generated response for question: {question.question}")
        return {"answer": answer}
    except Exception as e:
        Logger.log_error(e)
        raise HTTPException(status_code=500, detail="Error processing question")

@app.post("/onboard")
async def onboard_user(data: OnboardingData):
    try:
        # Save the user and get the user_id
        user_id = aws_helper.save_user(data.email, data.name, data.dream_role, data.resume)
        
        # Create a new session for the user
        session_id = aws_helper.create_session(user_id)
        
        # Send an email with the session_id in the URL
        aws_helper.send_email(
            data.email,
            'Welcome to AI Career Adviser',
            f"Hello {data.name},\n\nWelcome to AI Career Adviser! Click the link below to start your journey:\n\nhttp://localhost:8000?sessionid={session_id}\n\nBest,\nAI Career Adviser Team"
        )
        Logger.log_success(f"Onboarded user: {data.email} with session ID: {session_id}")
        return {"message": "Onboarding successful"}
    except Exception as e:
        Logger.log_error(e)
        raise HTTPException(status_code=500, detail="Error during onboarding")

@app.post("/check_user")
async def check_user(request: CheckUserRequest):
    email = request.email
    Logger.log_success(f"Received request to check user: {email}")
    try:
        user_id = aws_helper.check_user_exists(email)
        if user_id:
            Logger.log_success(f"User exists: {email} with user_id: {user_id}")
            session_id = aws_helper.create_session(user_id)
            Logger.log_success(f"Created session ID: {session_id} for user: {email}")
            aws_helper.send_email(
                email,
                'Your Login Link for AI Career Adviser',
                f"Hello,\n\nClick the link below to log in:\n\nhttp://localhost:8000?sessionid={session_id}\n\nBest,\nAI Career Adviser Team"
            )
            Logger.log_success(f"Sent login link to user: {email}")
            return {"onboarded": True, "user_id": user_id}
        else:
            Logger.log_success(f"User not found: {email}")
            return {"onboarded": False}
    except Exception as e:
        Logger.log_error(e)
        raise HTTPException(status_code=500, detail="Error checking user status")

@app.post("/validate_session")
async def validate_session(request: ValidateSessionRequest):
    session_id = request.session_id
    Logger.log_success(f"Received session ID for validation: {session_id}")
    try:
        user_id = aws_helper.validate_session(session_id)  # Assume this returns user_id if valid
        if user_id:
            Logger.log_success(f"Validated session: {session_id} for user: {user_id}")
            return {"valid": True, "user_id": user_id}
        Logger.log_success(f"Session invalid or expired: {session_id}")
        return {"valid": False}
    except Exception as e:
        Logger.log_error(e)
        raise HTTPException(status_code=500, detail="Error validating session")

@app.post("/get_resume")
async def get_resume(request: Request):
    user_id = request.headers.get('user_id')
    if not user_id:
        raise HTTPException(status_code=400, detail="User-ID header is missing")
    
    try:
        # Fetch resume from aica_user table
        resume = aws_helper.get_user_resume(user_id)
        
        # Fetch skills from aica_user_skills table
        skills = aws_helper.get_user_skills(user_id)

        return {"resume": resume, "skills": skills}
    except Exception as e:
        Logger.log_error(e)
        raise HTTPException(status_code=500, detail="Error fetching resume and skills")

@app.post("/remove_account")
async def remove_account(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    if not user_id:
        raise HTTPException(status_code=400, detail="User-ID is required")

    try:
        # Logic to remove user account and associated data
        aws_helper.remove_user_account(user_id)
        return {"message": "Account removed successfully"}
    except Exception as e:
        Logger.log_error(e)
        raise HTTPException(status_code=500, detail="Error removing account") 