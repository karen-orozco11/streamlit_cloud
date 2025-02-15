import boto3
import logging
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from datetime import datetime, timedelta
import uuid
from boto3.dynamodb.conditions import Key

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class AWSHelper:
    def __init__(self, region_name='your-region'):
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.ses_client = boto3.client('ses', region_name=region_name)
        self.conversation_table = self.dynamodb.Table('aica_conversation')
        logging.info(f"AWSHelper initialized with region: {region_name}")

    def save_user(self, email, name, dream_role, resume):
        logging.debug(f"Saving user: {email}, {name}, {dream_role}")
        user_table = self.dynamodb.Table('aica_user')
        user_id = str(uuid.uuid4())
        user_table.put_item(
            Item={
                'user_id': user_id,
                'email': email,
                'name': name,
                'dream_role': dream_role,
                'resume': resume
            }
        )
        logging.info(f"User saved: {email} with user_id: {user_id}")
        return user_id

    def create_session(self, user_id):
        logging.debug(f"Creating session for user_id: {user_id}")
        session_table = self.dynamodb.Table('aica_session')
        session_id = str(uuid.uuid4())
        expiry_time = datetime.utcnow() + timedelta(hours=240)
        session_table.put_item(
            Item={
                'user_id': user_id,
                'session_id': session_id,
                'expiry_time': expiry_time.isoformat()
            }
        )
        logging.info(f"Session created: {session_id} for user_id: {user_id}")
        return session_id

    def send_email(self, email, subject, body):
        logging.debug(f"Sending email to: {email}, subject: {subject}")
        self.ses_client.send_email(
            Source='willmusing@berkeley.edu',
            Destination={
                'ToAddresses': [email],
            },
            Message={
                'Subject': {
                    'Data': subject,
                },
                'Body': {
                    'Text': {
                        'Data': body,
                    }
                }
            }
        )
        logging.info(f"Email sent to: {email}")

    def check_user_exists(self, email):
        logging.debug(f"Checking if user exists: {email}")
        user_table = self.dynamodb.Table('aica_user')
        response = user_table.get_item(Key={'email': email})
        if 'Item' in response:
            user_id = response['Item'].get('user_id')  # Retrieve the user_id
            logging.info(f"User exists: True for email: {email}, user_id: {user_id}")
            return user_id
        logging.info(f"User exists: False for email: {email}")
        return None

    def validate_session(self, session_id):
        logging.debug(f"Validating session: {session_id}")
        session_table = self.dynamodb.Table('aica_session')
        try:
            # Query the table using the session_id as the partition key
            response = session_table.query(
                KeyConditionExpression=Key('session_id').eq(session_id)
            )
            if response['Items']:
                session = response['Items'][0]  # Assuming session_id is unique
                if datetime.fromisoformat(session['expiry_time']) > datetime.utcnow():
                    user_id = session.get('user_id')
                    logging.info(f"Session valid: True for session_id: {session_id}, user_id: {user_id}")
                    return user_id
            logging.info(f"Session not found or expired for session_id: {session_id}")
            return None
        except Exception as e:
            logging.error(f"Error validating session: {e}")
            return None

    def save_conversation(self, user_id, conversation_id, role, text):
        timestamp = datetime.utcnow().isoformat()
        unique_sort_key = f"{conversation_id}#{timestamp}"
        self.conversation_table.put_item(
            Item={
                'user_id': user_id,
                'conversation_id': unique_sort_key,  # Use unique sort key
                'role': role,
                'text': text,
                'datetime': timestamp
            }
        )

    def get_conversation_history(self, user_id, conversation_id):
        try:
            response = self.conversation_table.query(
                KeyConditionExpression=Key('user_id').eq(user_id) & Key('conversation_id').begins_with(conversation_id),
                ScanIndexForward=True  # Ensures the results are in ascending order by timestamp
            )
            return response.get('Items', [])
        except Exception as e:
            logging.error(f"Error retrieving conversation history: {e}")
            return []

    def get_user_resume(self, user_id):
        logging.debug(f"Fetching resume for user_id: {user_id}")
        user_table = self.dynamodb.Table('aica_user')
        try:
            # Query using the GSI with user_id as the partition key
            response = user_table.query(
                IndexName='UserIdIndex',  # Replace with your actual GSI name
                KeyConditionExpression=Key('user_id').eq(user_id)
            )
            if response['Items']:
                resume = response['Items'][0].get('resume', "No resume found.")
                logging.info(f"Resume fetched for user_id: {user_id}")
                return resume
            else:
                logging.info(f"No resume found for user_id: {user_id}")
                return "No resume found."
        except Exception as e:
            logging.error(f"Error fetching resume for user_id {user_id}: {e}")
            return "Error fetching resume."

    def get_user_skills(self, user_id):
        logging.debug(f"Fetching skills for user_id: {user_id}")
        skills_table = self.dynamodb.Table('aica_user_skills')
        try:
            # Query using only the partition key (user_id)
            response = skills_table.query(
                KeyConditionExpression=Key('user_id').eq(user_id)
            )
            skills = []
            for item in response.get('Items', []):
                skills.extend(item.get('skills', []))
            logging.info(f"Skills fetched for user_id: {user_id}")
            return skills
        except Exception as e:
            logging.error(f"Error fetching skills for user_id {user_id}: {e}")
            return []

    def remove_user_account(self, user_id):
        logging.debug(f"Removing account for user_id: {user_id}")
        user_table = self.dynamodb.Table('aica_user')
        skills_table = self.dynamodb.Table('aica_user_skills')
        session_table = self.dynamodb.Table('aica_session')
        conversation_table = self.dynamodb.Table('aica_conversation')

        try:
            # Delete user data
            user_table.delete_item(Key={'user_id': user_id})
            skills_table.delete_item(Key={'user_id': user_id})
            session_table.delete_item(Key={'user_id': user_id})
            # Delete all conversations for the user
            response = conversation_table.query(
                KeyConditionExpression=Key('user_id').eq(user_id)
            )
            for item in response['Items']:
                conversation_table.delete_item(
                    Key={
                        'user_id': item['user_id'],
                        'conversation_id': item['conversation_id']
                    }
                )
            logging.info(f"Account removed for user_id: {user_id}")
        except Exception as e:
            logging.error(f"Error removing account for user_id {user_id}: {e}")
            raise