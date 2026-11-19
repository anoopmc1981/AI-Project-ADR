"""
AI Assistant Lambda Function
Uses Amazon Bedrock to provide natural language queries and explanations
Converts user questions to filters and provides insights about scan data
"""

import json
import os
import boto3
from datetime import datetime
from typing import Dict, List, Optional
from aws_lambda_powertools import Logger

logger = Logger()
dynamodb = boto3.resource('dynamodb')
bedrock_runtime = boto3.client('bedrock-runtime')

CROSSINGS_TABLE = os.environ.get('DYNAMODB_TABLE_CROSSINGS')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')


class FilterInterpreter:
    """Convert natural language to structured filters"""
    
    @staticmethod
    def get_interpretation_prompt(user_query: str, available_crossings: List[Dict]) -> str:
        """
        Create a prompt for Claude to interpret user query
        
        Args:
            user_query: User's natural language query
            available_crossings: Current crossing data for context
            
        Returns:
            Formatted prompt
        """
        
        crossings_summary = FilterInterpreter._summarize_crossings(available_crossings)
        
        prompt = f"""You are an AI assistant for an ADR (Average Daily Range) stock scanner.
A user has asked a question about their scan results. Your job is to:
1. Understand what they're asking
2. Extract structured filters from their query
3. Return ONLY a valid JSON object with the filters

Current scan data summary:
- Total crossings: {len(available_crossings)}
- Upper crossings: {len([c for c in available_crossings if c.get('direction') == 'UPPER'])}
- Lower crossings: {len([c for c in available_crossings if c.get('direction') == 'LOWER'])}

{crossings_summary}

User Query: "{user_query}"

You MUST respond with ONLY a valid JSON object with these possible fields:
{{
  "direction": "UPPER|LOWER|both",
  "min_price": number,
  "max_price": number,
  "min_volume_ratio": number,
  "adr_pct_min": number,
  "adr_pct_max": number,
  "min_move_pct": number,
  "max_move_pct": number,
  "interpretation": "brief explanation of what you understood"
}}

Only include fields that are relevant to the query. Return empty object {{}} if query cannot be interpreted as a filter.
"""
        
        return prompt
    
    @staticmethod
    def _summarize_crossings(crossings: List[Dict]) -> str:
        """Generate summary of current crossings"""
        if not crossings:
            return "No crossings today."
        
        try:
            prices = [c.get('ltp', 0) for c in crossings]
            volumes = [c.get('volume_vs_avg', 0) for c in crossings]
            moves = [abs(c.get('percentage_move', 0)) for c in crossings]
            
            summary = f"""
Recent crossings:
- Price range: ₹{min(prices):.2f} - ₹{max(prices):.2f}
- Average volume ratio: {sum(volumes)/len(volumes):.2f}x
- Largest move: {max(moves):.2f}%
- Top symbols: {', '.join([c.get('symbol', 'N/A') for c in crossings[:5]])}
"""
            return summary
        except:
            return ""


class ScanAnalyzer:
    """Analyze scan results and provide insights"""
    
    @staticmethod
    def generate_summary(crossings: List[Dict]) -> str:
        """Generate a natural language summary of scan results"""
        
        if not crossings:
            return "No crossings detected today."
        
        upper = [c for c in crossings if c.get('direction') == 'UPPER']
        lower = [c for c in crossings if c.get('direction') == 'LOWER']
        
        summary = f"ADR Scan Summary:\n"
        summary += f"- Total crossings: {len(crossings)}\n"
        summary += f"- Upper level crossings: {len(upper)}\n"
        summary += f"- Lower level crossings: {len(lower)}\n"
        
        if upper:
            avg_volume = sum([c.get('volume_vs_avg', 0) for c in upper]) / len(upper)
            summary += f"- Upper average volume ratio: {avg_volume:.2f}x\n"
        
        if lower:
            avg_volume = sum([c.get('volume_vs_avg', 0) for c in lower]) / len(lower)
            summary += f"- Lower average volume ratio: {avg_volume:.2f}x\n"
        
        summary += "\nTop movers:\n"
        top_movers = sorted(
            crossings,
            key=lambda x: abs(x.get('percentage_move', 0)),
            reverse=True
        )[:3]
        
        for i, cross in enumerate(top_movers, 1):
            direction = "▲" if cross.get('direction') == 'UPPER' else "▼"
            summary += f"{i}. {cross.get('symbol')} {direction} {cross.get('percentage_move'):.2f}% - ₹{cross.get('ltp')}\n"
        
        summary += "\n*For information and education only. Not investment advice.*"
        
        return summary
    
    @staticmethod
    def explain_crossing(crossing: Dict) -> str:
        """Provide detailed explanation for a specific crossing"""
        
        explanation = f"""
Crossing Details for {crossing.get('symbol')}:

Direction: {'Upper ADR Crossing ▲' if crossing.get('direction') == 'UPPER' else 'Lower ADR Crossing ▼'}
Time: {crossing.get('crossing_timestamp', 'N/A')}

Price Information:
- Current Price (LTP): ₹{crossing.get('ltp'):.2f}
- Anchor Price: ₹{crossing.get('anchor'):.2f}
- Level Crossed: ₹{crossing.get('level'):.2f}
- % Move from Anchor: {crossing.get('percentage_move'):.2f}%

ADR Metrics:
- ADR Value: ₹{crossing.get('adr'):.2f}
- ADR %: {crossing.get('adr_pct'):.2f}%

Volume:
- Volume vs Average: {crossing.get('volume_vs_avg'):.2f}x
- Status: {'Active' if crossing.get('status') == 'ACTIVE' else 'Reverted'}

Why This Matters:
- The stock crossed the {crossing.get('direction', 'ADR')} level, indicating {'increased volatility to the upside' if crossing.get('direction') == 'UPPER' else 'increased volatility to the downside'}.
- Volume ratio of {crossing.get('volume_vs_avg'):.2f}x {'confirms strong' if crossing.get('volume_vs_avg', 0) > 1 else 'shows moderate'} buying/selling pressure.

*For information and education only. Not investment advice.*
        """.strip()
        
        return explanation


