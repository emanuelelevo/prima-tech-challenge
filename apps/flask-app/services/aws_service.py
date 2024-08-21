import boto3
from werkzeug.utils import secure_filename
import uuid
from flask import current_app as app
import logging

logger = logging.getLogger(__name__)

def get_boto3_client(service):
    return boto3.client(service, region_name=app.config['AWS_REGION'])

def get_users_from_dynamodb():
    dynamodb = get_boto3_client('dynamodb')
    try:
        response = dynamodb.scan(TableName=app.config['DYNAMODB_TABLE'])
        users = []
        for item in response['Items']:
            user = {
                "name": item['name']['S'],
                "email": item['email']['S'],
                "avatar_url": item['avatar_url']['S']
            }
            users.append(user)
        return users
    except Exception as e:
        logger.error("Error fetching users from DynamoDB", exc_info=True)
        raise

def save_user_to_dynamodb(name, email, avatar_url):
    dynamodb = get_boto3_client('dynamodb')
    try:
        dynamodb.put_item(
            TableName=app.config['DYNAMODB_TABLE'],
            Item={
                'name': {'S': name},
                'email': {'S': email},
                'avatar_url': {'S': avatar_url}
            }
        )
    except Exception as e:
        logger.error("Error saving user to DynamoDB", exc_info=True)
        raise

def upload_file_to_s3(file):
    s3 = get_boto3_client('s3')
    try:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        s3.upload_fileobj(file, app.config['S3_BUCKET'], unique_filename)
        avatar_url = f"https://{app.config['S3_BUCKET']}.s3.amazonaws.com/{unique_filename}"
        logger.info("Uploaded file to S3")
        return avatar_url
    except Exception as e:
        logger.error("Error uploading file to S3", exc_info=True)
        raise
