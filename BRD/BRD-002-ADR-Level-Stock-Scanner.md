# BRD-002: AI-Powered ADR Level Breakout Stock Scanner (Indian Equities)

**Version:** 1.1
**Project:** ADR Scanner
**Market:** NSE-listed equities (cash segment)
**Platform:** AWS (serverless) + Fyers API v3 market data (free Standard plan)

## 1. Business Objective

Build a web-based scanner that identifies NSE-listed stocks whose price has crossed the **upper ADR level** or the **lower ADR level**, and presents them as a ranked, filterable list for intraday and swing traders.

An AI layer allows users to query and understand scan results in natural language, for example: "Show stocks that crossed the upper ADR level with volume above 2x average."

The signal calculation is **deterministic** (rule-based). The AI layer only explains, summarizes, and filters results. It never calculates or invents signals.

## 2. Indicator Definition (Assumption — To Be Confirmed)

ADR in this document means **Average Daily Range**.

- **Daily Range** = High − Low for a trading day.
- **ADR(N)** = Simple moving average of the Daily Range over the previous N completed trading days (default N = 14; configurable 5–50). The current day is excluded from the calculation.
- **ADR % (optional)** = ADR(N) / Previous Close × 100.
- **Anchor price** (configurable): Today's Open (default) or Previous Close.
- **Upper ADR Level** = Anchor + (ADR × Multiplier).
- **Lower ADR Level** = Anchor − (ADR × Multiplier).
- **Multiplier** default = 1.0 (configurable, for example 0.5, 1.0, 1.5, 2.0).

**Crossing rules:**
- **Upper cross:** Last traded price (or candle close, per user setting) is at or above the Upper ADR Level.
- **Lower cross:** Last traded price (or candle close, per user setting) is at or below the Lower ADR Level.

> If "ADR" is intended to mean something else (for example, a custom ADR indicator from a charting platform), the formula in this section must be updated before development starts.

## 3. Application Scope

The application must provide:

- User authentication using Amazon Cognito.
- A web dashboard showing stocks that crossed the upper ADR level and the lower ADR level.
- Daily computation of ADR for the configured stock universe.
- Live (intraday) detection of ADR level crossings during market hours.
- End-of-day (EOD) scan for swing traders.
- Configurable filters (universe, ADR period, multiplier, anchor, volume, price, ADR %).
- An AI assistant for natural language queries and result summaries.
- Alert notifications for new crossings.
- Scan history for review.

## 4. Functional Requirements

### FR-01: Authentication
- Implement Amazon Cognito User Pool.
- Users must log in before accessing the dashboard.
- Unauthenticated users must be redirected to the login page.
- Support logout and session termination.
- Protect backend APIs using Cognito authorization.

### FR-02: Stock Universe Management
- Support selectable universes: NIFTY 50, NIFTY 100, NIFTY 200, NIFTY 500, and All NSE EQ series.
- Load the NSE instrument list (symbol, token, series, ISIN) daily before market open.
- Exclude non-EQ series, suspended, and illiquid stocks based on configurable minimum price and minimum average volume.
- Equity cash market only. Futures and options are out of scope.

### FR-03: Market Data Ingestion
- Fetch historical daily OHLCV data for ADR calculation from the primary data provider (Fyers) through a data-provider interface (see Section 6).
- Obtain live prices during market hours (09:15–15:30 IST) using batched quote requests (maximum 50 symbols per request) and/or the data WebSocket (maximum 100 symbols), within the free-plan limits in Section 6.
- Handle API rate limits using batching, backoff, and retries.
- Store daily and intraday data needed for calculations.
- Adjust for corporate actions (splits, bonus) so the ADR is not distorted.

### FR-04: ADR Calculation Engine
- Calculate ADR(N), ADR %, Upper Level, and Lower Level for every stock in the selected universe before market open each trading day.
- Support configurable N, multiplier, and anchor price.
- Cache the computed levels for use during the trading session.
- Log inputs and outputs for each calculation for auditability.

### FR-05: Crossing Detection
- Evaluate live prices against the Upper and Lower levels.
- Record the following for every crossing: symbol, direction (UPPER/LOWER), level value, price at crossing, timestamp, volume at crossing, ADR %, and percentage move from anchor.
- Avoid duplicate alerts for the same stock and direction on the same day (the first crossing is the event; later ticks only update the status).
- Mark a stock as "Reverted" if the price returns inside the ADR band.
- Support an end-of-day scan mode using daily close prices.

### FR-06: Dashboard
- Two lists: **Crossed Upper ADR** and **Crossed Lower ADR**.
- Columns: Symbol, LTP, Anchor, ADR, ADR %, Upper/Lower Level, % Move, Volume vs Average Volume, Crossing Time, Status.
- Sorting, filtering, and search.
- Auto-refresh during market hours (polling interval configurable).
- Export results to CSV or Excel.
- Display the last data refresh time and data delay status.
- Display clear messages when the market is closed or data is unavailable.

