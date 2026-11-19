"""
WhatsApp Alert Lambda Function
Sends WhatsApp notifications for ADR level crossings
Triggered by SQS events from SNS
"""

import json
import os
import boto3
from datetime import datetime
from typing import Dict, Optional
import requests
from aws_lambda_powertools import Logger

logger = Logger()
dynamodb = boto3.resource('dynamodb')
secretsmanager = boto3.client('secretsmanager')

USER_SETTINGS_TABLE = os.environ.get('DYNAMODB_TABLE_SETTINGS', 'adr-scanner-user-settings')


class WhatsAppNotificationService:
    """Send WhatsApp notifications via Twilio or similar provider"""
    
    def __init__(self, api_key: str, api_url: str = None):
        self.api_key = api_key
        self.api_url = api_url or "https://api.whatsapp.com/send"
        # For production: use Twilio WhatsApp API, AWS SNS, or similar
        # This is a placeholder implementation
    
    def send_crossing_alert(
        self,
        recipient_number: str,
        symbol: str,
        direction: str,
        ltp: float,
        level: float,
        adr_pct: float,
        volume_vs_avg: float
    ) -> bool:
        """
        Send crossing alert via WhatsApp
        
        Args:
            recipient_number: WhatsApp number (with country code, e.g., +919876543210)
            symbol: Stock symbol
            direction: 'UPPER' or 'LOWER'
            ltp: Last Traded Price
            level: ADR level crossed
            adr_pct: ADR percentage
            volume_vs_avg: Volume vs average ratio
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            message = self._format_alert_message(
                symbol, direction, ltp, level, adr_pct, volume_vs_avg
            )
            
            # TODO: Implement actual WhatsApp sending
            # Option 1: Twilio WhatsApp API
            # Option 2: AWS SNS with SNS to WhatsApp provider
            # Option 3: Custom webhook to WhatsApp gateway
            
            logger.info(f"WhatsApp message prepared for {recipient_number}: {message}")
            
            # Placeholder: In production, use Twilio or similar
            # response = self._send_via_twilio(recipient_number, message)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp alert: {str(e)}")
            return False
    
    def _format_alert_message(
        self,
        symbol: str,
        direction: str,
        ltp: float,
        level: float,
        adr_pct: float,
        volume_vs_avg: float
    ) -> str:
        """Format crossing alert message"""
        direction_text = "Upper ADR" if direction == "UPPER" else "Lower ADR"
        emoji = "📈" if direction == "UPPER" else "📉"
        
        message = f"""
{emoji} ADR ALERT - {symbol}

Direction: {direction_text}
Current Price: ₹{ltp:.2f}
Level: ₹{level:.2f}
ADR %: {adr_pct:.2f}%
Volume: {volume_vs_avg:.1f}x Avg

Time: {datetime.utcnow().strftime('%H:%M:%S')}

*For information and education only. Not investment advice.*
        """.strip()
        
        return message
    
    def _send_via_twilio(self, recipient_number: str, message: str) -> bool:
        """Send via Twilio WhatsApp API"""
        try:
            # Get Twilio credentials
            # This would normally be retrieved from Secrets Manager
            
            payload = {
                'To': f"whatsapp:{recipient_number}",
                'From': 'whatsapp:YOUR_TWILIO_NUMBER',  # Configure in Secrets Manager
                'Body': message
            }
            
            # Make request to Twilio
            # response = requests.post(url, data=payload, auth=(account_sid, auth_token))
            # return response.status_code == 201
            
            return True
            
        except Exception as e:
            logger.error(f"Twilio send failed: {str(e)}")
            return False


def get_user_alert_settings(user_id: str) -> Optional[Dict]:
    """Retrieve user's alert preferences"""
    try:
        table = dynamodb.Table(USER_SETTINGS_TABLE)
        response = table.get_item(Key={'user_id': user_id})
        
        if 'Item' in response:
            item = response['Item']
            # Only return if WhatsApp alerts enabled
            if item.get('alerts_enabled') and item.get('alert_channel') == 'whatsapp':
                return item
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to get user settings: {str(e)}")
        return None


def get_whatsapp_credentials() -> Dict:
    """Retrieve WhatsApp API credentials from Secrets Manager"""
    try:
        response = secretsmanager.get_secret_value(
            SecretId='whatsapp-credentials'
        )
        
        if 'SecretString' in response:
            return json.loads(response['SecretString'])
        
        return {}
        
    except Exception as e:
        logger.error(f"Failed to retrieve WhatsApp credentials: {str(e)}")
        return {}


@logger.inject_lambda_context
def lambda_handler(event, context):
    """
    Lambda handler for WhatsApp alert processing
    Receives events from SQS triggered by SNS
    
    SQS Event structure:
    {
        Records: [{
            Sns: {
                Message: {
                    type: 'crossing_alert',
                    symbol: 'INFY',
                    direction: 'UPPER',
                    ltp: 2150.50,
                    level: 2145.00,
                    volume_vs_avg: 1.5,
                    timestamp: '...'
                }
            }
        }]
    }
    """
    
    processed_count = 0
    failed_count = 0
    
    try:
        # Get WhatsApp credentials
        credentials = get_whatsapp_credentials()
        if not credentials:
            logger.warning("No WhatsApp credentials found")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'WhatsApp credentials not configured'})
            }
        
        # Initialize WhatsApp service
        whatsapp_service = WhatsAppNotificationService(
            api_key=credentials.get('api_key'),
            api_url=credentials.get('api_url')
        )
        
        # Process each SQS record
        records = event.get('Records', [])
        
        for record in records:
            try:
                # Parse SNS message from SQS
                sns_message = json.loads(record['Sns']['Message'])
                
                symbol = sns_message.get('symbol')
                direction = sns_message.get('direction')
                ltp = sns_message.get('ltp')
                level = sns_message.get('level')
                volume_vs_avg = sns_message.get('volume_vs_avg', 0)
                adr_pct = sns_message.get('adr_pct', 0)
                
                # TODO: Retrieve user ID from message and get their settings
                # For now, use placeholder
                user_id = sns_message.get('user_id', 'default')
                user_settings = get_user_alert_settings(user_id)
                
                if not user_settings:
                    logger.warning(f"No WhatsApp settings for user {user_id}")
                    continue
                
                whatsapp_number = user_settings.get('whatsapp_number')
                if not whatsapp_number:
                    logger.warning(f"No WhatsApp number for user {user_id}")
                    continue
                
                # Send alert
                success = whatsapp_service.send_crossing_alert(
                    recipient_number=whatsapp_number,
                    symbol=symbol,
                    direction=direction,
                    ltp=ltp,
                    level=level,
                    adr_pct=adr_pct,
                    volume_vs_avg=volume_vs_avg
                )
                
                if success:
                    processed_count += 1
                    logger.info(f"WhatsApp alert sent for {symbol} to {whatsapp_number}")
                else:
                    failed_count += 1
                    logger.error(f"Failed to send WhatsApp alert for {symbol}")
                
            except Exception as e:
                logger.error(f"Error processing record: {str(e)}")
                failed_count += 1
                continue
        
        logger.info(f"WhatsApp alert processing complete: {processed_count} sent, {failed_count} failed")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'processed': processed_count,
                'failed': failed_count
            })
        }
        
    except Exception as e:
        logger.exception(f"WhatsApp alert handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
