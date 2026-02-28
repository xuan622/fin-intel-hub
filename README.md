# Finance Data Intelligence

OpenClaw skill for comprehensive financial data scraping and analytics.

## Features

- **SEC Filings** — Retrieve 10-K, 10-Q, 8-K filings from EDGAR
- **Market Data** — Stock prices, earnings, fundamentals (Alpha Vantage)
- **Crypto On-Chain** — DeFi TVL, exchange flows, gas prices (DeFiLlama, CoinGecko)
- **News Sentiment** — Financial news analysis with sentiment scoring (NewsAPI)
- **Macro Data** — Fed rates, CPI, unemployment, GDP (FRED API)

## Quick Start

### 1. Install

Copy this skill folder to your OpenClaw skills directory:
```bash
cp -r finance-data-intelligence ~/.openclaw/skills/
```

### 2. Get API Keys (Free Tiers Available)

| Service | Purpose | Free Tier | Get Key |
|---------|---------|-----------|---------|
| Alpha Vantage | Stock prices, earnings | 25 calls/day | [alphavantage.co](https://www.alphavantage.co/support/#api-key) |
| NewsAPI | Financial news | 100 requests/day | [newsapi.org](https://newsapi.org/register) |
| FRED | Macroeconomic data | 120 requests/min | [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html) |
| DeFiLlama | DeFi TVL, crypto data | Unlimited (no key) | N/A |

### 3. Set Environment Variables

```bash
export ALPHA_VANTAGE_API_KEY="your_key"
export NEWS_API_KEY="your_key"
export FRED_API_KEY="your_key"
```

Or add to your `~/.bashrc` or `~/.zshrc` for persistence.

## Usage

### SEC Filings
```python
from scripts.sec_filings import get_recent_filings, get_latest_10k

# Get recent 10-K filings
filings = get_recent_filings("AAPL", form="10-K", limit=5)

# Get latest 10-K summary
latest = get_latest_10k("TSLA")
```

### Market Data
```python
from scripts.market_data import get_price_history, get_quote, get_company_overview

# Price history
prices = get_price_history("AAPL", days=30)

# Real-time quote
quote = get_quote("TSLA")

# Company fundamentals
overview = get_company_overview("MSFT")
```

### Crypto On-Chain
```python
from scripts.crypto_onchain import get_defi_tvl, get_top_exchanges, get_exchange_flows

# DeFi TVL
tvl = get_defi_tvl()  # Global
tvl_aave = get_defi_tvl("aave")  # Specific protocol

# Top exchanges
exchanges = get_top_exchanges(10)
```

### News Sentiment
```python
from scripts.sentiment_news import get_sentiment_summary

# Sentiment analysis for a ticker
sentiment = get_sentiment_summary(ticker="AAPL", days=7)
print(f"Sentiment: {sentiment['sentiment_label']}")  # Bullish/Bearish/Neutral
```

### Macro Data
```python
from scripts.macro_data import get_macro_dashboard, get_fed_rate, get_cpi

# Full dashboard
dashboard = get_macro_dashboard()

# Individual indicators
fed_rate = get_fed_rate()
cpi = get_cpi()
unemployment = get_unemployment()
```

## Project Structure

```
finance-data-intelligence/
├── SKILL.md                  # Skill documentation
├── README.md                 # This file
├── SECURITY.md               # Security hardening checklist
├── scripts/
│   ├── sec_filings.py        # SEC EDGAR integration
│   ├── market_data.py        # Alpha Vantage (stocks)
│   ├── crypto_onchain.py     # DeFiLlama, CoinGecko (crypto)
│   ├── sentiment_news.py     # NewsAPI (news + sentiment)
│   └── macro_data.py         # FRED API (macro indicators)
└── references/               # API documentation (optional)
```

## API Key Tiers

All APIs used have free tiers suitable for personal/research use:

- **Alpha Vantage**: 25 API calls/day free
- **NewsAPI**: 100 requests/day free  
- **FRED**: 120 requests/minute free
- **DeFiLlama**: Unlimited (no key required)
- **CoinGecko**: Free tier available

For higher limits, upgrade directly with the API providers.

## Security

- All API keys stored in environment variables only
- No hardcoded secrets
- HTTPS enforced on all API calls
- Request timeouts configured

See `SECURITY.md` for detailed security considerations.

## License

MIT — Free to use, modify, and distribute.

## Contributing

This is a Boring Life project. Built by AI, guided by humans.

---

**Built with 🏗️ by David (CTO, Boring Life)**
