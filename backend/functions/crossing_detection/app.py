"""
Crossing Detection Lambda Function
Detects real-time ADR level crossings and triggers alerts
Designed for polling-based approach (triggered every 1-5 minutes during market hours)
"""

import json
import os
import boto3
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import hashlib
from aws_lambda_powertools import Logger

logger = Logger()
dynamodb = boto3.resource('dynamodb')
sns_client = boto3.client('sns')
s3_client = boto3.client('s3')

# Environment variables
ADR_LEVELS_TABLE = os.environ.get('DYNAMODB_TABLE_LEVELS')
CROSSINGS_TABLE = os.environ.get('DYNAMODB_TABLE_CROSSINGS')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

# State tracking to prevent duplicate alerts
CROSSING_STATE = {}  # In-memory cache (reset on Lambda cold start)


class FyersQuoteProvider:
    """Fetch live quotes from Fyers API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.fyers.in/api/v3"
    
    def get_ltp(self, symbol: str) -> Optional[Dict]:
        """
        Get Last Traded Price for a symbol
        
        Args:
            symbol: Stock symbol (e.g., 'INFY')
            
        Returns:
            Dictionary with quote info or None
        """
        try:
            import requests
            
            fyers_symbol = f"NSE:{symbol}-EQ"
            
            params = {
                'symbols': fyers_symbol
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.get(
                f"{self.base_url}/quotes",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('s') == 'ok' and fyers_symbol in data:
                    quote = data[fyers_symbol]
                    return {
                        'ltp': quote.get('v', {}).get('ltp', 0),
                        'volume': quote.get('v', {}).get('vol', 0),
                        'timestamp': datetime.utcnow().isoformat()
                    }
            
            logger.warning(f"Failed to get quote for {symbol}: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch LTP for {symbol}: {str(e)}")
            return None
    
    def get_ltps_batch(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Get LTP for multiple symbols
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary mapping symbol to quote info
        """
        try:
            import requests
            
            fyers_symbols = [f"NSE:{sym}-EQ" for sym in symbols]
            
            params = {
                'symbols': ','.join(fyers_symbols)
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.get(
                f"{self.base_url}/quotes",
                params=params,
                headers=headers,
                timeout=10
            )
            
            quotes = {}
            if response.status_code == 200:
                data = response.json()
                if data.get('s') == 'ok':
                    for fyers_symbol, quote_data in data.items():
                        symbol = fyers_symbol.split(':')[1].split('-')[0]
                        quotes[symbol] = {
                            'ltp': quote_data.get('v', {}).get('ltp', 0),
                            'volume': quote_data.get('v', {}).get('vol', 0),
                            'timestamp': datetime.utcnow().isoformat()
                        }
            
            return quotes
            
        except Exception as e:
            logger.error(f"Batch quote fetch failed: {str(e)}")
            return {}


class CrossingDetector:
    """Detect ADR level crossings"""
    
    @staticmethod
    def get_adr_levels(symbol: str) -> Optional[Dict]:
        """Get today's ADR levels from DynamoDB"""
        try:
            table = dynamodb.Table(ADR_LEVELS_TABLE)
            today = datetime.utcnow().strftime('%Y-%m-%d')
            
            response = table.get_item(
                Key={
                    'symbol': symbol,
                    'calculation_date': today
                }
            )
            
            if 'Item' in response:
                return response['Item']
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get ADR levels for {symbol}: {str(e)}")
            return None
    
    @staticmethod
    def detect_crossing(symbol: str, ltp: float, levels: Dict) -> Optional[str]:
        """
        Detect if a crossing occurred
        
        Args:
            symbol: Stock symbol
            ltp: Last Traded Price
            levels: ADR levels data
            
        Returns:
            'UPPER', 'LOWER', or None
        """
        upper = levels.get('upper_level', 0)
        lower = levels.get('lower_level', 0)
        
        if ltp >= upper:
            return 'UPPER'
        elif ltp <= lower:
            return 'LOWER'
        
        return None
    
    @staticmethod
    def is_duplicate_alert(symbol: str, direction: str, today: str) -> bool:
        """
        Check if we already alerted for this symbol/direction today
        Uses in-memory cache and DynamoDB check
        """
        crossing_key = f"{symbol}_{direction}_{today}"
        
        # Check in-memory cache (fast path)
        if crossing_key in CROSSING_STATE:
            return True
        
        # Check DynamoDB (persistent check)
        try:
            table = dynamodb.Table(CROSSINGS_TABLE)
            response = table.query(
                IndexName='SymbolDateIndex',
                KeyConditionExpression='symbol = :symbol AND crossing_date = :date',
                ExpressionAttributeValues={
                    ':symbol': symbol,
                    ':date': today
                }
            )
            
            # Check if any crossing with same direction exists
            for item in response.get('Items', []):
                if item.get('direction') == direction:
                    CROSSING_STATE[crossing_key] = True
                    return True
            
        except Exception as e:
            logger.error(f"Duplicate check failed for {symbol}: {str(e)}")
            # Fail safe: assume not duplicate if check fails
            return False
        
        # Mark as seen
        CROSSING_STATE[crossing_key] = True
        return False


def record_crossing(
    symbol: str,
    direction: str,
    ltp: float,
    levels: Dict,
    volume: int
) -> str:
    """
    Record a crossing event in DynamoDB
    
    Args:
        symbol: Stock symbol
        direction: 'UPPER' or 'LOWER'
        ltp: Last Traded Price at crossing
        levels: ADR levels data
        volume: Volume at crossing
        
    Returns:
        Crossing ID
    """
    try:
        table = dynamodb.Table(CROSSINGS_TABLE)
        today = datetime.utcnow().strftime('%Y-%m-%d')
        now = datetime.utcnow()
        
        # Generate unique crossing ID
        crossing_id = hashlib.md5(
            f"{symbol}_{direction}_{today}_{now.isoformat()}".encode()
        ).hexdigest()
        
        anchor_price = levels.get('anchor_price', 0)
        percentage_move = ((ltp - anchor_price) / anchor_price * 100) if anchor_price > 0 else 0
        
        item = {
            'crossing_id': crossing_id,
            'symbol': symbol,
            'direction': direction,
            'crossing_date': today,
            'crossing_timestamp': now.isoformat(),
            'ltp_at_crossing': round(ltp, 2),
            'level_value': levels.get('upper_level' if direction == 'UPPER' else 'lower_level', 0),
            'volume_at_crossing': volume,
            'volume_vs_avg': round(volume / (volumes.get('avg_volume', 1) or 1), 2),
            'anchor_price': anchor_price,
            'percentage_move': round(percentage_move, 2),
            'adr': levels.get('adr', 0),
            'adr_pct': levels.get('adr_pct', 0),
            'status': 'ACTIVE',
            'recorded_at': now.isoformat(),
            'ttl': int((now + timedelta(days=90)).timestamp())
        }
        
        table.put_item(Item=item)
        logger.info(f"Recorded crossing: {symbol} {direction} at {ltp}")
        
        return crossing_id
        
    except Exception as e:
        logger.error(f"Failed to record crossing for {symbol}: {str(e)}")
        return None


def publish_alert(crossing_data: Dict):
    """
    Publish crossing alert to SNS
    Will be picked up by WhatsApp alert function
    
    Args:
        crossing_data: Dictionary with crossing details
    """
    try:
        message = {
            'type': 'crossing_alert',
            'symbol': crossing_data['symbol'],
            'direction': crossing_data['direction'],
            'ltp': crossing_data['ltp_at_crossing'],
            'level': crossing_data['level_value'],
            'volume_vs_avg': crossing_data['volume_vs_avg'],
            'timestamp': crossing_data['recorded_at']
        }
        
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(message),
            Subject=f"ADR Alert: {crossing_data['symbol']} {crossing_data['direction']}"
        )
        
        logger.info(f"Alert published for {crossing_data['symbol']}")
        
    except Exception as e:
        logger.error(f"Failed to publish alert: {str(e)}")


