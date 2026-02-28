import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class OptionContract:
    symbol: str
    strike: float
    expiration: str
    option_type: str  # 'call' or 'put'
    last_price: float
    bid: float
    ask: float
    volume: int
    open_interest: int
    implied_volatility: float
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None

@dataclass
class OptionsAnalysis:
    ticker: str
    expiration: str
    call_volume: int
    put_volume: int
    call_put_ratio: float
    total_volume: int
    max_pain: float
    implied_volatility_avg: float
    unusual_activity: List[Dict]
    largest_positions: List[Dict]

class OptionsDataClient:
    """Client for fetching and analyzing options data from Yahoo Finance."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def get_options_chain(
        self, 
        ticker: str, 
        expiration: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get full options chain for a ticker.
        
        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            expiration: Expiration date (YYYY-MM-DD). If None, gets nearest expiration.
        
        Returns:
            Dictionary with calls, puts, and metadata
        """
        try:
            # First, get available expiration dates
            url = f"https://query1.finance.yahoo.com/v7/finance/options/{ticker}"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if "optionChain" not in data or not data["optionChain"]["result"]:
                return {"error": f"No options data found for {ticker}"}
            
            result = data["optionChain"]["result"][0]
            
            # Get expiration dates
            expirations = result.get("expirationDates", [])
            if not expirations:
                return {"error": f"No options expirations found for {ticker}"}
            
            # Use specified expiration or nearest
            if expiration:
                # Convert YYYY-MM-DD to timestamp
                exp_ts = int(datetime.strptime(expiration, "%Y-%m-%d").timestamp())
                if exp_ts not in expirations:
                    return {"error": f"Invalid expiration. Available: {self._format_expirations(expirations)}"}
            else:
                exp_ts = expirations[0]  # Nearest expiration
                expiration = datetime.fromtimestamp(exp_ts).strftime("%Y-%m-%d")
            
            # Fetch options chain for specific expiration
            url = f"https://query1.finance.yahoo.com/v7/finance/options/{ticker}"
            params = {"date": exp_ts}
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if "optionChain" not in data or not data["optionChain"]["result"]:
                return {"error": f"No options data for {ticker} on {expiration}"}
            
            result = data["optionChain"]["result"][0]
            options_data = result.get("options", [{}])[0]
            
            # Parse calls and puts
            calls = self._parse_options(options_data.get("calls", []), "call")
            puts = self._parse_options(options_data.get("puts", []), "put")
            
            # Get underlying stock info
            quote = result.get("quote", {})
            underlying_price = quote.get("regularMarketPrice")
            
            return {
                "ticker": ticker,
                "expiration": expiration,
                "expiration_timestamp": exp_ts,
                "underlying_price": underlying_price,
                "available_expirations": [datetime.fromtimestamp(ts).strftime("%Y-%m-%d") for ts in expirations[:10]],
                "calls": calls,
                "puts": puts,
                "call_count": len(calls),
                "put_count": len(puts)
            }
            
        except Exception as e:
            return {"error": f"Error fetching options: {str(e)}"}
    
    def _parse_options(self, options_list: List[Dict], option_type: str) -> List[OptionContract]:
        """Parse raw options data into OptionContract objects."""
        contracts = []
        for opt in options_list:
            contract = OptionContract(
                symbol=opt.get("contractSymbol", ""),
                strike=opt.get("strike", 0),
                expiration=datetime.fromtimestamp(opt.get("expiration", 0)).strftime("%Y-%m-%d"),
                option_type=option_type,
                last_price=opt.get("lastPrice", 0),
                bid=opt.get("bid", 0),
                ask=opt.get("ask", 0),
                volume=opt.get("volume", 0) or 0,
                open_interest=opt.get("openInterest", 0) or 0,
                implied_volatility=opt.get("impliedVolatility", 0) or 0,
                delta=opt.get("delta"),
                gamma=opt.get("gamma"),
                theta=opt.get("theta"),
                vega=opt.get("vega")
            )
            contracts.append(contract)
        return contracts
    
    def _format_expirations(self, timestamps: List[int]) -> List[str]:
        """Format expiration timestamps to readable dates."""
        return [datetime.fromtimestamp(ts).strftime("%Y-%m-%d") for ts in timestamps[:5]]
    
    def calculate_max_pain(self, chain: Dict[str, Any]) -> float:
        """
        Calculate Max Pain - the strike price where most options expire worthless.
        This is where option writers (market makers) have minimum payout.
        
        Formula: For each strike, calculate total value of all ITM options at expiration.
        The strike with lowest total value is Max Pain.
        """
        if "error" in chain:
            return 0.0
        
        calls = chain.get("calls", [])
        puts = chain.get("puts", [])
        
        # Get all unique strikes
        all_strikes = set()
        for c in calls:
            all_strikes.add(c.strike)
        for p in puts:
            all_strikes.add(p.strike)
        
        strikes = sorted(all_strikes)
        
        # Calculate pain at each strike
        min_pain = float('inf')
        max_pain_strike = 0.0
        
        for strike in strikes:
            total_pain = 0.0
            
            # Calculate loss for call writers if stock ends at this strike
            for call in calls:
                if strike > call.strike:  # Call is ITM
                    intrinsic = strike - call.strike
                    total_pain += intrinsic * call.open_interest * 100  # 100 shares per contract
            
            # Calculate loss for put writers if stock ends at this strike
            for put in puts:
                if strike < put.strike:  # Put is ITM
                    intrinsic = put.strike - strike
                    total_pain += intrinsic * put.open_interest * 100
            
            if total_pain < min_pain:
                min_pain = total_pain
                max_pain_strike = strike
        
        return max_pain_strike
    
    def analyze_options_flow(
        self, 
        ticker: str, 
        expiration: Optional[str] = None,
        volume_threshold: float = 1.5
    ) -> Dict[str, Any]:
        """
        Comprehensive options flow analysis.
        
        Args:
            ticker: Stock symbol
            expiration: Specific expiration or None for nearest
            volume_threshold: Multiplier for "unusual" volume (e.g., 1.5 = 50% above average)
        
        Returns:
            Analysis results including call/put ratio, max pain, unusual activity
        """
        chain = self.get_options_chain(ticker, expiration)
        
        if "error" in chain:
            return chain
        
        calls = chain.get("calls", [])
        puts = chain.get("puts", [])
        
        # Volume analysis
        call_volume = sum(c.volume for c in calls)
        put_volume = sum(p.volume for p in puts)
        total_volume = call_volume + put_volume
        
        # Call/Put ratio
        call_put_ratio = call_volume / put_volume if put_volume > 0 else float('inf')
        
        # Open interest
        call_oi = sum(c.open_interest for c in calls)
        put_oi = sum(p.open_interest for p in puts)
        
        # Average implied volatility
        call_iv = [c.implied_volatility for c in calls if c.implied_volatility > 0]
        put_iv = [p.implied_volatility for p in puts if p.implied_volatility > 0]
        avg_iv = (sum(call_iv) + sum(put_iv)) / (len(call_iv) + len(put_iv)) if (call_iv or put_iv) else 0
        
        # Calculate Max Pain
        max_pain = self.calculate_max_pain(chain)
        
        # Detect unusual volume
        unusual_activity = self._detect_unusual_volume(calls, puts, volume_threshold)
        
        # Find largest positions (by open interest)
        largest_positions = self._find_largest_positions(calls, puts)
        
        # Sentiment interpretation
        sentiment = self._interpret_sentiment(call_put_ratio, call_oi, put_oi)
        
        return {
            "ticker": ticker,
            "expiration": chain.get("expiration"),
            "underlying_price": chain.get("underlying_price"),
            "analysis": {
                "call_volume": call_volume,
                "put_volume": put_volume,
                "total_volume": total_volume,
                "call_put_ratio": round(call_put_ratio, 2),
                "call_open_interest": call_oi,
                "put_open_interest": put_oi,
                "total_open_interest": call_oi + put_oi,
                "avg_implied_volatility": round(avg_iv * 100, 2),  # As percentage
                "max_pain": max_pain,
                "sentiment": sentiment,
                "distance_to_max_pain": round(abs(chain.get("underlying_price", 0) - max_pain), 2) if max_pain else None
            },
            "unusual_activity": unusual_activity,
            "largest_positions": largest_positions,
            "available_expirations": chain.get("available_expirations", [])
        }
    
    def _detect_unusual_volume(
        self, 
        calls: List[OptionContract], 
        puts: List[OptionContract], 
        threshold: float
    ) -> List[Dict]:
        """Detect contracts with unusually high volume."""
        alerts = []
        
        # Calculate average volume for all contracts
        all_volumes = [c.volume for c in calls] + [p.volume for p in puts]
        avg_volume = sum(all_volumes) / len(all_volumes) if all_volumes else 0
        
        if avg_volume == 0:
            return alerts
        
        threshold_volume = avg_volume * threshold
        
        # Check calls
        for call in calls:
            if call.volume >= threshold_volume and call.volume > 10:  # Minimum 10 contracts
                alerts.append({
                    "type": "CALL",
                    "strike": call.strike,
                    "volume": call.volume,
                    "open_interest": call.open_interest,
                    "implied_volatility": round(call.implied_volatility * 100, 2),
                    "sentiment": "BULLISH" if call.strike > call.last_price else "SPECULATIVE"
                })
        
        # Check puts
        for put in puts:
            if put.volume >= threshold_volume and put.volume > 10:
                alerts.append({
                    "type": "PUT",
                    "strike": put.strike,
                    "volume": put.volume,
                    "open_interest": put.open_interest,
                    "implied_volatility": round(put.implied_volatility * 100, 2),
                    "sentiment": "BEARISH" if put.strike < put.last_price else "HEDGE"
                })
        
        # Sort by volume
        alerts.sort(key=lambda x: x["volume"], reverse=True)
        return alerts[:10]  # Top 10 unusual activities
    
    def _find_largest_positions(
        self, 
        calls: List[OptionContract], 
        puts: List[OptionContract]
    ) -> List[Dict]:
        """Find largest open interest positions."""
        all_contracts = []
        
        for call in calls:
            all_contracts.append({
                "type": "CALL",
                "strike": call.strike,
                "open_interest": call.open_interest,
                "implied_volatility": round(call.implied_volatility * 100, 2)
            })
        
        for put in puts:
            all_contracts.append({
                "type": "PUT",
                "strike": put.strike,
                "open_interest": put.open_interest,
                "implied_volatility": round(put.implied_volatility * 100, 2)
            })
        
        # Sort by open interest
        all_contracts.sort(key=lambda x: x["open_interest"], reverse=True)
        return all_contracts[:10]
    
    def _interpret_sentiment(self, call_put_ratio: float, call_oi: int, put_oi: int) -> Dict[str, str]:
        """Interpret market sentiment from options data."""
        oi_ratio = call_oi / put_oi if put_oi > 0 else float('inf')
        
        if call_put_ratio > 1.5 and oi_ratio > 1.2:
            return {"bias": "BULLISH", "strength": "STRONG", "description": "High call volume and open interest"}
        elif call_put_ratio > 1.2:
            return {"bias": "BULLISH", "strength": "MODERATE", "description": "Elevated call activity"}
        elif call_put_ratio < 0.7 and oi_ratio < 0.8:
            return {"bias": "BEARISH", "strength": "STRONG", "description": "High put volume and open interest"}
        elif call_put_ratio < 0.9:
            return {"bias": "BEARISH", "strength": "MODERATE", "description": "Elevated put activity"}
        else:
            return {"bias": "NEUTRAL", "strength": "WEAK", "description": "Balanced call/put activity"}


