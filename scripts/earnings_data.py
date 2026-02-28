import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class EarningsEvent:
    ticker: str
    company_name: str
    report_date: str
    report_time: str  # 'bmo' (before market open), 'amc' (after market close), 'tns' (time not supplied)
    eps_estimate: Optional[float]
    eps_actual: Optional[float]
    revenue_estimate: Optional[float]
    revenue_actual: Optional[float]
    surprise_pct: Optional[float]
    market_cap: Optional[float]

class EarningsClient:
    """Client for fetching earnings calendar and reports from Yahoo Finance."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def get_upcoming_earnings(
        self, 
        days_ahead: int = 7,
        min_market_cap: Optional[float] = None
    ) -> List[EarningsEvent]:
        """
        Get upcoming earnings calendar.
        
        Args:
            days_ahead: Number of days to look ahead (default 7)
            min_market_cap: Minimum market cap in billions (optional filter)
        
        Returns:
            List of upcoming earnings events
        """
        try:
            # Yahoo Finance earnings calendar URL
            url = "https://finance.yahoo.com/calendar/earnings"
            
            # Get today's date and future date
            today = datetime.now()
            future = today + timedelta(days=days_ahead)
            
            # Yahoo's earnings calendar is hard to scrape directly
            # Alternative: Use their API endpoint
            events = []
            
            # For now, return a helpful message about the feature
            # In production, this would scrape or use an API
            return {
                "note": "Upcoming earnings feature - Yahoo Finance data",
                "date_range": f"{today.strftime('%Y-%m-%d')} to {future.strftime('%Y-%m-%d')}",
                "suggestion": "For specific stock earnings, use get_earnings_history(ticker)"
            }
            
        except Exception as e:
            return {"error": f"Error fetching earnings calendar: {e}"}
    
    def get_earnings_history(
        self, 
        ticker: str,
        limit: int = 4
    ) -> List[Dict]:
        """
        Get historical earnings data for a specific stock.
        
        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            limit: Number of past earnings to retrieve (default 4 quarters)
        
        Returns:
            List of historical earnings results
        """
        try:
            # Yahoo Finance earnings API
            url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
            params = {
                "modules": "earningsHistory"
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if "quoteSummary" not in data or not data["quoteSummary"]["result"]:
                return []
            
            result = data["quoteSummary"]["result"][0]
            earnings_history = result.get("earningsHistory", {}).get("history", [])
            
            events = []
            for item in earnings_history[:limit]:
                try:
                    eps_actual = item.get("epsActual", {}).get("raw") if isinstance(item.get("epsActual"), dict) else item.get("epsActual")
                    eps_estimate = item.get("epsEstimate", {}).get("raw") if isinstance(item.get("epsEstimate"), dict) else item.get("epsEstimate")
                    
                    surprise = None
                    if eps_actual and eps_estimate and eps_estimate != 0:
                        surprise = ((eps_actual - eps_estimate) / abs(eps_estimate)) * 100
                    
                    events.append({
                        "ticker": ticker.upper(),
                        "report_date": datetime.fromtimestamp(item.get("quarter", 0)).strftime("%Y-%m-%d") if item.get("quarter") else None,
                        "eps_actual": eps_actual,
                        "eps_estimate": eps_estimate,
                        "surprise_pct": round(surprise, 2) if surprise else None,
                        "beat": eps_actual > eps_estimate if eps_actual and eps_estimate else None
                    })
                except:
                    continue
            
            return events
            
        except Exception as e:
            print(f"Error fetching earnings for {ticker}: {e}")
            return []
    
    def get_next_earnings_date(self, ticker: str) -> Optional[Dict]:
        """
        Get the next earnings date for a stock.
        
        Args:
            ticker: Stock symbol
        
        Returns:
            Dictionary with next earnings info or None
        """
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            if "chart" not in data or not data["chart"]["result"]:
                return None
            
            meta = data["chart"]["result"][0].get("meta", {})
            
            # Try to get earnings date from calendar module
            cal_url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
            cal_params = {"modules": "calendarEvents"}
            
            cal_response = self.session.get(cal_url, params=cal_params, timeout=10)
            cal_data = cal_response.json()
            
            if "quoteSummary" in cal_data and cal_data["quoteSummary"]["result"]:
                calendar = cal_data["quoteSummary"]["result"][0].get("calendarEvents", {})
                earnings_date = calendar.get("earnings", {}).get("earningsDate", [])
                
                if earnings_date:
                    return {
                        "ticker": ticker.upper(),
                        "next_earnings_date": datetime.fromtimestamp(earnings_date[0]).strftime("%Y-%m-%d"),
                        "company_name": meta.get("symbol"),
                        "note": "Date may change - confirm with company"
                    }
            
            return None
            
        except Exception as e:
            print(f"Error fetching next earnings for {ticker}: {e}")
            return None
    
    def analyze_earnings_trend(self, ticker: str) -> Dict[str, Any]:
        """
        Analyze earnings trend for a stock (beat/miss streak).
        
        Args:
            ticker: Stock symbol
        
        Returns:
            Analysis of earnings consistency
        """
        history = self.get_earnings_history(ticker, limit=8)  # Last 2 years
        
        if not history:
            return {"error": f"No earnings history found for {ticker}"}
        
        beats = sum(1 for h in history if h.get("beat") is True)
        misses = sum(1 for h in history if h.get("beat") is False)
        
        avg_surprise = None
        surprises = [h["surprise_pct"] for h in history if h.get("surprise_pct") is not None]
        if surprises:
            avg_surprise = sum(surprises) / len(surprises)
        
        # Determine streak
        streak_type = None
        streak_count = 0
        for h in history:
            if h.get("beat") is True:
                if streak_type == "beat":
                    streak_count += 1
                else:
                    streak_type = "beat"
                    streak_count = 1
            elif h.get("beat") is False:
                if streak_type == "miss":
                    streak_count += 1
                else:
                    streak_type = "miss"
                    streak_count = 1
        
        return {
            "ticker": ticker.upper(),
            "total_quarters": len(history),
            "beats": beats,
            "misses": misses,
            "beat_rate": round(beats / len(history) * 100, 1) if history else 0,
            "current_streak": f"{streak_count} {'beats' if streak_type == 'beat' else 'misses'}" if streak_type else "N/A",
            "avg_surprise_pct": round(avg_surprise, 2) if avg_surprise else None,
            "recent_history": history[:4]
        }


# Convenience functions
def get_earnings_history(ticker: str, limit: int = 4) -> List[Dict]:
    """Get historical earnings for a stock."""
    client = EarningsClient()
    return client.get_earnings_history(ticker, limit)


def get_next_earnings_date(ticker: str) -> Optional[Dict]:
    """Get next earnings date for a stock."""
    client = EarningsClient()
    return client.get_next_earnings_date(ticker)


def analyze_earnings_trend(ticker: str) -> Dict[str, Any]:
    """Analyze earnings beat/miss trend."""
    client = EarningsClient()
    return client.analyze_earnings_trend(ticker)


def check_earnings_soon(ticker: str, days: int = 14) -> Dict[str, Any]:
    """
    Check if a stock has earnings coming up soon.
    
    Returns:
        Dict with earnings info and recommendation
    """
    next_earnings = get_next_earnings_date(ticker)
    
    if not next_earnings:
        return {
            "ticker": ticker.upper(),
            "has_earnings_soon": False,
            "message": "No upcoming earnings date found"
        }
    
    earnings_date = datetime.strptime(next_earnings["next_earnings_date"], "%Y-%m-%d")
    today = datetime.now()
    days_until = (earnings_date - today).days
    
    # Get trend analysis
    trend = analyze_earnings_trend(ticker)
    
    return {
        "ticker": ticker.upper(),
        "has_earnings_soon": days_until <= days,
        "earnings_date": next_earnings["next_earnings_date"],
        "days_until": days_until,
        "historical_beat_rate": trend.get("beat_rate", "N/A"),
        "avg_surprise": trend.get("avg_surprise_pct", "N/A"),
        "note": "High volatility expected around earnings date"
    }


if __name__ == "__main__":
    # Test
    print("Testing earnings data...")
    
    # Test earnings history
    print("\n=== AAPL Earnings History ===")
    history = get_earnings_history("AAPL", limit=4)
    for h in history:
        beat_miss = "BEAT" if h.get("beat") else "MISS"
        print(f"{h['report_date']}: EPS ${h['eps_actual']:.2f} vs Est ${h['eps_estimate']:.2f} ({beat_miss})")
    
    # Test next earnings
    print("\n=== AAPL Next Earnings ===")
    next_earnings = get_next_earnings_date("AAPL")
    if next_earnings:
        print(f"Next earnings: {next_earnings['next_earnings_date']}")
    
    # Test trend analysis
    print("\n=== AAPL Earnings Trend ===")
    trend = analyze_earnings_trend("AAPL")
    print(f"Beat rate: {trend.get('beat_rate')}%")
    print(f"Current streak: {trend.get('current_streak')}")
    print(f"Avg surprise: {trend.get('avg_surprise_pct')}%")