def detect_and_process_crossings(symbols: List[str], api_key: str) -> Dict:
    """
    Main detection function
    
    Args:
        symbols: List of symbols to check
        api_key: Fyers API key
        
    Returns:
        Detection results
    """
    provider = FyersQuoteProvider(api_key)
    detector = CrossingDetector()
    
    today = datetime.utcnow().strftime('%Y-%m-%d')
    crossings_detected = []
    
    # Fetch all quotes in batch
    quotes = provider.get_ltps_batch(symbols)
    
    for symbol in symbols:
        try:
            # Get quote
            if symbol not in quotes:
                logger.warning(f"No quote for {symbol}")
                continue
            
            quote = quotes[symbol]
            ltp = quote['ltp']
            volume = quote['volume']
            
            # Get ADR levels
            levels = detector.get_adr_levels(symbol)
            if not levels:
                logger.warning(f"No ADR levels for {symbol}")
                continue
            
            # Detect crossing
            direction = detector.detect_crossing(symbol, ltp, levels)
            if not direction:
                continue
            
            # Check for duplicate
            if detector.is_duplicate_alert(symbol, direction, today):
                logger.info(f"Duplicate alert skipped for {symbol} {direction}")
                continue
            
            # Record crossing
            crossing_id = record_crossing(symbol, direction, ltp, levels, volume)
            if not crossing_id:
                continue
            
            # Build crossing data
            anchor_price = levels.get('anchor_price', 0)
            percentage_move = ((ltp - anchor_price) / anchor_price * 100) if anchor_price > 0 else 0
            
            crossing_data = {
                'crossing_id': crossing_id,
                'symbol': symbol,
                'direction': direction,
                'ltp_at_crossing': ltp,
                'level_value': levels.get('upper_level' if direction == 'UPPER' else 'lower_level', 0),
                'volume_at_crossing': volume,
                'volume_vs_avg': round(volume / (levels.get('avg_volume', 1) or 1), 2),
                'percentage_move': round(percentage_move, 2),
                'adr_pct': levels.get('adr_pct', 0),
                'recorded_at': datetime.utcnow().isoformat()
            }
            
            # Publish alert
            publish_alert(crossing_data)
            crossings_detected.append(crossing_data)
            
        except Exception as e:
            logger.error(f"Error processing {symbol}: {str(e)}")
            continue
    
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'crossings_detected': len(crossings_detected),
        'crossings': crossings_detected
    }


