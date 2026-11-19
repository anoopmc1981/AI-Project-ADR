"""
Dashboard API Lambda Function
Provides data for the frontend dashboard
Returns current crossings and scan history
"""

import json
import os
import boto3
from datetime import datetime, timedelta
from typing import Dict, List
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.validation import validate

logger = Logger()
dynamodb = boto3.resource('dynamodb')

CROSSINGS_TABLE = os.environ.get('DYNAMODB_TABLE_CROSSINGS')
HISTORY_TABLE = os.environ.get('DYNAMODB_TABLE_HISTORY')
ADR_LEVELS_TABLE = os.environ.get('DYNAMODB_TABLE_LEVELS')


def get_current_crossings(
    direction: str = None,
    limit: int = 50
) -> List[Dict]:
    """
    Get current day's crossings
    
    Args:
        direction: Filter by 'UPPER', 'LOWER', or None for both
        limit: Maximum results
        
    Returns:
        List of crossing records
    """
    try:
        table = dynamodb.Table(CROSSINGS_TABLE)
        today = datetime.utcnow().strftime('%Y-%m-%d')
        
        response = table.query(
            IndexName='SymbolDateIndex',
            KeyConditionExpression='crossing_date = :date',
            ExpressionAttributeValues={
                ':date': today
            },
            Limit=limit
        )
        
        crossings = response.get('Items', [])
        
        # Filter by direction if specified
        if direction:
            crossings = [c for c in crossings if c.get('direction') == direction]
        
        # Sort by crossing time, newest first
        crossings.sort(key=lambda x: x.get('crossing_timestamp', ''), reverse=True)
        
        return crossings
        
    except Exception as e:
        logger.error(f"Failed to get current crossings: {str(e)}")
        return []


