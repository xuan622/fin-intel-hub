---
name: fin-intel-hub
description: Comprehensive financial intelligence hub for SEC filings, earnings, crypto on-chain data, news sentiment, macro indicators, options flow, and global stock markets (US, China, Hong Kong, Taiwan, Japan, Korea). Use when users need to: (1) Retrieve SEC EDGAR filings (10-K, 10-Q, 8-K), (2) Track upcoming earnings and historical performance, (3) Monitor crypto on-chain metrics and whale alerts, (4) Analyze financial news sentiment, (5) Access macroeconomic indicators (Fed rates, CPI, unemployment), (6) Analyze options flow (Max Pain, unusual volume, call/put ratio), (7) Get global stock prices including Asian markets (HKEX, Tokyo, Taiwan, Korea, Shanghai, Shenzhen), or any financial data research and analysis tasks.
---

# Fin Intel Hub

Financial intelligence hub for OpenClaw. Supports global markets including US, China, Hong Kong, Taiwan, Japan, and Korea.

## Features

- **SEC Filings**: Retrieve 10-K, 10-Q, 8-K filings from EDGAR
- **Earnings Calendar**: Track upcoming earnings and historical beats/misses
- **Global Market Data**: US stocks (Alpha Vantage) + Asian markets (Yahoo Finance)
- **Asian Markets**: Hong Kong, Tokyo, Taiwan, Korea, Shanghai, Shenzhen
- **Options Flow**: Unusual activity, call/put ratio, Max Pain, sentiment analysis
- **Earnings Reports**: Historical earnings, beat/miss trends, next earnings date
- **Crypto On-Chain**: Monitor wallet flows, exchange inflows/outflows
- **News Sentiment**: Aggregate sentiment from financial news sources
- **Macro Dashboard**: Fed rates, CPI, unemployment data

## API Keys (Optional)

All API keys are **optional**. The skill works without any keys using Yahoo Finance for stock data.
Add keys to unlock additional features:

| Service | Purpose | Free Tier | Required? |
|---------|---------|-----------|-----------|
| Yahoo Finance | Global/Asian stocks, indices, futures, commodities | Unlimited | **No** |
| Alpha Vantage | US stocks, earnings | 25 calls/day | Optional |
| NewsAPI | Financial news sentiment | 100 requests/day | Optional |
| FRED API | Macroeconomic data | Unlimited | Optional |
| DeFiLlama | Crypto on-chain data | Unlimited | **No** |

## Quick Start

### SEC Filings
```python
from scripts.sec_filings import get_recent_filings

# Get last 5 10-K filings for Apple
filings = get_recent_filings(ticker="AAPL", form="10-K", limit=5)
```

### Stock Prices
```python
from scripts.market_data import get_price_history

# Get 30-day price history
prices = get_price_history(ticker="TSLA", days=30)
```

### Crypto Data
```python
from scripts.crypto_onchain import get_exchange_flows

# Monitor exchange inflows/outflows
flows = get_exchange_flows(exchange="binance", days=7)
```

## Scripts Reference

- `scripts/sec_filings.py` - SEC EDGAR integration
- `scripts/market_data.py` - US stock prices and earnings (Alpha Vantage)
- `scripts/yahoo_finance.py` - Global/Asian stock prices (Yahoo Finance)
- `scripts/crypto_onchain.py` - Blockchain data via DeFiLlama/CoinGecko
- `scripts/sentiment_news.py` - News sentiment analysis
- `scripts/macro_data.py` - FRED macroeconomic indicators
- `scripts/options_data.py` - Options chain, flow analysis, Max Pain, unusual activity
- `scripts/earnings_data.py` - Earnings history, trends, next earnings dates

### Asian Market Examples
```python
from scripts.yahoo_finance import get_hong_kong_stock, get_tokyo_stock, get_taiwan_stock

# Hong Kong - Tencent
prices = get_hong_kong_stock("0700", period="1y")

# Tokyo - Toyota
prices = get_tokyo_stock("7203", period="1y")

# Taiwan - TSMC
prices = get_taiwan_stock("2330", period="1y")
```

### Indices & Futures Examples
```python
from scripts.yahoo_finance import get_sp500, get_nikkei225, get_vix
from scripts.yahoo_finance import get_crude_oil, get_gold, list_available_indices

# Global indices (15+ available)
sp500 = get_sp500(period="1y")
nasdaq = get_nasdaq(period="1y")
nikkei = get_nikkei225(period="1y")
hang_seng = get_hang_seng(period="1y")
vix = get_vix(period="1mo")  # Fear index

# Futures (15+ available)
oil_futures = get_crude_oil(period="6mo")
gold_futures = get_gold(period="6mo")
sp_futures = get_sp500_futures(period="1mo")
natural_gas = get_natural_gas(period="6mo")

# List all available
indices = list_available_indices()
futures = list_available_futures()
```

### Options Analysis Examples
```python
from scripts.options_data import analyze_options_flow, get_unusual_options_activity
from scripts.options_data import get_max_pain, get_call_put_ratio

# Full options flow analysis
flow = analyze_options_flow("AAPL")
print(f"Call/Put Ratio: {flow['analysis']['call_put_ratio']}")
print(f"Max Pain: ${flow['analysis']['max_pain']}")
print(f"Sentiment: {flow['analysis']['sentiment']['bias']}")

# Unusual options activity (volume spike > 2x average)
unusual = get_unusual_options_activity("TSLA", threshold=2.0)
for alert in unusual[:5]:
    print(f"{alert['type']} ${alert['strike']}: {alert['volume']} contracts")

# Get Max Pain strike
max_pain = get_max_pain("SPY")
print(f"SPY Max Pain: ${max_pain}")
```

### Earnings Analysis Examples
```python
from scripts.earnings_data import get_earnings_history, get_next_earnings_date, analyze_earnings_trend

# Get earnings history
earnings = get_earnings_history("AAPL", limit=4)
for e in earnings:
    beat_miss = "BEAT" if e['beat'] else "MISS"
    print(f"{e['report_date']}: EPS ${e['eps_actual']} vs Est ${e['eps_estimate']} ({beat_miss})")

# Check next earnings date
next_date = get_next_earnings_date("TSLA")
print(f"Next earnings: {next_date['next_earnings_date']}")

# Analyze earnings trend (beat/miss streak)
trend = analyze_earnings_trend("MSFT")
print(f"Beat rate: {trend['beat_rate']}%")
print(f"Current streak: {trend['current_streak']}")
```

For detailed API documentation and data schemas, see `references/`.
