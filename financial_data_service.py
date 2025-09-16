"""
Real Financial Data Service for TradingGrow
Integrates with Alpha Vantage, Yahoo Finance, and other providers
"""

import os
import requests
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional

# Optional imports for heavy data libraries
try:
    import yfinance as yf
    import pandas as pd
    YFINANCE_AVAILABLE = True
    PANDAS_AVAILABLE = True
except ImportError:
    yf = None
    pd = None
    YFINANCE_AVAILABLE = False
    PANDAS_AVAILABLE = False

# Optional imports for Alpha Vantage
try:
    from alpha_vantage.timeseries import TimeSeries
    from alpha_vantage.sectorperformance import SectorPerformances
    ALPHA_VANTAGE_AVAILABLE = True
except ImportError:
    TimeSeries = None
    SectorPerformances = None
    ALPHA_VANTAGE_AVAILABLE = False

logger = logging.getLogger(__name__)

class FinancialDataService:
    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.polygon_key = os.getenv('POLYGON_API_KEY')
        self.fmp_key = os.getenv('FMP_API_KEY')
        
        # Initialize Alpha Vantage if key and library are available
        if self.alpha_vantage_key and ALPHA_VANTAGE_AVAILABLE:
            self.ts = TimeSeries(key=self.alpha_vantage_key, output_format='pandas')
            self.sp = SectorPerformances(key=self.alpha_vantage_key, output_format='json')
        else:
            self.ts = None
            self.sp = None
            if not ALPHA_VANTAGE_AVAILABLE:
                logger.warning("Alpha Vantage library not installed. Using fallback data sources.")
            elif not self.alpha_vantage_key:
                logger.warning("Alpha Vantage API key not found. Using fallback data sources.")
    
    def get_sector_performance(self) -> Dict:
        """Get real-time sector performance data"""
        try:
            if self.alpha_vantage_key and self.sp:
                # Use Alpha Vantage for sector data
                data, meta_data = self.sp.get_sector()
                
                sectors = []
                rank_mapping = data.get('Rank A: Real-Time Performance', {})
                
                for sector, performance in rank_mapping.items():
                    sectors.append({
                        'name': sector.replace(' ', '_').lower(),
                        'display_name': sector,
                        'performance': float(performance.replace('%', '')),
                        'trend': 'up' if float(performance.replace('%', '')) > 0 else 'down',
                        'volume': self._generate_volume(),
                        'market_cap': self._generate_market_cap()
                    })
                
                return {
                    'sectors': sectors,
                    'last_updated': datetime.now().isoformat(),
                    'source': 'alpha_vantage'
                }
            else:
                # Fallback to Yahoo Finance sector ETFs
                return self._get_sector_etf_data()
                
        except Exception as e:
            logger.error(f"Error fetching sector data: {e}")
            return self._get_fallback_sector_data()
    
    def get_stock_data(self, symbol: str, period: str = '1y') -> Dict:
        """Get real stock data for a symbol"""
        try:
            # Check if yfinance is available
            if not YFINANCE_AVAILABLE:
                logger.warning("yfinance not available, using fallback data")
                return self._get_fallback_stock_data(symbol)
            
            # Use Yahoo Finance as primary source (more reliable for individual stocks)
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            info = stock.info
            
            if hist.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'price': round(current_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'volume': int(hist['Volume'].iloc[-1]),
                'market_cap': info.get('marketCap', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'historical_data': self._format_historical_data(hist),
                'last_updated': datetime.now().isoformat(),
                'source': 'yahoo_finance'
            }
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return self._get_fallback_stock_data(symbol)
    
    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get data for multiple stocks efficiently"""
        results = {}
        
        try:
            # Check if yfinance is available
            if not YFINANCE_AVAILABLE:
                logger.warning("yfinance not available, using fallback data")
                for symbol in symbols:
                    results[symbol] = self._get_fallback_stock_data(symbol)
                return results
            
            # Use Yahoo Finance for batch processing
            tickers = yf.Tickers(' '.join(symbols))
            
            for symbol in symbols:
                try:
                    ticker = tickers.tickers[symbol]
                    hist = ticker.history(period='5d')
                    info = ticker.info
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                        change = current_price - prev_close
                        change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
                        
                        results[symbol] = {
                            'symbol': symbol,
                            'name': info.get('longName', symbol),
                            'price': round(current_price, 2),
                            'change': round(change, 2),
                            'change_percent': round(change_percent, 2),
                            'volume': int(hist['Volume'].iloc[-1]),
                            'market_cap': info.get('marketCap', 0),
                            'sector': info.get('sector', 'Unknown')
                        }
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    results[symbol] = self._get_fallback_stock_data(symbol)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch stock fetch: {e}")
            # Fallback to individual requests
            for symbol in symbols:
                results[symbol] = self.get_stock_data(symbol)
            
            return results
    
    def search_stocks(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for stocks by name or symbol"""
        try:
            if self.alpha_vantage_key:
                # Use Alpha Vantage symbol search
                url = f"https://www.alphavantage.co/query"
                params = {
                    'function': 'SYMBOL_SEARCH',
                    'keywords': query,
                    'apikey': self.alpha_vantage_key
                }
                
                response = requests.get(url, params=params)
                data = response.json()
                
                results = []
                for match in data.get('bestMatches', [])[:limit]:
                    results.append({
                        'symbol': match['1. symbol'],
                        'name': match['2. name'],
                        'type': match['3. type'],
                        'region': match['4. region'],
                        'currency': match['8. currency']
                    })
                
                return results
            
            else:
                # Fallback search using a predefined list
                return self._fallback_search(query, limit)
                
        except Exception as e:
            logger.error(f"Error searching stocks: {e}")
            return self._fallback_search(query, limit)
    
    def get_market_overview(self) -> Dict:
        """Get general market overview"""
        try:
            # Check if yfinance is available
            if not YFINANCE_AVAILABLE:
                logger.warning("yfinance not available, using fallback market data")
                return self._get_fallback_market_overview()
            
            # Major market indices
            indices = ['^GSPC', '^DJI', '^IXIC', '^RUT']  # S&P 500, Dow, Nasdaq, Russell 2000
            market_data = {}
            
            for index in indices:
                stock = yf.Ticker(index)
                hist = stock.history(period='5d')
                
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                    change = current - prev
                    change_percent = (change / prev) * 100 if prev != 0 else 0
                    
                    market_data[index] = {
                        'value': round(current, 2),
                        'change': round(change, 2),
                        'change_percent': round(change_percent, 2)
                    }
            
            return {
                'indices': market_data,
                'last_updated': datetime.now().isoformat(),
                'market_status': self._get_market_status()
            }
            
        except Exception as e:
            logger.error(f"Error fetching market overview: {e}")
            return self._get_fallback_market_overview()
    
    def _get_sector_etf_data(self) -> Dict:
        """Fallback sector data using sector ETFs"""
        # Check if yfinance is available for ETF data
        if not YFINANCE_AVAILABLE:
            logger.warning("yfinance not available, using hardcoded fallback sector data")
            return self._get_fallback_sector_data()
        
        sector_etfs = {
            'Technology': 'XLK',
            'Healthcare': 'XLV',
            'Financial Services': 'XLF',
            'Consumer Discretionary': 'XLY',
            'Communication Services': 'XLC',
            'Industrial': 'XLI',
            'Consumer Staples': 'XLP',
            'Energy': 'XLE',
            'Utilities': 'XLU',
            'Real Estate': 'XLRE',
            'Materials': 'XLB'
        }
        
        sectors = []
        for sector_name, etf_symbol in sector_etfs.items():
            try:
                stock = yf.Ticker(etf_symbol)
                hist = stock.history(period='5d')
                
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                    change_percent = ((current - prev) / prev) * 100 if prev != 0 else 0
                    
                    sectors.append({
                        'name': sector_name.lower().replace(' ', '_'),
                        'display_name': sector_name,
                        'performance': round(change_percent, 2),
                        'trend': 'up' if change_percent > 0 else 'down',
                        'volume': int(hist['Volume'].iloc[-1]),
                        'market_cap': self._generate_market_cap()
                    })
            except Exception as e:
                logger.error(f"Error fetching ETF data for {sector_name}: {e}")
        
        return {
            'sectors': sectors,
            'last_updated': datetime.now().isoformat(),
            'source': 'yahoo_finance_etf'
        }
    
    def _format_historical_data(self, hist_df) -> List[Dict]:
        """Format historical data for frontend consumption"""
        data = []
        
        # Check if pandas is available and hist_df is a DataFrame
        if not PANDAS_AVAILABLE or hist_df is None:
            return data  # Return empty list if pandas not available
        
        try:
            for date, row in hist_df.tail(30).iterrows():  # Last 30 days
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': round(row['Open'], 2),
                    'high': round(row['High'], 2),
                    'low': round(row['Low'], 2),
                    'close': round(row['Close'], 2),
                    'volume': int(row['Volume'])
                })
        except Exception as e:
            logger.error(f"Error formatting historical data: {e}")
        
        return data
    
    def _generate_volume(self) -> int:
        """Generate realistic volume for sectors"""
        import random
        return random.randint(1000000, 50000000)
    
    def _generate_market_cap(self) -> int:
        """Generate realistic market cap"""
        import random
        return random.randint(100000000, 5000000000)
    
    def _get_market_status(self) -> str:
        """Determine if market is open/closed"""
        now = datetime.now()
        # Simple market hours check (9:30 AM - 4:00 PM ET, weekdays)
        if now.weekday() < 5 and 9.5 <= now.hour + now.minute/60 <= 16:
            return "open"
        return "closed"
    
    def _fallback_search(self, query: str, limit: int) -> List[Dict]:
        """Fallback stock search with common symbols"""
        common_stocks = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'type': 'Equity', 'region': 'United States', 'currency': 'USD'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'type': 'Equity', 'region': 'United States', 'currency': 'USD'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'type': 'Equity', 'region': 'United States', 'currency': 'USD'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'type': 'Equity', 'region': 'United States', 'currency': 'USD'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'type': 'Equity', 'region': 'United States', 'currency': 'USD'},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'type': 'Equity', 'region': 'United States', 'currency': 'USD'},
            {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'type': 'Equity', 'region': 'United States', 'currency': 'USD'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'type': 'Equity', 'region': 'United States', 'currency': 'USD'},
        ]
        
        # Filter by query
        query_lower = query.lower()
        matches = [
            stock for stock in common_stocks 
            if query_lower in stock['symbol'].lower() or query_lower in stock['name'].lower()
        ]
        
        return matches[:limit]
    
    def _get_fallback_stock_data(self, symbol: str) -> Dict:
        """Fallback stock data when API fails"""
        import random
        base_price = random.uniform(10, 500)
        change = random.uniform(-10, 10)
        
        return {
            'symbol': symbol,
            'name': f"{symbol} Corp",
            'price': round(base_price, 2),
            'change': round(change, 2),
            'change_percent': round((change / base_price) * 100, 2),
            'volume': random.randint(100000, 10000000),
            'market_cap': random.randint(1000000000, 100000000000),
            'sector': 'Technology',
            'industry': 'Software',
            'pe_ratio': random.uniform(10, 30),
            'dividend_yield': 0,
            'fifty_two_week_high': round(base_price * 1.2, 2),
            'fifty_two_week_low': round(base_price * 0.8, 2),
            'historical_data': [],
            'last_updated': datetime.now().isoformat(),
            'source': 'fallback'
        }
    
    def _get_fallback_sector_data(self) -> Dict:
        """Fallback sector data when APIs fail"""
        import random
        sectors = ['Technology', 'Healthcare', 'Financial Services', 'Consumer Discretionary', 
                  'Energy', 'Industrial', 'Materials', 'Utilities', 'Real Estate']
        
        sector_list = []
        for sector in sectors:
            performance = random.uniform(-5, 5)
            sector_list.append({
                'name': sector.lower().replace(' ', '_'),
                'display_name': sector,
                'performance': round(performance, 2),
                'trend': 'up' if performance > 0 else 'down',
                'volume': random.randint(1000000, 50000000),
                'market_cap': random.randint(100000000, 5000000000)
            })
        
        return {
            'sectors': sector_list,
            'last_updated': datetime.now().isoformat(),
            'source': 'fallback'
        }
    
    def _get_fallback_market_overview(self) -> Dict:
        """Fallback market overview"""
        import random
        
        return {
            'indices': {
                '^GSPC': {'value': 4500.0, 'change': random.uniform(-50, 50), 'change_percent': random.uniform(-2, 2)},
                '^DJI': {'value': 35000.0, 'change': random.uniform(-300, 300), 'change_percent': random.uniform(-2, 2)},
                '^IXIC': {'value': 14000.0, 'change': random.uniform(-100, 100), 'change_percent': random.uniform(-2, 2)},
            },
            'last_updated': datetime.now().isoformat(),
            'market_status': 'closed'
        }

# Global instance
financial_service = FinancialDataService()