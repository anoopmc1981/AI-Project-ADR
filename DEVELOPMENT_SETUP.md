# ADR Level Breakout Stock Scanner - Development Setup Guide

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend development, optional)
- Docker (for local testing with DynamoDB)
- AWS CLI with configured credentials
- SAM CLI

### 1. Clone and Setup

```bash
# Clone repository
git clone <repo-url>
cd AI-Project-ADR

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Optional: Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

### 2. Local Development Environment

#### Run SAM Local API

```bash
sam build --use-container
sam local start-api --port 3001
```

The API will be available at `http://localhost:3001`

#### Run DynamoDB Local (optional)

```bash
# Using Docker
docker run -p 8000:8000 amazon/dynamodb-local

# Update environment variable
export AWS_ENDPOINT_URL=http://localhost:8000
```

### 3. Frontend Development

Edit `frontend/js/auth.js` to point to local API:

```javascript
const API_BASE_URL = 'http://localhost:3001';
```

Serve frontend locally:

```bash
# Using Python
cd frontend
python -m http.server 8080

# Using Node (if installed)
npx http-server frontend
```

Access at `http://localhost:8080`

## Project Structure

```
AI-Project-ADR/
├── backend/
│   ├── functions/
│   │   ├── auth/              # Authentication Lambda
│   │   ├── adr_calculation/   # ADR computation
│   │   ├── crossing_detection/ # Real-time crossing detection
│   │   ├── dashboard/         # Dashboard API
│   │   ├── ai_assistant/      # AI query processing
│   │   └── whatsapp_alert/    # Alert notifications
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── index.html             # Main dashboard HTML
│   ├── css/
│   │   └── style.css          # Styling
│   └── js/
│       ├── auth.js            # Authentication logic
│       ├── dashboard.js       # Dashboard functionality
│       └── ai-assistant.js    # AI chat interface
├── template.yaml              # SAM template (infrastructure)
├── DEPLOYMENT.md              # Deployment guide
├── DEVELOPMENT_SETUP.md       # This file
└── README.md                  # Project overview
```

## Development Workflow

### 1. Backend Development

#### Adding New Lambda Function

1. Create function directory:
```bash
mkdir backend/functions/my-function
touch backend/functions/my-function/app.py
touch backend/functions/my-function/__init__.py
```

2. Implement function:
```python
import json
import os
from aws_lambda_powertools import Logger

logger = Logger()

@logger.inject_lambda_context
def lambda_handler(event, context):
    """Function description"""
    try:
        # Your code here
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Success'})
        }
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

3. Add to SAM template:
```yaml
MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    FunctionName: !Sub 'adr-scanner-myfunction-${Environment}'
    CodeUri: backend/functions/my-function/
    Handler: app.lambda_handler
    Policies:
      - DynamoDBReadPolicy:
          TableName: !Ref SomeTable
    Events:
      ApiEvent:
        Type: Api
        Properties:
          RestApiId: !Ref ADRScannerApi
          Path: /api/myendpoint
          Method: GET
```

4. Test locally:
```bash
sam local invoke MyFunction --event events/event.json
```

#### Testing Backend

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_adr_calculation.py::test_calculate_adr -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

#### Code Quality

```bash
# Format code
black backend/functions/

# Lint
flake8 backend/functions/

# Type checking
mypy backend/functions/
```

### 2. Frontend Development

#### File Organization

- `index.html` - Main dashboard structure
- `css/style.css` - All styling
- `js/auth.js` - Authentication and user management
- `js/dashboard.js` - Dashboard logic and data fetching
- `js/ai-assistant.js` - AI chat interface

#### Adding New Feature

1. Update HTML in `index.html`
2. Add styling to `css/style.css`
3. Add JavaScript logic to appropriate `js/` file
4. Test in browser with developer tools

#### Browser Console Debugging

```javascript
// Check authentication
authManager.isAuthenticated()
localStorage.getItem('adr_scanner_token')

// Load crossings manually
dashboard.loadCrossings()

// Send AI query
aiAssistant.sendMessage()

// Check API connection
fetch(API_BASE_URL + '/api/crossings', {
  headers: authManager.getAuthHeaders()
}).then(r => r.json()).then(console.log)
```

### 3. Testing Workflow

#### Manual Testing Checklist

- [ ] Login with test credentials
- [ ] Dashboard loads without errors
- [ ] Filters work correctly
- [ ] Auto-refresh updates data
- [ ] Export to CSV works
- [ ] AI assistant responds to queries
- [ ] Logout clears session
- [ ] Responsive design works on mobile

#### API Testing

```bash
# Login
curl -X POST http://localhost:3001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'

# Get crossings
curl -X GET http://localhost:3001/api/crossings \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test AI assistant
curl -X POST http://localhost:3001/api/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"Show upper crossings","type":"filter"}'
```

### 4. Database Management

#### DynamoDB Tables

Tables are created automatically by SAM template:

1. **adr-scanner-levels** - ADR calculations
2. **adr-scanner-crossings** - Crossing events
3. **adr-scanner-history** - Scan history
4. **adr-scanner-user-settings** - User preferences

#### Query Data Locally

```bash
# List tables
aws dynamodb list-tables --endpoint-url http://localhost:8000