def get_crossing_summary() -> Dict:
    """
    Get summary of today's crossings
    
    Returns:
        Dictionary with count summaries
    """
    try:
        upper_crossings = get_current_crossings(direction='UPPER')
        lower_crossings = get_current_crossings(direction='LOWER')
        
        return {
            'upper_count': len(upper_crossings),
            'lower_count': len(lower_crossings),
            'total_count': len(upper_crossings) + len(lower_crossings),
            'last_update': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get summary: {str(e)}")
        return {
            'upper_count': 0,
            'lower_count': 0,
            'total_count': 0,
            'last_update': datetime.utcnow().isoformat()
        }


def get_scan_history(
    days: int = 7,
    limit: int = 100
) -> List[Dict]:
    """
    Get historical scan summaries
    
    Args:
        days: Number of past days to retrieve
        limit: Maximum results
        
    Returns:
        List of historical scan records
    """
    try:
        table = dynamodb.Table(HISTORY_TABLE)
        
        # Calculate date range
        end_date = datetime.utcnow().strftime('%Y-%m-%d')
        start_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        response = table.scan(
            FilterExpression='scan_date BETWEEN :start_date AND :end_date',
            ExpressionAttributeValues={
                ':start_date': start_date,
                ':end_date': end_date
            },
            Limit=limit
        )
        
        history = response.get('Items', [])
        history.sort(key=lambda x: x.get('scan_date', ''), reverse=True)
        
        return history
        
    except Exception as e:
        logger.error(f"Failed to get scan history: {str(e)}")
        return []


def format_crossing_for_display(crossing: Dict) -> Dict:
    """
    Format crossing data for frontend display
    
    Args:
        crossing: Raw crossing record
        
    Returns:
        Formatted crossing record
    """
    return {
        'symbol': crossing.get('symbol'),
        'direction': crossing.get('direction'),
        'ltp': crossing.get('ltp_at_crossing'),
        'anchor': crossing.get('anchor_price'),
        'adr': crossing.get('adr'),
        'adr_pct': crossing.get('adr_pct'),
        'level': crossing.get('level_value'),
        'percentage_move': crossing.get('percentage_move'),
        'volume_vs_avg': crossing.get('volume_vs_avg'),
        'crossing_time': crossing.get('crossing_timestamp'),
        'status': crossing.get('status', 'ACTIVE')
    }


def apply_filters(
    crossings: List[Dict],
    filters: Dict
) -> List[Dict]:
    """
    Apply user-specified filters to crossings
    
    Args:
        crossings: List of crossing records
        filters: Filter criteria (min_price, min_volume_ratio, adr_pct_min, etc.)
        
    Returns:
        Filtered list
    """
    filtered = crossings
    
    # Min price filter
    if 'min_price' in filters:
        filtered = [c for c in filtered if c.get('ltp_at_crossing', 0) >= filters['min_price']]
    
    # Volume ratio filter
    if 'min_volume_ratio' in filters:
        filtered = [c for c in filtered if c.get('volume_vs_avg', 0) >= filters['min_volume_ratio']]
    
    # ADR % minimum
    if 'adr_pct_min' in filters:
        filtered = [c for c in filtered if c.get('adr_pct', 0) >= filters['adr_pct_min']]
    
    # ADR % maximum
    if 'adr_pct_max' in filters:
        filtered = [c for c in filtered if c.get('adr_pct', 0) <= filters['adr_pct_max']]
    
    # Percentage move filter
    if 'min_move_pct' in filters:
        filtered = [c for c in filtered if abs(c.get('percentage_move', 0)) >= filters['min_move_pct']]
    
    return filtered


@logger.inject_lambda_context
def lambda_handler(event, context):
    """
    Dashboard API handler
    
    Query parameters:
    - type: 'crossings' or 'history' (default: 'crossings')
    - direction: 'UPPER', 'LOWER', or 'both' (default: 'both')
    - days: number of days for history (default: 7)
    - min_price: minimum stock price
    - min_volume_ratio: minimum volume vs average ratio
    - adr_pct_min: minimum ADR %
    - adr_pct_max: maximum ADR %
    """
    try:
        # Parse query parameters
        query_params = event.get('queryStringParameters') or {}
        request_type = query_params.get('type', 'crossings')
        
        if request_type == 'history':
            # Return scan history
            days = int(query_params.get('days', 7))
            history = get_scan_history(days=days)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'type': 'history',
                    'data': history,
                    'timestamp': datetime.utcnow().isoformat()
                })
            }
        
        else:
            # Return current crossings
            direction = query_params.get('direction', 'both')
            
            # Get crossings
            upper = get_current_crossings(direction='UPPER') if direction in ['both', 'UPPER'] else []
            lower = get_current_crossings(direction='LOWER') if direction in ['both', 'LOWER'] else []
            
            # Format for display
            upper_formatted = [format_crossing_for_display(c) for c in upper]
            lower_formatted = [format_crossing_for_display(c) for c in lower]
            
            # Apply filters if specified
            filters = {}
            if 'min_price' in query_params:
                filters['min_price'] = float(query_params['min_price'])
            if 'min_volume_ratio' in query_params:
                filters['min_volume_ratio'] = float(query_params['min_volume_ratio'])
            if 'adr_pct_min' in query_params:
                filters['adr_pct_min'] = float(query_params['adr_pct_min'])
            if 'adr_pct_max' in query_params:
                filters['adr_pct_max'] = float(query_params['adr_pct_max'])
            if 'min_move_pct' in query_params:
                filters['min_move_pct'] = float(query_params['min_move_pct'])
            
            if filters:
                upper_formatted = apply_filters(upper_formatted, filters)
                lower_formatted = apply_filters(lower_formatted, filters)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'type': 'crossings',
                    'summary': get_crossing_summary(),
                    'upper_crossings': upper_formatted,
                    'lower_crossings': lower_formatted,
                    'timestamp': datetime.utcnow().isoformat()
                })
            }
        
    except Exception as e:
        logger.exception(f"Dashboard API error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
