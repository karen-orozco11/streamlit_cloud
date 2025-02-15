from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import boto3
import uuid
from datetime import datetime
from skill_extractor import SkillExtractor
from logger import Logger
import logging
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Suppress boto3 and botocore debug logs
logging.getLogger('boto3').setLevel(logging.INFO)
logging.getLogger('botocore').setLevel(logging.INFO)

app = FastAPI()

dynamodb = boto3.resource('dynamodb', region_name='your-region')
task_table = dynamodb.Table('aica_task')
user_table = dynamodb.Table('aica_user')
user_skills_table = dynamodb.Table('aica_user_skills')

skill_extractor = SkillExtractor()

class SkillExtractionRequest(BaseModel):
    user_id: str

@app.post("/extract_skills")
async def extract_skills(request: SkillExtractionRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    Logger.log_info(f"Received skill extraction request for user_id: {request.user_id}")

    try:
        task_table.put_item(
            Item={
                'task_id': task_id,
                'user_id': request.user_id,
                'task_status': 'new',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
        )
        Logger.log_success(f"Task created with task_id: {task_id}")

        background_tasks.add_task(process_skill_extraction, task_id)
        return {"task_id": task_id}
    except Exception as e:
        Logger.log_error(e)
        raise HTTPException(status_code=500, detail="Error creating task")

def redact_pii(text):
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()

    # Detect PII
    results = analyzer.analyze(text=text, entities=["PHONE_NUMBER", "PERSON", "LOCATION"], language='en')

    # Redact PII
    redacted_text = anonymizer.anonymize(text, results)
    return redacted_text

def process_skill_extraction(task_id):
    try:
        # Retrieve task details
        task = task_table.get_item(Key={'task_id': task_id})['Item']
        user_id = task['user_id']
        Logger.log_info(f"Processing skill extraction for task_id: {task_id}, user_id: {user_id}")

        # Retrieve user resume
        user = user_table.get_item(Key={'user_id': user_id})['Item']
        resume = user['resume']
        Logger.log_info(f"Retrieved resume for user_id: {user_id}")

        # Redact PII from resume
        redacted_resume = redact_pii(resume)
        Logger.log_info(f"Redacted PII from resume for user_id: {user_id}")

        # Update the user table with the redacted resume
        user_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression="set resume=:r",
            ExpressionAttributeValues={
                ':r': redacted_resume
            }
        )
        Logger.log_success(f"Updated user table with redacted resume for user_id: {user_id}")

        # Use SkillExtractor to extract skills from the redacted resume
        skills = skill_extractor.extract_skills(redacted_resume)
        Logger.log_success(f"Extracted skills for user_id: {user_id}")

        # Save skills to user_skills_table
        user_skills_table.put_item(
            Item={
                'user_id': user_id,
                'role': 'data_scientist',
                'skills': skills
            }
        )
        Logger.log_success(f"Saved skills for user_id: {user_id}")

        # Update task status
        task_table.update_item(
            Key={'task_id': task_id},
            UpdateExpression="set task_status=:s, updated_at=:u",
            ExpressionAttributeValues={
                ':s': 'completed',
                ':u': datetime.utcnow().isoformat()
            }
        )
        Logger.log_success(f"Task completed for task_id: {task_id}")
    except Exception as e:
        Logger.log_error(e)
        raise