# Scan table
aws dynamodb scan \
  --table-name adr-scanner-crossings \
  --endpoint-url http://localhost:8000

# Get item
aws dynamodb get-item \
  --table-name adr-scanner-levels \
  --key '{"symbol":{"S":"INFY"},"calculation_date":{"S":"2024-01-15"}}' \
  --endpoint-url http://localhost:8000
```

## Common Development Tasks

### Update ADR Calculation Logic

File: `backend/functions/adr_calculation/app.py`

Key methods:
- `FyersDataProvider.get_historical_data()` - Fetch OHLCV
- `ADRCalculator.calculate_adr()` - Compute ADR
- `ADRCalculator.calculate_levels()` - Calculate levels

Example modification:

```python
@staticmethod
def calculate_adr_with_smoothing(df: pd.DataFrame, period: int = 14) -> float:
    """Calculate ADR with exponential smoothing"""
    daily_range = df['high'] - df['low']
    # Apply EMA instead of SMA
    adr = daily_range.ewm(span=period).mean().iloc[-1]
    return adr
```

### Add New Dashboard Filter

1. Add HTML input in `index.html`:
```html
<div class="filter-group">
  <label for="mySectorFilter">Sector:</label>
  <select id="mySectorFilter">
    <option value="">All Sectors</option>
  </select>
</div>
```

2. Update JavaScript in `js/dashboard.js`:
```javascript
applyFilters() {
  const sector = document.getElementById('mySectorFilter').value;
  // Add to queryParams
}
```

3. Update backend Lambda to support filter

### Modify AI Assistant Prompts

File: `backend/functions/ai_assistant/app.py`

The key prompt is in `FilterInterpreter.get_interpretation_prompt()`. Modify the prompt template to change AI behavior:

```python
prompt = f"""You are an AI assistant for an ADR stock scanner.
[Your enhanced prompt here]
"""
```

### Add WhatsApp Integration

File: `backend/functions/whatsapp_alert/app.py`

Currently has placeholder. To implement:

1. Get WhatsApp API credentials (Twilio, AWS SNS, etc.)
2. Store in AWS Secrets Manager
3. Implement in `WhatsAppNotificationService._send_via_twilio()`
4. Test alert delivery

## Debugging Tips

### Enable Verbose Logging

Set environment variable:
```bash
export LOG_LEVEL=DEBUG
```

### CloudWatch Logs Insight Queries

```
# Find errors
fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc

# Performance analysis
fields @duration | stats avg(@duration), max(@duration), pct(@duration, 99)

# ADR calculation times
fields @timestamp, @duration | filter @message like /ADR calculation/ 
```

### SAM Local Debugging

```bash
# Enable debug output
sam local start-api --debug --log-level DEBUG

# Debug specific function
sam local invoke -d 5858 ADRCalculationFunction \
  --event events/adr-event.json
```

## Performance Optimization

### Lambda Performance

1. **Increase Memory** (better CPU):
```yaml
MemorySize: 1024  # Default 512
```

2. **Reduce Initialization Time**:
- Lazy import heavy libraries
- Keep dependencies minimal
- Use Lambda Layers for shared code

3. **Optimize Timeouts**:
```yaml
Timeout: 300  # 5 minutes for ADR calculation
```

### Frontend Performance

1. **Minimize HTTP Requests**:
- Batch API calls
- Cache results locally

2. **Optimize Table Rendering**:
```javascript
// Use document fragments for bulk inserts
const fragment = document.createDocumentFragment();
data.forEach(item => {
  fragment.appendChild(createRow(item));
});
tbody.appendChild(fragment);
```

3. **Lazy Load Data**:
```javascript
// Load data on demand
document.addEventListener('scroll', () => {
  if (nearBottom()) loadMoreData();
});
```

## Deployment to AWS

### Quick Deploy

```bash
sam build
sam deploy
```

### Staged Deployment

```bash
# Build
sam build --use-container

# Deploy to dev
sam deploy --config-file dev-samconfig.toml

# Deploy to staging
sam deploy --config-file staging-samconfig.toml

# Deploy to prod (after testing)
sam deploy --config-file prod-samconfig.toml
```

## Environment Variables

Create `.env` file (for local development):

```
ENVIRONMENT=dev
AWS_REGION=us-east-1
FYERS_API_KEY=your_key_here
WHATSAPP_API_KEY=your_key_here
LOG_LEVEL=INFO
```

Load in Python:
```python
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('FYERS_API_KEY')
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "feat: Add new feature"

# Push to remote
git push origin feature/my-feature

# Create Pull Request
# After review, merge to main
git checkout main
git pull
git merge feature/my-feature
git push origin main
```

## Troubleshooting Development Issues

### SAM Build Fails

```bash
# Clean and rebuild
rm -rf .aws-sam build/
sam build --use-container --debug
```

### Local API Returns 502

- Check Lambda logs: `sam local start-api --debug`
- Ensure DynamoDB is running if local
- Check function IAM permissions

### Frontend Can't Connect to API

- Verify API URL in `auth.js`
- Check CORS settings in API Gateway
- Verify auth token in browser console

### Tests Fail

- Ensure DynamoDB Local is running
- Check AWS credentials
- Review test setup in `conftest.py`

---

For more help, refer to:
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Fyers API Documentation](https://www.fyers.in/api-documentation)