### FR-07: AI Assistant
- Accept natural language questions about the current or historical scan results.
- Translate the question into structured filters applied to the scan data (not free-form calculation by the model).
- Generate a short summary of the scan, for example: number of crossings on each side, sector concentration, and the strongest movers by ADR multiple.
- Explain why a stock appears in a list (show the formula inputs and values).
- Refuse or redirect requests for buy/sell recommendations, price targets, or guaranteed outcomes.
- Display the following disclaimer with AI responses: "For information and education only. Not investment advice."

### FR-08: Alerts
- Allow users to enable alerts for upper crossings, lower crossings, or both.
- Deliver alerts through at least one channel (email through Amazon SES or WhatsApp/Telegram, to be confirmed).
- Limit alert frequency to avoid flooding (batching and per-stock cooldown).

### FR-09: Scan History
- Store daily scan results for a configurable retention period (default 90 days).
- Allow users to view past dates and compare how many stocks crossed on each side.

### FR-10: Logout
- Provide a Logout button.
- Terminate the Cognito session and redirect the user to the login page.
- Prevent further protected API access using an expired or invalid token.

## 5. Proposed AWS Infrastructure

| Component | AWS / External Service | Responsibility |
|---|---|---|
| Frontend hosting | Amazon S3 + Amazon CloudFront | Host and serve the web application |
| Authentication | Amazon Cognito | User authentication |
| API | Amazon API Gateway REST API | Expose dashboard, filter, and chat APIs |
| Backend | AWS Lambda (Python) | Scan APIs, AI query handling |
| Scheduling | Amazon EventBridge Scheduler | Pre-market ADR calculation, EOD scan, instrument refresh |
| Live data processing | Scheduled AWS Lambda (quote polling); optional ECS Fargate worker for WebSocket | Fetch live prices and detect crossings* |
| Data store | Amazon DynamoDB | Daily levels, crossing events, user settings |
| Historical storage | Amazon S3 (Parquet) | Daily OHLCV and scan history |
| AI | Amazon Bedrock (foundation model) | Natural language to filters, summaries, explanations |
| Alerts | Amazon SES / SNS | Notification delivery |
| Secrets | AWS Secrets Manager / SSM Parameter Store | Broker API credentials and tokens |
| Monitoring | Amazon CloudWatch | Logs, metrics, alarms |
| Market data | Fyers API v3 (Standard plan, free) | Historical candles, live quotes, symbol master |

\* On the free Fyers plan the data WebSocket is limited to 100 symbols, so the default design for NIFTY 500 is a scheduled Lambda that polls the quotes API every 1–2 minutes (about 10 requests of 50 symbols per refresh). An always-on worker (ECS Fargate or EC2) is needed only if a WebSocket feed is used, for example for a NIFTY 50 or NIFTY 100 universe.

## 6. Data Source Requirements

### 6.1 Primary Data Source: Fyers API v3 (Standard / Free Plan)

- Fyers API v3 is the primary source of historical and live market data for NSE equities.
- Market data (historical and real-time) is provided at no charge to Fyers clients under the free Standard plan. A Fyers trading account and a Fyers API app with the Historical Data and Quotes & Market Data permissions are required.
- The application only reads market data. No order placement is in scope, so the static IP requirement (which applies to order placement only) does not apply.
- Fyers access is issued through an authentication flow. The access token lifetime and a compliant way to automate the daily refresh must be confirmed before development (see Section 11).
- Credentials (app ID, secret, tokens) must be stored in AWS Secrets Manager or SSM Parameter Store, never in source code.

### 6.2 Design Constraints from the Free Plan

| Feature | Standard (free) limit | Design impact |
|---|---|---|
| Quotes API | 50 symbols per request | Batch the universe in groups of 50. NIFTY 500 needs about 10 requests per refresh. |
| Data WebSocket | 100 symbols | Live streaming covers only NIFTY 50 or NIFTY 100. Use quote polling for larger universes. |
| Historical data (daily) | Last 5 years | Sufficient: ADR(N) needs only the last N daily candles (default 14, maximum 50). |
| Historical data (intraday) | Last 1 year | Not required for the ADR scan. |
| Tick-by-tick socket | 1 symbol | Not used. |
| Seconds data | Not available | Not used. Minimum detection interval is the quote polling interval. |

The design must not depend on any feature outside the Standard plan. Higher limits (Fyers Prime) are out of scope for the free build.

### 6.3 Data-Provider Abstraction

