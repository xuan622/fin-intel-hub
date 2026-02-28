# Fin Intel Hub

OpenClaw skill for comprehensive financial intelligence and analytics.

## Features

- **SEC Filings** — Retrieve 10-K, 10-Q, 8-K filings from EDGAR
- **Market Data** — Stock prices, earnings, fundamentals (Alpha Vantage + Yahoo Finance)
- **Asian Markets** — Hong Kong, Tokyo, Taiwan, Korea, Shanghai, Shenzhen exchanges
- **Indices & Futures** — 15+ global indices, commodity futures
- **Options Flow** — Unusual volume, call/put ratio, Max Pain, sentiment
- **Earnings Reports** — Historical earnings, beat/miss analysis, upcoming dates analysis
- **Crypto On-Chain** — DeFi TVL, exchange flows, gas prices (DeFiLlama, CoinGecko)
- **News Sentiment** — Financial news analysis with sentiment scoring (NewsAPI)
- **Macro Data** — Fed rates, CPI, unemployment, GDP (FRED API)

## Quick Start

### 1. Install

Copy this skill folder to your OpenClaw skills directory:
```bash
cp -r fin-intel-hub ~/.openclaw/skills/
```

### 2. Get API Keys (Optional)

**No API keys required to start!** The skill works out-of-the-box with Yahoo Finance for global stock data.

Add API keys to unlock additional features:

| Service | Purpose | Free Tier | Get Key |
|---------|---------|-----------|---------|
| **Yahoo Finance** | **Global stocks, indices, futures** | **Unlimited** | **No key needed** ✅ |
| Alpha Vantage | US stocks, earnings | 25 calls/day | [alphavantage.co](https://www.alphavantage.co/support/#api-key) |
| NewsAPI | Financial news sentiment | 100 requests/day | [newsapi.org](https://newsapi.org/register) |
| FRED | Macroeconomic data | 120 requests/min | [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html) |
| DeFiLlama | DeFi TVL, crypto data | Unlimited | N/A |

### 3. Set Environment Variables (Optional)

```bash
# Optional - only if you want these features
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

### Asian Markets
```python
from scripts.yahoo_finance import get_hong_kong_stock, get_tokyo_stock, get_taiwan_stock

# Hong Kong - Tencent (0700.HK)
prices = get_hong_kong_stock("0700", period="1y")

# Tokyo - Toyota (7203.T)
prices = get_tokyo_stock("7203", period="1y")

# Taiwan - TSMC (2330.TW)
prices = get_taiwan_stock("2330", period="1y")

# Korea - Samsung (005930.KS)
from scripts.yahoo_finance import get_korea_stock
prices = get_korea_stock("005930", period="1y")

# China - Shanghai/Shenzhen
from scripts.yahoo_finance import get_shanghai_stock, get_shenzhen_stock
prices = get_shanghai_stock("600519")  # Kweichow Moutai
prices = get_shenzhen_stock("000001")  # Ping An Bank
```

### Indices & Futures
```python
from scripts.yahoo_finance import get_sp500, get_nasdaq, get_nikkei225, get_hang_seng
from scripts.yahoo_finance import get_crude_oil, get_gold, get_sp500_futures

# Major Indices
sp500 = get_sp500(period="1y")
nasdaq = get_nasdaq(period="1y")
nikkei = get_nikkei225(period="1y")
hang_seng = get_hang_seng(period="1y")
vix = get_vix(period="1mo")  # Fear index

# Futures
oil_futures = get_crude_oil(period="6mo")
gold_futures = get_gold(period="6mo")
sp_futures = get_sp500_futures(period="1mo")

# List all available
from scripts.yahoo_finance import list_available_indices, list_available_futures
indices = list_available_indices()   # 15+ global indices
futures = list_available_futures()   # 15+ futures contracts
```

### Options Flow Analysis
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

# Get Max Pain strike (where most options expire worthless)
max_pain = get_max_pain("SPY")
print(f"SPY Max Pain: ${max_pain}")
```

### Earnings Reports
```python
from scripts.earnings_data import get_earnings_history, get_next_earnings_date, analyze_earnings_trend

# Get historical earnings with beat/miss
earnings = get_earnings_history("AAPL", limit=4)
for e in earnings:
    beat_miss = "BEAT" if e['beat'] else "MISS"
    print(f"{e['report_date']}: EPS ${e['eps_actual']} vs Est ${e['eps_estimate']} ({beat_miss})")

# Check next earnings date
next_date = get_next_earnings_date("TSLA")
print(f"Next earnings: {next_date['next_earnings_date']}")

# Analyze earnings consistency (beat rate, streak)
trend = analyze_earnings_trend("MSFT")
print(f"Beat rate: {trend['beat_rate']}%, Streak: {trend['current_streak']}")
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
fin-intel-hub/
├── SKILL.md                  # Skill documentation
├── README.md                 # This file
├── SECURITY.md               # Security hardening checklist
├── scripts/
│   ├── sec_filings.py        # SEC EDGAR integration
│   ├── market_data.py        # Alpha Vantage (US stocks)
│   ├── yahoo_finance.py      # Yahoo Finance (global/Asian stocks)
│   ├── options_data.py       # Options chain, flow analysis, Max Pain
│   ├── earnings_data.py      # Earnings history, trends, next earnings dates
│   ├── crypto_onchain.py     # DeFiLlama, CoinGecko (crypto)
│   ├── sentiment_news.py     # NewsAPI (news + sentiment)
│   └── macro_data.py         # FRED API (macro indicators)
└── references/               # API documentation (optional)
```

## API Key Tiers

All APIs used have free tiers suitable for personal/research use:

### No Key Required (Works Out-of-the-Box)
- **Yahoo Finance**: Unlimited - Global stocks, Asian markets, indices, futures, commodities, options
- **DeFiLlama**: Unlimited - DeFi TVL, crypto on-chain data
- **CoinGecko**: Free tier available - Crypto exchange data

### Optional Keys (Unlock Additional Features)
- **Alpha Vantage**: 25 API calls/day free - US stocks, earnings (Yahoo Finance covers this too)
- **NewsAPI**: 100 requests/day free - Financial news sentiment analysis
- **FRED**: 120 requests/minute free - US macroeconomic indicators

For higher limits, upgrade directly with the API providers.

## Security

- ✅ **Input Validation** - All ticker symbols sanitized (SQL injection prevention)
- ✅ **Rate Limiting** - Automatic throttling for all APIs (25/day Alpha Vantage, etc.)
- ✅ **Secure Logging** - Sensitive data (API keys, tokens) auto-redacted
- ✅ **Safe Errors** - No stack traces or sensitive info leaked to users
- ✅ **API Keys** - Environment variables only, no hardcoded secrets

See `SECURITY.md` for detailed security documentation.

## License

MIT - Free to use, modify, and distribute.

## Contributing

This is a Boring Life project. Built by AI, guided by humans.

---

**Built with 🏗️ by David (CTO, Boring Life)**
