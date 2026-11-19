# ADR Level Breakout Stock Scanner

An **AI-powered, serverless web application** that scans NSE-listed stocks for **Average Daily Range (ADR) level crossings**. Built with **AWS serverless architecture** and **Fyers market data API**, it provides real-time detection of upper and lower ADR breakouts with an intelligent AI assistant for natural language queries.

![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![AWS](https://img.shields.io/badge/AWS-Serverless-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Development](#development)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [License](#license)

## Features

### Core Functionality

✅ **ADR Calculation Engine**
- Calculates Average Daily Range over configurable periods (default 14 days)
- Supports configurable multipliers (0.5x to 2.0x)
- Adjustable anchor prices (Open or Close)
- Pre-computed daily for NSE NIFTY 50 stocks

✅ **Real-time Crossing Detection**
- Live detection of upper and lower ADR level crossings
- Duplicate alert prevention (first crossing per stock/day)
- Reversion detection (price returning inside ADR band)
- Volume ratio analysis (vs. average volume)

✅ **Interactive Dashboard**
- Two-table view: Upper and Lower crossings
- Real-time data with auto-refresh (30-second intervals during market hours)
- Advanced filtering (price, volume, ADR %, move %)
- Export to CSV for further analysis
- Market hours detection and status display

✅ **AI-Powered Natural Language Assistant**
- Ask questions in natural language (e.g., "Show stocks crossing upper ADR with 2x volume")
- Converts queries to structured filters automatically
- Generates scan summaries and insights
- Explainable results with formula inputs shown
- Includes investment disclaimer on all responses

✅ **Alert System**
- WhatsApp notifications for new crossings
- User-configurable alert preferences
- Batching and cooldown to prevent flooding
- Support for single or multiple users

✅ **User Authentication**
- Cognito-based secure login
- Session management with JWT tokens
- Role-based settings (future multi-user support)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Browser                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Dashboard   │  │  AI Assistant│  │   Settings   │       │
│  │   (HTML/JS)  │  │   Chat UI    │  │   Filters    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                           │
                    ┌──────┴──────┐
                    │ CloudFront  │ (CDN)
                    │  + S3       │
                    └──────┬──────┘
                           │
                    ┌──────┴──────────────────────────┐
                    │   AWS API Gateway               │
                    │   (REST API, Auth)              │
                    └──────┬──────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┬──────────────────┐
        │                  │                  │                  │
   ┌────▼────┐        ┌────▼────┐       ┌────▼────┐        ┌────▼────┐
   │ Lambda  │        │ Lambda  │       │ Lambda  │        │ Lambda  │
   │ Auth    │        │ Dashboard│      │  AI     │        │ Alerts  │
   │Function │        │ Function │      │Assistant│        │Function │
   └─────────┘        └─────────┘       └────────┘        └─────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────┴──────┐
                    │  DynamoDB   │ (User data, Crossings, History)
                    │  Tables     │
                    └─────────────┘
        ┌─────────────────────┐
        │EventBridge Scheduler│ (Daily ADR calc at 9 AM IST)
        └──────────┬──────────┘
                   │
              ┌────▼────┐
              │ Lambda  │
              │ ADR Cal.│ (Pre-market calculation)
              └────┬────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   ┌────▼─────┐         ┌─────▼────┐
   │Fyers API │         │ S3       │
   │(Market   │         │ Parquet  │
   │Data)     │         │ Storage  │
   └──────────┘         └──────────┘

Live Detection (Polling):
┌─────────────────┐
│EventBridge Sched│ (Every 1-5 min during market hours)
└────────┬────────┘
         │
    ┌────▼─────────────┐
    │Lambda Crossing   │
    │Detection         │
    ├─ Fetch LTP       │
    ├─ Check levels    │
    ├─ Record event    │
    └────┬─────────────┘
         │
    ┌────▼──────┐
    │SNS Topic  │
    │(Alerts)   │
    └────┬──────┘
         │
    ┌────▼──────────┐
    │SQS Queue      │
    └────┬──────────┘
         │
    ┌────▼─────────────┐
    │Lambda WhatsApp   │
    │Alert Function    │
    └──────────────────┘
```

## Tech Stack

### Backend
- **AWS Lambda** - Serverless compute
- **AWS DynamoDB** - NoSQL database
- **AWS API Gateway** - REST API
- **AWS Cognito** - Authentication
- **AWS EventBridge** - Scheduling
- **AWS SNS/SQS** - Messaging
- **AWS Bedrock** - AI/ML (Claude)
- **Python 3.11** - Function runtime
- **AWS Powertools** - Observability

### Frontend
- **HTML5, CSS3, JavaScript** (vanilla)
- **Responsive Design** (mobile-friendly)
- **JWT Authentication**
- **Fetch API** for async requests

### Integration APIs
- **Fyers Kite Connect** - Market data
- **WhatsApp API** - Notifications
- **AWS Secrets Manager** - Credential management

### DevOps
- **AWS SAM** - Infrastructure as Code
- **CloudFormation** - Infrastructure provisioning
- **CloudFront** - CDN
- **CloudWatch** - Monitoring & Logs

## Quick Start

### Prerequisites

- Python 3.11+
- AWS Account with IAM permissions
- AWS CLI & SAM CLI configured
- Fyers Broker Account with API access
- Docker (for SAM local testing)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd AI-Project-ADR

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Build SAM application
sam build --use-container
```

### Local Development

```bash
# Start local API
sam local start-api --port 3001

# In another terminal, serve frontend
cd frontend
python -m http.server 8080
```

Access dashboard at: `http://localhost:8080`

### Deployment to AWS

```bash
# Build and deploy (interactive setup on first deploy)
sam deploy --guided

# Or deploy directly if already configured
sam deploy
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Usage

### Dashboard

1. **Login** with Cognito credentials
2. **View Crossings**:
   - Upper ADR Level crossings (bullish breakout)
   - Lower ADR Level crossings (bearish breakout)
3. **Apply Filters**:
   - By direction (upper/lower)
   - By price range
   - By volume ratio
   - By ADR %
4. **Auto-Refresh**: Toggle 30-second auto-refresh during market hours
5. **Export**: Download results as CSV

### AI Assistant

Ask natural language questions:
- "Show upper crossings with volume > 2x average"
- "Which stocks crossed ADR with highest move percentage?"
- "Give me a summary of today's scan"
- "Explain the INFY crossing"

The AI converts queries to filters and shows results.

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | User authentication |
| GET | `/api/crossings` | Get today's crossings |
| GET | `/api/crossings?direction=UPPER` | Filter by direction |
| GET | `/api/history?days=7` | Scan history |
| POST | `/api/chat` | AI assistant query |

See [API Documentation](#api-documentation) for details.

## Development

### Project Structure

```
AI-Project-ADR/
├── backend/
│   ├── functions/
│   │   ├── auth/
│   │   ├── adr_calculation/
│   │   ├── crossing_detection/
│   │   ├── dashboard/
│   │   ├── ai_assistant/
│   │   └── whatsapp_alert/
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── auth.js
│       ├── dashboard.js
│       └── ai-assistant.js
├── template.yaml
├── Makefile
├── DEVELOPMENT_SETUP.md
├── DEPLOYMENT.md
└── README.md
```

### Development Setup

```bash
# See DEVELOPMENT_SETUP.md for:
# - Local API testing
# - Frontend development
# - Database queries
# - Debugging tips
# - Performance optimization
```

### Adding Features

1. **New Lambda Function**: See [backend guide](DEVELOPMENT_SETUP.md#adding-new-lambda-function)
2. **Frontend Changes**: Update HTML, CSS, and JS
3. **Database Schema**: Modify SAM template DynamoDB sections
4. **Testing**: Add tests in `tests/` directory

## Deployment

### Prerequisites

```bash
# Install AWS SAM CLI
brew install aws-sam-cli  # macOS
# Or download from https://aws.amazon.com/serverless/sam/

# Configure AWS credentials
aws configure

# Verify credentials
aws sts get-caller-identity
```

### Deploy Steps

```bash
# 1. Build
sam build --use-container

# 2. Deploy (first time - interactive)
sam deploy --guided

# 3. Get outputs
aws cloudformation describe-stacks \
  --stack-name adr-scanner-dev \
  --query 'Stacks[0].Outputs'

# 4. Deploy frontend
aws s3 sync frontend/ s3://YOUR_BUCKET/ --delete

# 5. Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"
```

For detailed deployment: [DEPLOYMENT.md](DEPLOYMENT.md)

## API Documentation

### Authentication Endpoint

**POST** `/auth/login`

Request:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "remember_me": true
}
```

Response:
```json
{
  "success": true,
  "user_id": "user-uuid",
  "id_token": "jwt-token",
  "access_token": "access-token",
  "expires_in": 3600
}
```

### Dashboard Endpoint

**GET** `/api/crossings`

Query Parameters:
- `direction`: "UPPER" | "LOWER" | "both" (default: both)
- `min_price`: Minimum stock price
- `min_volume_ratio`: Minimum volume vs average
- `adr_pct_min`: Minimum ADR %
- `adr_pct_max`: Maximum ADR %

Response:
```json
{
  "type": "crossings",
  "summary": {
    "upper_count": 5,
    "lower_count": 3,
    "total_count": 8,
    "last_update": "2024-01-15T14:30:00"
  },
  "upper_crossings": [
    {
      "symbol": "INFY",
      "direction": "UPPER",
      "ltp": 2150.50,
      "anchor": 2140.00,
      "adr": 25.50,
      "adr_pct": 1.19,
      "level": 2165.50,
      "percentage_move": 0.49,
      "volume_vs_avg": 1.8,
      "crossing_time": "2024-01-15T14:25:30Z",
      "status": "ACTIVE"
    }
  ],
  "lower_crossings": []
}
```

### AI Assistant Endpoint

**POST** `/api/chat`

Request:
```json
{
  "query": "Show upper crossings with volume > 2x average",
  "type": "filter"
}
```

Response:
```json
{
  "response_type": "filters",
  "message": "Found 3 stocks crossing upper ADR with high volume",
  "filters": {
    "direction": "UPPER",
    "min_volume_ratio": 2.0
  },
  "disclaimer": "For information and education only. Not investment advice."
}
```

## Troubleshooting

### Common Issues

**Login fails**
- Verify Cognito User Pool ID in frontend
- Check user exists: `aws cognito-idp admin-get-user --user-pool-id POOL_ID --username EMAIL`
- Reset password if needed

**API returns 502**
- Check Lambda logs: `aws logs tail /aws/lambda/FUNCTION_NAME`
- Verify IAM permissions for Lambda
- Check DynamoDB tables exist

**Frontend can't connect**
- Verify API URL in `js/auth.js`
- Check CORS settings
- Ensure CloudFront is configured

**No crossings detected**
- Verify Fyers API credentials
- Check market hours (9:15 AM - 3:30 PM IST)
- Ensure ADR levels calculated (check ADR Calculation Lambda)

See [Troubleshooting Guide](DEVELOPMENT_SETUP.md#troubleshooting-development-issues) for more.

## Roadmap

### Phase 1 (Current)
- ✅ ADR calculation engine
- ✅ Real-time crossing detection
- ✅ Dashboard with filters
- ✅ AI assistant (basic queries)
- ✅ WhatsApp alerts
- ✅ Single user support

### Phase 2
- 🔄 Multi-user support with user profiles
- 🔄 Custom universe selection (not just NIFTY 50)
- 🔄 Advanced alerting (email, SMS, Telegram)
- 🔄 Historical backtesting
- 🔄 Performance analytics

### Phase 3
- 📋 Mobile app (React Native)
- 📋 Webhook integrations (Discord, Slack)
- 📋 Strategy builder (combine multiple indicators)
- 📋 Portfolio tracking
- 📋 Machine learning insights

### Future
- 🚀 Other exchanges (BSE, MCX)
- 🚀 Options analysis
- 🚀 Advanced charting
- 🚀 Community signals sharing

## Configuration

### Environment Variables

```bash
# AWS
AWS_REGION=us-east-1
ENVIRONMENT=dev

# Fyers
FYERS_API_KEY=your_api_key

# WhatsApp
WHATSAPP_API_KEY=your_api_key
WHATSAPP_API_URL=https://your_whatsapp_provider_url

# ADR Settings
ADR_PERIOD=14
ADR_MULTIPLIER=1.0
ADR_ANCHOR=open  # 'open' or 'close'

# Universe
UNIVERSE=NIFTY_50  # NIFTY_50, NIFTY_100, NIFTY_500, ALL_NSE

# Alerts
ALERT_CHANNEL=whatsapp  # whatsapp, email, telegram
```

## Performance Metrics

### Target Latencies
- Dashboard page load: < 3 seconds
- API response time: < 500ms
- Crossing detection: < 60 seconds from price event
- ADR calculation: completes before 9:00 AM IST

### Scalability
- Supports 50+ concurrent users
- Processes 500+ stocks in ~2 minutes
- Handles 1000s of crossings per day
- Auto-scaling Lambda and DynamoDB (on-demand)

## Security

### Best Practices Implemented
- ✅ JWT token authentication (Cognito)
- ✅ HTTPS only (API Gateway + CloudFront)
- ✅ Least privilege IAM roles
- ✅ Secrets Manager for API credentials
- ✅ DynamoDB encryption at rest
- ✅ S3 bucket versioning & access blocks
- ✅ CloudFront OAI for S3 access

### API Security
- OAuth 2.0 with Cognito
- Rate limiting on API Gateway
- CORS validation
- Input validation and sanitization

## Monitoring

### CloudWatch Dashboards
- Lambda invocations and errors
- DynamoDB read/write capacity
- API Gateway latency and errors
- Crossing detection frequency

### Alarms
- Lambda function errors
- DynamoDB throttling
- API Gateway 5XX errors
- Crossing detection lag

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a Pull Request

See [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md) for development guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## Disclaimer

**Important**: This application is for informational and educational purposes only.

- ADR crossings are NOT guaranteed trading signals
- Past performance does not guarantee future results
- Always do your own research before trading
- Consult with a financial advisor for investment decisions
- The developers assume no liability for trading losses

Use at your own risk. The stock market involves risk, and individuals should carefully consider their investment goals and risk tolerance before trading.

## Support

For issues, questions, or suggestions:
1. Check [troubleshooting guide](DEVELOPMENT_SETUP.md#troubleshooting-development-issues)
2. Review [API docs](#api-documentation)
3. Open a GitHub issue
4. Contact the development team

## Authors

- **Created**: January 2025
- **Project**: ADR Level Breakout Stock Scanner for NSE Equities

## Acknowledgments

- Fyers broker for market data API
- AWS for serverless infrastructure
- Claude AI (via Bedrock) for natural language processing
- Indian stock trading community

---

**Happy trading! 📈📉**

**Remember: This is a screening tool for personal use. Always verify signals manually and trade responsibly.**
