"""
Authentication Lambda function using Amazon Cognito
Handles user login and token generation
"""

import json
import os
import boto3
import hashlib
import hmac
import base64
from datetime import datetime
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.validation import validate

logger = Logger()
cognito_client = boto3.client('cognito-idp')
dynamodb = boto3.resource('dynamodb')

COGNITO_USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID')
COGNITO_CLIENT_ID = os.environ.get('COGNITO_CLIENT_ID')
USER_SETTINGS_TABLE = os.environ.get('DYNAMODB_TABLE_SETTINGS', 'adr-scanner-user-settings')


def get_secret_hash(username, client_id, client_secret):
    """Generate Cognito SecretHash for client authentication"""
    message = bytes(username + client_id, 'utf-8')
    key = bytes(client_secret, 'utf-8')
    secret_hash = base64.b64encode(
        hmac.new(key, message, digestmod=hashlib.sha256).digest()
    ).decode()
    return secret_hash


@logger.inject_lambda_context
def lambda_handler(event, context):
    """
    Handle user login request
    
    Request body:
    {
        "email": "user@example.com",
        "password": "password123",
        "remember_me": true/false
    }
    """
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
        password = body.get('password')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Email and password are required'})
            }
        
        # Authenticate user with Cognito
        auth_response = cognito_client.admin_initiate_auth(
            UserPoolId=COGNITO_USER_POOL_ID,
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )
        
        # Extract tokens
        id_token = auth_response['AuthenticationResult']['IdToken']
        access_token = auth_response['AuthenticationResult']['AccessToken']
        refresh_token = auth_response['AuthenticationResult']['RefreshToken']
        expires_in = auth_response['AuthenticationResult']['ExpiresIn']
        
        # Get user info from Cognito
        user_info = cognito_client.get_user(AccessToken=access_token)
        
        # Initialize user settings if first login
        user_id = user_info['Username']
        initialize_user_settings(user_id, email)
        
        logger.info(f"User {email} successfully authenticated")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'user_id': user_id,
                'email': email,
                'id_token': id_token,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': expires_in
            })
        }
        
    except cognito_client.exceptions.NotAuthorizedException:
        logger.warning(f"Authentication failed for {body.get('email')}")
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Invalid email or password'})
        }
    except cognito_client.exceptions.UserNotFoundException:
        logger.warning(f"User not found: {body.get('email')}")
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'User does not exist'})
        }
    except Exception as e:
        logger.exception(f"Authentication error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Authentication failed'})
        }


def initialize_user_settings(user_id, email):
    """Initialize default user settings on first login"""
    try:
        table = dynamodb.Table(USER_SETTINGS_TABLE)
        
        # Check if settings already exist
        response = table.get_item(Key={'user_id': user_id})
        if 'Item' in response:
            return
        
        # Default settings for new user
        default_settings = {
            'user_id': user_id,
            'email': email,
            'created_at': datetime.utcnow().isoformat(),
            'adr_period': 14,
            'multiplier': 1.0,
            'anchor': 'open',  # 'open' or 'close'
            'universe': 'NIFTY_50',
            'min_price': 20.0,
            'min_volume': 100000,
            'alerts_enabled': True,
            'alert_channel': 'whatsapp',
            'whatsapp_number': '',
            'crossing_type': 'both',  # 'upper', 'lower', 'both'
        }
        
        table.put_item(Item=default_settings)
        logger.info(f"Initialized default settings for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to initialize user settings: {str(e)}")
        # Don't fail the login process if settings initialization fails
        pass