def get_current_crossings() -> List[Dict]:
    """Fetch today's crossings from DynamoDB"""
    try:
        table = dynamodb.Table(CROSSINGS_TABLE)
        today = datetime.utcnow().strftime('%Y-%m-%d')
        
        response = table.query(
            IndexName='SymbolDateIndex',
            KeyConditionExpression='crossing_date = :date',
            ExpressionAttributeValues={
                ':date': today
            }
        )
        
        return response.get('Items', [])
        
    except Exception as e:
        logger.error(f"Failed to fetch crossings: {str(e)}")
        return []


def invoke_bedrock(prompt: str) -> Optional[str]:
    """
    Invoke Bedrock Claude model
    
    Args:
        prompt: The prompt to send to Claude
        
    Returns:
        Model response or None
    """
    try:
        message = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-06-01',
                'max_tokens': 1024,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(message['body'].read())
        content = response_body['content'][0]['text']
        
        return content
        
    except Exception as e:
        logger.error(f"Bedrock invocation failed: {str(e)}")
        return None


def process_chat_query(user_message: str, query_type: str = 'filter') -> Dict:
    """
    Process a user chat query
    
    Args:
        user_message: The user's question
        query_type: 'filter', 'summary', or 'explain'
        
    Returns:
        Dictionary with response
    """
    
    try:
        crossings = get_current_crossings()
        
        if query_type == 'summary':
            # Generate scan summary
            summary = ScanAnalyzer.generate_summary(crossings)
            return {
                'response_type': 'summary',
                'message': summary
            }
        
        elif query_type == 'filter':
            # Interpret query and extract filters
            interpreter_prompt = FilterInterpreter.get_interpretation_prompt(
                user_message,
                crossings
            )
            
            bedrock_response = invoke_bedrock(interpreter_prompt)
            if not bedrock_response:
                return {
                    'response_type': 'error',
                    'message': 'Failed to process query'
                }
            
            # Try to parse as JSON
            try:
                filters = json.loads(bedrock_response)
                interpretation = filters.get('interpretation', 'Understood your query')
                
                return {
                    'response_type': 'filters',
                    'message': f"Found filters: {interpretation}",
                    'filters': {k: v for k, v in filters.items() if k != 'interpretation'},
                    'disclaimer': 'For information and education only. Not investment advice.'
                }
            except json.JSONDecodeError:
                # If JSON parse fails, return Claude's response as-is
                return {
                    'response_type': 'text',
                    'message': bedrock_response,
                    'disclaimer': 'For information and education only. Not investment advice.'
                }
        
        else:
            return {
                'response_type': 'error',
                'message': f'Unknown query type: {query_type}'
            }
        
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        return {
            'response_type': 'error',
            'message': f'Query processing failed: {str(e)}'
        }


@logger.inject_lambda_context
def lambda_handler(event, context):
    """
    AI Assistant API handler
    
    Request body:
    {
        "query": "Show stocks that crossed upper ADR with volume > 2x average",
        "type": "filter|summary|explain"
    }
    """
    
    try:
        body = json.loads(event.get('body', '{}'))
        user_query = body.get('query', '')
        query_type = body.get('type', 'filter')
        
        if not user_query:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Query is required'})
            }
        
        # Process query
        result = process_chat_query(user_query, query_type)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.exception(f"Chat API error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