# Convenience functions
def get_options_chain(ticker: str, expiration: Optional[str] = None) -> Dict[str, Any]:
    """Get full options chain for a ticker."""
    client = OptionsDataClient()
    return client.get_options_chain(ticker, expiration)


def analyze_options_flow(
    ticker: str, 
    expiration: Optional[str] = None,
    volume_threshold: float = 1.5
) -> Dict[str, Any]:
    """Analyze options flow for unusual activity and sentiment."""
    client = OptionsDataClient()
    return client.analyze_options_flow(ticker, expiration, volume_threshold)


def get_max_pain(ticker: str, expiration: Optional[str] = None) -> float:
    """Get Max Pain strike price."""
    client = OptionsDataClient()
    chain = client.get_options_chain(ticker, expiration)
    return client.calculate_max_pain(chain)


def get_unusual_options_activity(ticker: str, threshold: float = 2.0) -> List[Dict]:
    """Get unusual options activity (high volume)."""
    client = OptionsDataClient()
    analysis = client.analyze_options_flow(ticker, volume_threshold=threshold)
    return analysis.get("unusual_activity", [])


def get_call_put_ratio(ticker: str, expiration: Optional[str] = None) -> Dict[str, Any]:
    """Get call/put ratio and sentiment."""
    client = OptionsDataClient()
    analysis = client.analyze_options_flow(ticker, expiration)
    
    if "error" in analysis:
        return analysis
    
    return {
        "ticker": ticker,
        "expiration": analysis.get("expiration"),
        "call_put_volume_ratio": analysis["analysis"]["call_put_ratio"],
        "call_put_oi_ratio": round(
            analysis["analysis"]["call_open_interest"] / analysis["analysis"]["put_open_interest"], 2
        ) if analysis["analysis"]["put_open_interest"] > 0 else None,
        "sentiment": analysis["analysis"]["sentiment"]
    }


if __name__ == "__main__":
    # Test
    print("Testing options data...")
    
    # Test options flow analysis
    print("\n=== AAPL Options Analysis ===")
    analysis = analyze_options_flow("AAPL")
    
    if "error" not in analysis:
        print(f"Expiration: {analysis['expiration']}")
        print(f"Underlying Price: ${analysis['underlying_price']}")
        print(f"Call/Put Ratio: {analysis['analysis']['call_put_ratio']}")
        print(f"Max Pain: ${analysis['analysis']['max_pain']}")
        print(f"Sentiment: {analysis['analysis']['sentiment']['bias']} ({analysis['analysis']['sentiment']['strength']})")
        
        if analysis['unusual_activity']:
            print(f"\nUnusual Activity (Top 3):")
            for alert in analysis['unusual_activity'][:3]:
                print(f"  {alert['type']} ${alert['strike']}: Volume={alert['volume']} ({alert['sentiment']})")
    else:
        print(f"Error: {analysis['error']}")