- All market data access must go through a provider-neutral interface (for example: get instruments, get daily candles, get quotes for a list of symbols, subscribe to symbols).
- Fyers is the first implementation. The interface must allow another broker API (for example Zerodha Kite Connect at about ₹500 per month, or another broker's data API) to be added without changing the calculation or crossing-detection logic.
- Provider-specific limits (batch size, WebSocket symbol cap, rate limits) are held in configuration, not hardcoded.

### 6.4 Supporting and Validation Source

- NSE end-of-day files may be used to validate ADR inputs or backfill history. NSE's website terms restrict automated data collection without consent, so the usage terms must be reviewed before any automated download.

### 6.5 Usage and Licensing

- Broker API data is licensed for the account holder's own use. The application is limited to personal use. Redistributing or displaying live data to other users may violate exchange data policies and would require a licensed data vendor.
- Fyers rate limits for the market data endpoints must be confirmed from the current Fyers plan documentation, and the request schedule (pre-market history calls, intraday quote polling) must stay within them.

## 7. Non-Functional Requirements

- HTTPS communication.
- Secure authentication and authorization.
- IAM least-privilege access.
- No credentials or secrets hardcoded in source code.
- Pre-market ADR calculation completes before 09:00 IST on trading days.
- Crossing detection within one polling interval (target 60–120 seconds for NIFTY 500 using quote polling; near real-time for NIFTY 50/100 if the WebSocket is used).
- Dashboard page load of 3 seconds or less for a 500-stock universe (target).
- Handle NSE trading holidays and special sessions (for example, Muhurat trading).
- Basic CloudWatch logging and alarms for data feed failure.
- Responsive frontend interface.

## 8. Acceptance Criteria

1. Frontend is accessible through CloudFront.
2. Unauthenticated users cannot access the dashboard or APIs.
3. ADR, Upper Level, and Lower Level values for sample stocks match an independent manual or spreadsheet calculation.
4. Stocks crossing the upper ADR level appear in the Upper list; stocks crossing the lower level appear in the Lower list.
5. A stock is not duplicated in a list for repeated ticks on the same day.
6. Filters (universe, multiplier, ADR period, volume) change the results correctly.
7. The AI assistant correctly converts at least 10 sample questions into the right filters.
8. The AI assistant does not produce buy/sell recommendations and shows the disclaimer.
9. Alerts are delivered for new crossings without duplicates.
10. EOD scan results are stored and viewable in history.
11. Logout works and protected APIs reject expired tokens.

## 9. Risks, Constraints, and Compliance

- **Regulatory:** Providing stock signals or recommendations to the public may fall under SEBI Research Analyst or Investment Adviser regulations. The product should initially be positioned as a screening tool for personal use. Obtain professional legal advice before offering it publicly or commercially.
- **Data licensing:** Broker API data is generally licensed for the account holder's own use. Redistributing live data to other users may be restricted (see Section 6.5).
- **Signal quality:** An ADR crossing is a volatility-based observation, not a prediction. Results must not be presented as guaranteed trading signals.
- **Data accuracy:** Corporate actions, circuit-limit stocks, and illiquid stocks can produce misleading ADR values.
- **API dependency:** Fyers API downtime, free-plan limits (50-symbol quotes, 100-symbol WebSocket), rate limits, or access token expiry can interrupt detection. The data-provider abstraction (Section 6.3) is the mitigation.
- **AI behavior:** The model may misinterpret queries. Structured filter output must be validated before execution.

## 10. Out of Scope

- Futures and options (F&O) instruments.
- Automated order placement or trade execution.
- Buy/sell recommendations, price targets, or portfolio advice.
- Backtesting engine and strategy performance analytics (candidate for a later phase).
- User self-registration workflows and subscription billing.
- Mobile native applications.
- Non-Indian markets.
- Advanced analytics and machine-learning price prediction.

## 11. Open Questions

1. Confirm the ADR definition (Average Daily Range) and the preferred defaults: N, anchor, and multiplier.
2. Should crossings be evaluated on live price, 5-minute candle close, or daily close?
3. Single user (personal use) or multiple users?
4. Preferred alert channel: Email, WhatsApp, or Telegram?
5. Should the scan cover NIFTY 500 only or all NSE EQ stocks? (All NSE EQ is roughly 2,000 stocks and about 40 quote requests per refresh on the free plan.)
6. What are the Fyers market data rate limits, and how long does the access token last? Can the daily login be automated compliantly?

## 12. Expected Deliverables

- Functional ADR scanner web application.
- Cognito authentication.
- Dashboard frontend.
- Python ADR calculation and crossing detection services.
- Market data ingestion service with a provider-neutral interface and Fyers implementation.
- AI assistant (Bedrock) for natural language filtering and summaries.
- Alerting module.
- API Gateway configuration.
- DynamoDB tables and S3 data storage.
- AWS SAM/CloudFormation deployment templates.
- Basic functional and calculation validation test results.
- Deployment documentation.

**End of Document**