@logger.inject_lambda_context
def lambda_handler(event, context):
    """
    Lambda handler for crossing detection
    Can be triggered by EventBridge on a schedule (every 1-5 minutes during market hours)
    
    Sample event:
    {
        "symbols": ["INFY", "TCS", "HDFCBANK"],
        "api_key": "..."
    }
    """
    try:
        # For now, use the hardcoded NIFTY 50 list
        # In production, could be parameterized per user
        nifty_50_symbols = [
            'ADANIGREEN', 'ADANIENT', 'APOLLOHOSP', 'ASIANPAINT', 'AXISBANK',
            'BAJAJFINSV', 'BAJAJHLDNG', 'BAJAJTWN', 'BHARTIARTL', 'BHEL',
            'BPCL', 'BRITANNIA', 'COALINDIA', 'COLPAL', 'DIVISLAB',
            'DLF', 'DRREDDY', 'EICHERMOT', 'GAIL', 'GRASIM',
            'HDFCBANK', 'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDPETRO',
            'HINDUNILVR', 'ICICIBANK', 'ICICIPRULI', 'IDFCFIRSTB', 'INDIGO',
            'INDUSINDBK', 'INFY', 'JSWSTEEL', 'KOTAKBANK', 'LT',
            'LTIM', 'MARUTI', 'NESTLEIND', 'NTPC', 'ONGC',
            'POWERGRID', 'RELIANCE', 'SBIN', 'SBILIFE', 'SUNPHARMA',
            'TCS', 'TECHM', 'TITAN', 'TRENT', 'UPL',
            'VBL', 'WIPRO', 'ZEEL'
        ]
        
        api_key = os.environ.get('FYERS_API_KEY')
        
        result = detect_and_process_crossings(nifty_50_symbols, api_key)
        
        logger.info(f"Crossing detection complete: {result}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.exception(f"Crossing detection failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
