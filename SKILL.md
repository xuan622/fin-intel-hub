---
name: finance-data-intelligence
description: Comprehensive financial data scraping and analytics for SEC filings, earnings, crypto on-chain data, news sentiment, macro indicators, and global stock markets (US, China, Hong Kong, Taiwan, Japan, Korea). Use when users need to: (1) Retrieve SEC EDGAR filings (10-K, 10-Q, 8-K), (2) Track upcoming earnings and historical performance, (3) Monitor crypto on-chain metrics and whale alerts, (4) Analyze financial news sentiment, (5) Access macroeconomic indicators (Fed rates, CPI, unemployment), (6) Get global stock prices including Asian markets (HKEX, Tokyo, Taiwan, Korea, Shanghai, Shenzhen), or any financial data research and analysis tasks.
---

# Finance Data Intelligence

Financial data scraping and analytics skill for OpenClaw. Supports global markets including US, China, Hong Kong, Taiwan, Japan, and Korea.

## Features

- **SEC Filings**: Retrieve 10-K, 10-Q, 8-K filings from EDGAR
- **Earnings Calendar**: Track upcoming earnings and historical beats/misses
- **Global Market Data**: US stocks (Alpha Vantage) + Asian markets (Yahoo Finance)
- **Asian Markets**: Hong Kong, Tokyo, Taiwan, Korea, Shanghai, Shenzhen
- **Crypto On-Chain**: Monitor wallet flows, exchange inflows/outflows
- **News Sentiment**: Aggregate sentiment from financial news sources
- **Macro Dashboard**: Fed rates, CPI, unemployment data

## API Keys Required

| Service | Purpose | Free Tier |
|---------|---------|-----------|
| Alpha Vantage | US stock prices, earnings | 25 calls/day |
| NewsAPI | Financial news | 100 requests/day |
| Dune Analytics | Crypto on-chain | Query via API |
| FRED API | Macroeconomic data | Unlimited |
| Yahoo Finance | Global/Asian stocks | No key needed |

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

For detailed API documentation and data schemas, see `references/`.
