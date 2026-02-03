"""Enhanced Web Research & Stock Data Agent with multi-source scraping."""

import logging
import requests
import os
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import wikipediaapi
from datetime import datetime

logger = logging.getLogger(__name__)


class DataCollectorAgent:
    """Agent for collecting real company and stock data from multiple web sources."""
    
    def __init__(self, llm=None):
        """Initialize Data Collector Agent."""
        self.llm = llm
        self._wiki = None
        self._session = None
    
    @property
    def wiki(self):
        """Lazy init Wikipedia API."""
        if self._wiki is None:
            self._wiki = wikipediaapi.Wikipedia('StockPulseAI/1.0', 'en')
        return self._wiki
    
    @property
    def session(self):
        """Lazy init requests session."""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
        return self._session
    
    def collect_data(self, company_name: str) -> Dict[str, Any]:
        """
        Collect company data from multiple sources.
        
        Returns:
            Dictionary with company_info, news, stock_performance, sources
        """
        logger.info(f"🔍 Starting research for: {company_name}")
        
        collected_data = {
            "company_name": company_name,
            "company_info": {},
            "news": [],
            "stock_performance": {},
            "sources": [],
            "data_quality": "unknown",
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # 1. Wikipedia
            wiki_data = self._search_wikipedia(company_name)
            if wiki_data:
                collected_data["company_info"].update(wiki_data)
                collected_data["sources"].append(f"Wikipedia: {wiki_data.get('url', 'N/A')}")
            
            # 2. News search
            news_data = self._search_news(company_name)
            if news_data:
                collected_data["news"] = news_data
                for article in news_data[:3]:
                    if article.get('url'):
                        collected_data["sources"].append(f"News: {article['url']}")
            
            # 3. Official website
            website_data = self._search_official_website(company_name)
            if website_data:
                collected_data["company_info"].update(website_data)
            
            # 4. Stock performance - multi-source
            stock_data = self._get_stock_data_multi_source(company_name)
            if stock_data:
                collected_data["stock_performance"] = stock_data
                collected_data["sources"].append(f"Stock: {stock_data.get('source', 'Web Search')}")
            
            # 5. Data quality
            collected_data["data_quality"] = self._assess_data_quality(collected_data)
            
            logger.info(f"✅ Research completed. Quality: {collected_data['data_quality']}")
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            collected_data["data_quality"] = "error"
            collected_data["error"] = str(e)
        
        return collected_data
    
    def _search_wikipedia(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Search Wikipedia for company info."""
        try:
            search_terms = [company_name, f"{company_name} company", f"{company_name} corporation"]
            
            for term in search_terms:
                page = self.wiki.page(term)
                if page.exists():
                    summary = page.summary[:800] if len(page.summary) > 800 else page.summary
                    return {
                        "description": summary,
                        "url": page.fullurl,
                        "title": page.title
                    }
            return None
        except Exception as e:
            logger.warning(f"Wikipedia error: {e}")
            return None
    
    def _search_news(self, company_name: str) -> List[Dict[str, Any]]:
        """Search for recent news."""
        news = []
        try:
            with DDGS() as ddgs:
                results = list(ddgs.news(f"{company_name} stock", max_results=5))
                for r in results:
                    news.append({
                        "title": r.get("title", ""),
                        "summary": r.get("body", "")[:200],
                        "url": r.get("url", ""),
                        "date": r.get("date", "")
                    })
        except Exception as e:
            logger.warning(f"News search error: {e}")
        return news
    
    def _search_official_website(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Try to find official website info."""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(f"{company_name} official website", max_results=1))
                if results:
                    return {"official_url": results[0].get("href", "")}
        except:
            pass
        return None
    
    def _get_stock_data_multi_source(self, company_name: str) -> Dict[str, Any]:
        """
        Get stock data from multiple sources.
        Priority: IndianAPI -> Web scraping from multiple financial sites
        """
        company_lower = company_name.lower().strip()
        ticker = company_name.upper()[:6]
        
        logger.info(f"📈 Looking up stock data for: {company_name}")
        
        # Try IndianAPI first (priority for Indian stocks)
        api_key = os.getenv("INDIAN_API_KEY", "")
        if api_key and api_key != "your_indian_api_key_here":
            indian_data = self._fetch_indian_api(company_name, api_key)
            if indian_data and indian_data.get("current_price") and "N/A" not in indian_data.get("current_price", ""):
                logger.info(f"✅ Got live data from IndianAPI for {company_name}")
                return indian_data
        
        # Fallback: Scrape stock data from web searches
        logger.info(f"📊 IndianAPI unavailable, scraping web for {company_name}...")
        return self._scrape_stock_data_from_web(company_name, ticker)
    
    def _fetch_indian_api(self, company_name: str, api_key: str) -> Optional[Dict[str, Any]]:
        """Fetch real-time stock data from IndianAPI (NSE/BSE)."""
        try:
            url = f"https://stock.indianapi.in/stock"
            params = {"name": company_name}
            headers = {"x-api-key": api_key}
            
            logger.info(f"🔄 Fetching IndianAPI: {company_name}")
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"⚠️ IndianAPI returned status {response.status_code}")
                return None
            
            data = response.json()
            
            # Check if we got valid data
            if not data or "error" in data:
                logger.warning(f"⚠️ IndianAPI error: {data.get('error', 'No data')}")
                return None
            
            # Parse stock data from response
            # IndianAPI returns data with currentPrice, percentChange, etc.
            current_price = data.get("currentPrice", {})
            
            # Get price from NSE or BSE
            nse_price = current_price.get("NSE", 0)
            bse_price = current_price.get("BSE", 0)
            price = nse_price or bse_price
            
            if not price:
                # Try alternate fields
                price = data.get("price", 0) or data.get("lastPrice", 0)
            
            if not price:
                return None
            
            # Get percentage change
            pct_change = data.get("percentChange", 0)
            if isinstance(pct_change, dict):
                pct_change = pct_change.get("NSE", 0) or pct_change.get("BSE", 0)
            pct_change = float(pct_change) if pct_change else 0
            
            # Determine trend
            trend = "bullish" if pct_change > 0 else ("bearish" if pct_change < 0 else "neutral")
            
            # Format price with 2 decimal places for accuracy
            price_formatted = f"₹{float(price):,.2f}"
            logger.info(f"✅ IndianAPI Price for {company_name}: {price_formatted} ({pct_change:+.2f}%)")
            
            return {
                "ticker": data.get("symbol", company_name.upper()[:6]),
                "company": data.get("companyName", company_name),
                "current_price": price_formatted,
                "change_24hr": f"{pct_change:+.2f}%",
                "price_change_pct": f"{pct_change:+.2f}%",
                "volume": data.get("totalTradedVolume", "N/A"),
                "trend": trend,
                "recommendation": self._get_recommendation(pct_change),
                "confidence": "High" if abs(pct_change) > 2 else "Moderate",
                "source": "IndianAPI (Live NSE/BSE)",
                "sources_analyzed": 1,
                "data_type": "live",
                "verified": True
            }
                
        except Exception as e:
            logger.warning(f"IndianAPI error for {company_name}: {e}")
        return None
    
    def _scrape_stock_data_from_web(self, company_name: str, ticker: str) -> Dict[str, Any]:
        """Scrape stock data from multiple financial websites via search."""
        logger.info(f"🌐 Searching multiple sources for {company_name} stock data...")
        
        stock_info = {
            "ticker": ticker,
            "company": company_name,
            "prices_found": [],
            "trends_found": [],
            "recommendations_found": [],
            "sources_checked": []
        }
        
        # Search queries for stock data
        search_queries = [
            f"{company_name} stock price today INR",
            f"{company_name} share price live",
            f"{company_name} stock buy or sell recommendation",
            f"{company_name} stock forecast"
        ]
        
        try:
            with DDGS() as ddgs:
                for query in search_queries:
                    results = list(ddgs.text(query, max_results=3))
                    for r in results:
                        snippet = r.get("body", "").lower()
                        title = r.get("title", "")
                        source = r.get("href", "")
                        
                        stock_info["sources_checked"].append(source[:50] if source else "")
                        
                        # Extract price mentions
                        self._extract_price_from_text(snippet, stock_info)
                        
                        # Extract trend signals
                        self._extract_trend_from_text(snippet, title, stock_info)
                        
                        # Extract recommendations
                        self._extract_recommendation_from_text(snippet, title, stock_info)
                        
        except Exception as e:
            logger.warning(f"Web scraping error: {e}")
        
        # Aggregate findings
        return self._aggregate_stock_findings(stock_info, company_name, ticker)
    
    def _extract_price_from_text(self, text: str, stock_info: Dict):
        """Extract price mentions from text."""
        import re
        # Look for INR prices
        inr_patterns = [
            r'₹\s*([\d,]+(?:\.\d+)?)',
            r'rs\.?\s*([\d,]+(?:\.\d+)?)',
            r'inr\s*([\d,]+(?:\.\d+)?)'
        ]
        for pattern in inr_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    price = float(match.replace(",", ""))
                    if 10 < price < 500000:  # Reasonable stock price range
                        stock_info["prices_found"].append(price)
                except:
                    pass
    
    def _extract_trend_from_text(self, snippet: str, title: str, stock_info: Dict):
        """Extract trend signals."""
        text = (snippet + " " + title).lower()
        
        bullish_words = ["rises", "gains", "jumps", "surges", "up", "rallies", "bullish", "positive", "growth"]
        bearish_words = ["falls", "drops", "declines", "down", "tumbles", "bearish", "negative", "loss"]
        
        for word in bullish_words:
            if word in text:
                stock_info["trends_found"].append("bullish")
                break
        for word in bearish_words:
            if word in text:
                stock_info["trends_found"].append("bearish")
                break
    
    def _extract_recommendation_from_text(self, snippet: str, title: str, stock_info: Dict):
        """Extract buy/sell recommendations."""
        text = (snippet + " " + title).lower()
        
        if any(w in text for w in ["strong buy", "buy rating", "outperform", "accumulate"]):
            stock_info["recommendations_found"].append("BUY")
        elif any(w in text for w in ["sell rating", "underperform", "avoid", "reduce"]):
            stock_info["recommendations_found"].append("SELL")
        elif any(w in text for w in ["hold", "neutral", "maintain"]):
            stock_info["recommendations_found"].append("HOLD")
    
    def _aggregate_stock_findings(self, stock_info: Dict, company_name: str, ticker: str) -> Dict[str, Any]:
        """Aggregate findings from multiple sources."""
        
        # Determine average price
        prices = stock_info.get("prices_found", [])
        avg_price = sum(prices) / len(prices) if prices else None
        
        # Determine trend consensus
        trends = stock_info.get("trends_found", [])
        if trends:
            bullish_count = trends.count("bullish")
            bearish_count = trends.count("bearish")
            trend = "bullish" if bullish_count > bearish_count else ("bearish" if bearish_count > bullish_count else "neutral")
        else:
            trend = "neutral"
        
        # Determine recommendation consensus
        recs = stock_info.get("recommendations_found", [])
        if recs:
            buy_count = recs.count("BUY")
            sell_count = recs.count("SELL")
            hold_count = recs.count("HOLD")
            if buy_count >= sell_count and buy_count >= hold_count:
                recommendation = "BUY"
                rec_confidence = "Strong" if buy_count > 2 else "Moderate"
            elif sell_count > buy_count and sell_count >= hold_count:
                recommendation = "SELL"
                rec_confidence = "Strong" if sell_count > 2 else "Moderate"
            else:
                recommendation = "HOLD"
                rec_confidence = "Moderate"
        else:
            recommendation = "HOLD"
            rec_confidence = "Low (limited data)"
        
        sources_count = len(set(stock_info.get("sources_checked", [])))
        
        # Format price with decimals for accuracy
        price_display = f"₹{avg_price:,.2f}" if avg_price else "Data unavailable"
        if avg_price:
            logger.info(f"📊 Web aggregated price for {company_name}: {price_display}")
        
        return {
            "ticker": ticker,
            "company": company_name,
            "current_price": price_display,
            "price_change_pct": f"~{abs(trends.count('bullish') - trends.count('bearish'))}% (est.)" if trends else "N/A",
            "trend": trend,
            "recommendation": recommendation,
            "confidence": rec_confidence,
            "sources_analyzed": max(sources_count, 1),
            "source": f"Web search ({sources_count} sources)",
            "data_type": "web_aggregated",
            "verified": False
        }
    
    def _get_recommendation(self, change_pct: float) -> str:
        """Simple recommendation based on price change."""
        if change_pct > 2:
            return "STRONG BUY"
        elif change_pct > 0:
            return "BUY"
        elif change_pct > -2:
            return "HOLD"
        else:
            return "SELL"
    
    def _assess_data_quality(self, data: Dict[str, Any]) -> str:
        """Assess data quality."""
        score = 0
        if data.get("company_info", {}).get("description"):
            score += 2
        if data.get("news") and len(data["news"]) > 0:
            score += 2
        if data.get("stock_performance", {}).get("current_price"):
            score += 2
        if len(data.get("sources", [])) >= 3:
            score += 1
        
        if score >= 5:
            return "high"
        elif score >= 3:
            return "medium"
        elif score >= 1:
            return "low"
        return "insufficient"
