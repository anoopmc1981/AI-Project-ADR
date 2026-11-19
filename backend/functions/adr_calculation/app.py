"""
ADR Calculation Lambda Function
Calculates ADR (Average Daily Range) levels for NSE stocks before market open
Uses Fyers API for market data
"""

import json
import os
import boto3
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from aws_lambda_powertools import Logger

logger = Logger()
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Environment variables
ADR_LEVELS_TABLE = os.environ.get('DYNAMODB_TABLE_LEVELS')
OHLCV_BUCKET = os.environ.get('S3_BUCKET_OHLCV')
FYERS_API_KEY = os.environ.get('FYERS_API_KEY')

# Constants
NIFTY_50_SYMBOLS = [
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

DEFAULT_ADR_PERIOD = 14
DEFAULT_MULTIPLIER = 1.0
DEFAULT_ANCHOR = 'open'  # 'open' or 'close'


class FyersDataProvider:
    """Interface with Fyers API for market data"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.fyers.in/api/v3"
        
    def get_historical_data(self, symbol: str, period: int = 60) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data from Fyers
        
        Args:
            symbol: Stock symbol (e.g., 'INFY')
            period: Number of days of historical data to fetch
            
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        try:
            import requests
            
            # Fyers requires NSE:SYMBOL format
            fyers_symbol = f"NSE:{symbol}-EQ"
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period)
            
            params = {
                'symbol': fyers_symbol,
                'resolution': 'D',  # Daily resolution
                'date_format': 'normal',
                'range_from': int(start_date.timestamp()),
                'range_to': int(end_date.timestamp()),
                'cont_flag': 'OFF'
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.get(
                f"{self.base_url}/history",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('s') == 'ok' and 'candles' in data:
                    candles = data['candles']
                    
                    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['date'] = pd.to_datetime(df['timestamp'], unit='s')
                    df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
                    
                    logger.info(f"Fetched {len(df)} candles for {symbol}")
                    return df
                else:
                    logger.warning(f"Invalid response for {symbol}: {data}")
                    return None
            else:
                logger.error(f"API error for {symbol}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {str(e)}")
            return None


class ADRCalculator:
    """Calculate ADR levels and metrics"""
    
    @staticmethod
    def calculate_adr(df: pd.DataFrame, period: int = 14) -> Optional[float]:
        """
        Calculate Average Daily Range
        
        Args:
            df: DataFrame with high/low columns
            period: Number of periods for SMA
            
        Returns:
            ADR value or None
        """
        try:
            if len(df) < period:
                logger.warning(f"Insufficient data for ADR calculation: {len(df)} < {period}")
                return None
            
            # Calculate daily range
            df['daily_range'] = df['high'] - df['low']
            
            # Calculate simple moving average of daily ranges
            adr = df['daily_range'].tail(period).mean()
            
            return adr
            
        except Exception as e:
            logger.error(f"ADR calculation failed: {str(e)}")
            return None
    
    @staticmethod
    def calculate_levels(
        df: pd.DataFrame,
        adr: float,
        multiplier: float = 1.0,
        anchor: str = 'open'
    ) -> Dict[str, float]:
        """
        Calculate upper and lower ADR levels
        
        Args:
            df: DataFrame with OHLC data
            adr: Average Daily Range value
            multiplier: ADR multiplier (default 1.0)
            anchor: 'open' or 'close' for anchor price
            
        Returns:
            Dictionary with level calculations
        """
        try:
            if anchor == 'open':
                anchor_price = df['open'].iloc[-1]
            else:
                anchor_price = df['close'].iloc[-1]
            
            adjusted_adr = adr * multiplier
            upper_level = anchor_price + adjusted_adr
            lower_level = anchor_price - adjusted_adr
            
            # Calculate ADR %
            adr_pct = (adr / df['close'].iloc[-1]) * 100
            
            return {
                'anchor_price': round(anchor_price, 2),
                'adr': round(adr, 2),
                'adr_pct': round(adr_pct, 2),
                'multiplier': multiplier,
                'upper_level': round(upper_level, 2),
                'lower_level': round(lower_level, 2),
                'adjusted_adr': round(adjusted_adr, 2)
            }
            
        except Exception as e:
            logger.error(f"Level calculation failed: {str(e)}")
            return None


def calculate_and_store_adr_levels(
    symbols: List[str],
    adr_period: int = DEFAULT_ADR_PERIOD,
    multiplier: float = DEFAULT_MULTIPLIER,
    anchor: str = DEFAULT_ANCHOR
) -> Dict[str, any]:
    """
    Main function to calculate ADR levels for all symbols and store in DynamoDB
    
    Args:
        symbols: List of stock symbols
        adr_period: ADR period (default 14)
        multiplier: ADR multiplier (default 1.0)
        anchor: Anchor price type (default 'open')
        
    Returns:
        Dictionary with calculation results
    """
    
    fyers_provider = FyersDataProvider(FYERS_API_KEY)
    calculator = ADRCalculator()
    table = dynamodb.Table(ADR_LEVELS_TABLE)
    
    calculation_date = datetime.utcnow().strftime('%Y-%m-%d')
    successful = 0
    failed = 0
    failed_symbols = []
    
    for symbol in symbols:
        try:
            logger.info(f"Processing {symbol}...")
            
            # Fetch historical data
            df = fyers_provider.get_historical_data(symbol, period=adr_period + 10)
            if df is None or len(df) < adr_period:
                logger.warning(f"Insufficient data for {symbol}")
                failed += 1
                failed_symbols.append(symbol)
                continue
            
            # Calculate ADR
            adr = calculator.calculate_adr(df, adr_period)
            if adr is None:
                failed += 1
                failed_symbols.append(symbol)
                continue
            
            # Calculate levels
            levels = calculator.calculate_levels(df, adr, multiplier, anchor)
            if levels is None:
                failed += 1
                failed_symbols.append(symbol)
                continue
            
            # Prepare item for DynamoDB
            item = {
                'symbol': symbol,
                'calculation_date': calculation_date,
                'calculation_time': datetime.utcnow().isoformat(),
                'adr_period': adr_period,
                'anchor': anchor,
                'multiplier': multiplier,
                **levels,
                'ttl': int((datetime.utcnow() + timedelta(days=90)).timestamp())
            }
            
            # Store in DynamoDB
            table.put_item(Item=item)
            
            logger.info(f"Successfully calculated levels for {symbol}: Upper={levels['upper_level']}, Lower={levels['lower_level']}")
            successful += 1
            
        except Exception as e:
            logger.error(f"Failed to process {symbol}: {str(e)}")
            failed += 1
            failed_symbols.append(symbol)
    
    return {
        'calculation_date': calculation_date,
        'total_symbols': len(symbols),
        'successful': successful,
        'failed': failed,
        'failed_symbols': failed_symbols,
        'timestamp': datetime.utcnow().isoformat()
    }


@logger.inject_lambda_context
def lambda_handler(event, context):
    """
    Lambda handler for pre-market ADR calculation
    Triggered by EventBridge schedule (daily at 9 AM IST)
    """
    try:
        logger.info("Starting ADR calculation for NIFTY 50 stocks")
        
        # Calculate for NIFTY 50 universe
        result = calculate_and_store_adr_levels(
            symbols=NIFTY_50_SYMBOLS,
            adr_period=DEFAULT_ADR_PERIOD,
            multiplier=DEFAULT_MULTIPLIER,
            anchor=DEFAULT_ANCHOR
        )
        
        logger.info(f"ADR calculation complete: {result}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.exception(f"ADR calculation failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
