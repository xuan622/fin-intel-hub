import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class StockPrice:
    date: str
    open_price: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: float

@dataclass
class StockInfo:
    symbol: str
    name: str
    currency: str
    market: str
    sector: Optional[str]
    industry: Optional[str]
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    fifty_two_week_high: Optional[float]
    fifty_two_week_low: Optional[float]

class YahooFinanceClient:
    """Client for fetching global stock data from Yahoo Finance."""
    
    BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
    
    # Market suffix mappings
    MARKET_SUFFIXES = {
        "hong_kong": ".HK",
        "tokyo": ".T",
        "taiwan": ".TW",
        "korea": ".KS",
        "shanghai": ".SS",  # Or .SH
        "shenzhen": ".SZ",
        "singapore": ".SI",
        "australia": ".AX",
        "london": ".L",
        "germany": ".DE",
        "paris": ".PA",
        "toronto": ".TO",
        "bombay": ".BO",
        "nse": ".NS",
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def get_price_history(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> List[StockPrice]:
        """
        Get historical price data for any global stock.
        
        Args:
            symbol: Yahoo Finance symbol (e.g., '0700.HK', '7203.T', 'AAPL')
            period: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
            interval: '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'
        
        Returns:
            List of StockPrice objects
        """
        url = f"{self.BASE_URL}/{symbol}"
        params = {
            "period1": int((datetime.now() - self._parse_period(period)).timestamp()),
            "period2": int(datetime.now().timestamp()),
            "interval": interval,
            "events": "history",
            "includeAdjustedClose": "true"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if "chart" not in data or "result" not in data["chart"] or not data["chart"]["result"]:
                print(f"No data found for {symbol}")
                return []
            
            result = data["chart"]["result"][0]
            timestamps = result.get("timestamp", [])
            quote = result.get("indicators", {}).get("quote", [{}])[0]
            adjclose = result.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose", [])
            
            prices = []
            for i, ts in enumerate(timestamps):
                try:
                    prices.append(StockPrice(
                        date=datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
                        open_price=quote.get("open", [])[i] or 0,
                        high=quote.get("high", [])[i] or 0,
                        low=quote.get("low", [])[i] or 0,
                        close=quote.get("close", [])[i] or 0,
                        volume=int(quote.get("volume", [])[i] or 0),
                        adjusted_close=adjclose[i] if i < len(adjclose) else (quote.get("close", [])[i] or 0)
                    ))
                except (IndexError, TypeError):
                    continue
            
            return prices
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return []
    
    def _parse_period(self, period: str) -> datetime:
        """Convert period string to datetime."""
        now = datetime.now()
        
        if period == "1d":
            return now - timedelta(days=1)
        elif period == "5d":
            return now - timedelta(days=5)
        elif period == "1mo":
            return now - timedelta(days=30)
        elif period == "3mo":
            return now - timedelta(days=90)
        elif period == "6mo":
            return now - timedelta(days=180)
        elif period == "1y":
            return now - timedelta(days=365)
        elif period == "2y":
            return now - timedelta(days=730)
        elif period == "5y":
            return now - timedelta(days=1825)
        elif period == "ytd":
            return datetime(now.year, 1, 1)
        elif period == "max":
            return now - timedelta(days=365*20)
        else:
            return now - timedelta(days=365)
    
    def get_stock_info(self, symbol: str) -> Optional[StockInfo]:
        """Get company/stock metadata."""
        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
        params = {
            "modules": "assetProfile,summaryDetail,price"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = data.get("quoteSummary", {}).get("result", [{}])[0]
            
            profile = result.get("assetProfile", {})
            summary = result.get("summaryDetail", {})
            price = result.get("price", {})
            
            return StockInfo(
                symbol=symbol,
                name=price.get("longName") or price.get("shortName", symbol),
                currency=price.get("currency", "USD"),
                market=price.get("exchangeName", "Unknown"),
                sector=profile.get("sector"),
                industry=profile.get("industry"),
                market_cap=summary.get("marketCap", {}).get("raw") if isinstance(summary.get("marketCap"), dict) else summary.get("marketCap"),
                pe_ratio=summary.get("trailingPE", {}).get("raw") if isinstance(summary.get("trailingPE"), dict) else summary.get("trailingPE"),
                dividend_yield=summary.get("dividendYield", {}).get("raw") if isinstance(summary.get("dividendYield"), dict) else summary.get("dividendYield"),
                fifty_two_week_high=summary.get("fiftyTwoWeekHigh", {}).get("raw") if isinstance(summary.get("fiftyTwoWeekHigh"), dict) else summary.get("fiftyTwoWeekHigh"),
                fifty_two_week_low=summary.get("fiftyTwoWeekLow", {}).get("raw") if isinstance(summary.get("fiftyTwoWeekLow"), dict) else summary.get("fiftyTwoWeekLow")
            )
            
        except Exception as e:
            print(f"Error fetching info for {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote."""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {"interval": "1d", "range": "1d"}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if "chart" not in data or "result" not in data["chart"] or not data["chart"]["result"]:
                return None
            
            meta = data["chart"]["result"][0].get("meta", {})
            
            return {
                "symbol": symbol,
                "price": meta.get("regularMarketPrice"),
                "previous_close": meta.get("previousClose"),
                "currency": meta.get("currency"),
                "exchange": meta.get("exchangeName"),
                "market_state": meta.get("marketState")
            }
            
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None


def get_price_history(symbol: str, period: str = "1y") -> List[Dict]:
    """Convenience function to get price history as dicts."""
    client = YahooFinanceClient()
    prices = client.get_price_history(symbol, period)
    return [
        {
            "date": p.date,
            "open": p.open_price,
            "high": p.high,
            "low": p.low,
            "close": p.close,
            "volume": p.volume,
            "adjusted_close": p.adjusted_close
        }
        for p in prices
    ]


def get_stock_info(symbol: str) -> Optional[Dict]:
    """Get stock information."""
    client = YahooFinanceClient()
    info = client.get_stock_info(symbol)
    if info:
        return {
            "symbol": info.symbol,
            "name": info.name,
            "currency": info.currency,
            "market": info.market,
            "sector": info.sector,
            "industry": info.industry,
            "market_cap": info.market_cap,
            "pe_ratio": info.pe_ratio,
            "dividend_yield": info.dividend_yield,
            "52_week_high": info.fifty_two_week_high,
            "52_week_low": info.fifty_two_week_low
        }
    return None


def get_current_price(symbol: str) -> Optional[Dict]:
    """Get current price quote."""
    client = YahooFinanceClient()
    return client.get_current_price(symbol)


# Helper functions for Asian markets
def get_hong_kong_stock(code: str, **kwargs) -> List[Dict]:
    """
    Get Hong Kong stock data.
    
    Args:
        code: Stock code (e.g., '0700' for Tencent, '3690' for Meituan)
    """
    symbol = f"{code}.HK"
    return get_price_history(symbol, **kwargs)


def get_tokyo_stock(code: str, **kwargs) -> List[Dict]:
    """
    Get Tokyo Stock Exchange data.
    
    Args:
        code: Stock code (e.g., '7203' for Toyota, '6758' for Sony)
    """
    symbol = f"{code}.T"
    return get_price_history(symbol, **kwargs)


def get_taiwan_stock(code: str, **kwargs) -> List[Dict]:
    """
    Get Taiwan Stock Exchange data.
    
    Args:
        code: Stock code (e.g., '2330' for TSMC, '2317' for Foxconn)
    """
    symbol = f"{code}.TW"
    return get_price_history(symbol, **kwargs)


def get_korea_stock(code: str, **kwargs) -> List[Dict]:
    """
    Get Korea Exchange data.
    
    Args:
        code: Stock code (e.g., '005930' for Samsung, '035420' for Naver)
    """
    symbol = f"{code}.KS"
    return get_price_history(symbol, **kwargs)


def get_shanghai_stock(code: str, **kwargs) -> List[Dict]:
    """
    Get Shanghai Stock Exchange data.
    
    Args:
        code: Stock code (e.g., '600519' for Kweichow Moutai)
    """
    symbol = f"{code}.SS"
    return get_price_history(symbol, **kwargs)


def get_shenzhen_stock(code: str, **kwargs) -> List[Dict]:
    """
    Get Shenzhen Stock Exchange data.
    
    Args:
        code: Stock code (e.g., '000001' for Ping An Bank)
    """
    symbol = f"{code}.SZ"
    return get_price_history(symbol, **kwargs)


if __name__ == "__main__":
    # Test examples
    print("Testing Asian market data...")
    
    # Hong Kong - Tencent
    print("\n--- Hong Kong: Tencent (0700.HK) ---")
    tencent = get_current_price("0700.HK")
    if tencent:
        print(f"Tencent: {tencent['price']} {tencent['currency']}")
    
    # Japan - Toyota
    print("\n--- Japan: Toyota (7203.T) ---")
    toyota = get_current_price("7203.T")
    if toyota:
        print(f"Toyota: {toyota['price']} {toyota['currency']}")
    
    # Taiwan - TSMC
    print("\n--- Taiwan: TSMC (2330.TW) ---")
    tsmc = get_current_price("2330.TW")
    if tsmc:
        print(f"TSMC: {tsmc['price']} {tsmc['currency']}")
    
    # Korea - Samsung
    print("\n--- Korea: Samsung (005930.KS) ---")
    samsung = get_current_price("005930.KS")
    if samsung:
        print(f"Samsung: {samsung['price']} {samsung['currency']}")
