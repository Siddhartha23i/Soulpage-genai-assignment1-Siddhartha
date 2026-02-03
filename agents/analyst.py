"""Analyst Agent - Generates concise insights and recommendations from collected data."""

import logging
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)


class AnalystAgent:
    """Agent for analyzing company data and generating actionable insights."""
    
    def __init__(self, llm):
        """Initialize Analyst with LLM."""
        self.llm = llm
        logger.info(f"📊 Analyst Agent initialized (model: {llm.model_name})")
    
    def analyze(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze collected data and generate insights.
        
        Returns:
            Dictionary with executive_summary, market_insights, risks_opportunities
        """
        company_name = raw_data.get("company_name", "Unknown")
        data_quality = raw_data.get("data_quality", "unknown")
        
        logger.info(f"📊 Analyzing data for: {company_name}")
        
        if data_quality in ["insufficient", "error"]:
            return self._insufficient_data_response(company_name, raw_data)
        
        try:
            summary = self._generate_summary(raw_data)
            insights = self._generate_insights(raw_data)
            risks = self._generate_risks_opportunities(raw_data)
            
            sources = raw_data.get("sources", [])
            sources_text = "\n".join([f"• {s}" for s in sources[:5]]) if sources else "No sources"
            
            return {
                "executive_summary": summary,
                "market_insights": insights,
                "risks_opportunities": risks,
                "data_sources": sources_text,
                "data_quality": data_quality
            }
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return self._error_response(company_name, str(e))
    
    def _insufficient_data_response(self, company_name: str, raw_data: Dict) -> Dict[str, str]:
        """Response when data is insufficient."""
        return {
            "executive_summary": f"Limited data available for {company_name}.",
            "market_insights": "• Insufficient data for detailed analysis",
            "risks_opportunities": "Risks:\n• Limited public information\n\nOpportunities:\n• Requires further research",
            "data_sources": "Limited sources found",
            "data_quality": "insufficient"
        }
    
    def _error_response(self, company_name: str, error: str) -> Dict[str, str]:
        """Response on error."""
        return {
            "executive_summary": f"Error analyzing {company_name}.",
            "market_insights": "• Analysis unavailable",
            "risks_opportunities": "• Technical error occurred",
            "data_sources": "Error",
            "data_quality": "error"
        }
    
    def _generate_summary(self, raw_data: Dict[str, Any]) -> str:
        """Generate brief executive summary."""
        company_name = raw_data.get("company_name", "Unknown")
        company_info = raw_data.get("company_info", {})
        stock = raw_data.get("stock_performance", {})
        
        description = company_info.get("description", "")[:400]
        
        # Check for disambiguation
        if "can refer to" in description.lower() or "may refer to" in description.lower():
            description = ""
        
        if not description and not stock:
            return f"**{company_name}** - A company in the market. Limited public information available."
        
        prompt = PromptTemplate(
            input_variables=["company_name", "description", "stock_info"],
            template="""Write 2 sentences about {company_name} the COMPANY (not the person).

Company Info: {description}
Stock: {stock_info}

Focus on what the company does. Just 2 short sentences. If info is limited, describe the industry."""
        )
        
        stock_info = f"{stock.get('current_price', 'N/A')}, {stock.get('trend', 'neutral')} trend"
        
        try:
            response = self.llm.invoke(prompt.format(
                company_name=company_name,
                description=description if description else "A company in the technology/business sector",
                stock_info=stock_info
            ))
            result = response.content.strip()
            # Double check for disambiguation in response
            if "can refer to" in result.lower() or "may refer to" in result.lower():
                return f"**{company_name}**\n\n{company_name} is a company operating in the market. Stock analysis based on available data."
            return f"**{company_name}**\n\n{result}"
        except Exception as e:
            logger.error(f"Summary error: {e}")
            return f"**{company_name}**\n\n{company_name} is a company. Analysis based on market data."
    
    def _generate_insights(self, raw_data: Dict[str, Any]) -> str:
        """Generate 3-4 bullet point insights."""
        company_name = raw_data.get("company_name", "Unknown")
        news = raw_data.get("news", [])
        stock = raw_data.get("stock_performance", {})
        
        news_text = "\n".join([f"- {n.get('title', '')}" for n in news[:4]])
        stock_text = f"Trend: {stock.get('trend', 'N/A')}, Price: {stock.get('current_price', 'N/A')}"
        
        prompt = PromptTemplate(
            input_variables=["company_name", "news", "stock"],
            template="""Give exactly 3 bullet insights for {company_name} stock.

News: {news}
Stock: {stock}

Format:
• Insight 1 (max 12 words)
• Insight 2 (max 12 words)  
• Insight 3 (max 12 words)

Only use provided data. No invented stats."""
        )
        
        try:
            response = self.llm.invoke(prompt.format(
                company_name=company_name,
                news=news_text if news_text else "No recent news",
                stock=stock_text
            ))
            return response.content.strip()
        except Exception as e:
            logger.error(f"Insights error: {e}")
            trend = stock.get("trend", "neutral")
            return f"• Stock showing {trend} trend\n• Market sentiment mixed\n• Monitor for changes"
    
    def _generate_risks_opportunities(self, raw_data: Dict[str, Any]) -> str:
        """Generate risks and opportunities assessment."""
        company_name = raw_data.get("company_name", "Unknown")
        news = raw_data.get("news", [])
        stock = raw_data.get("stock_performance", {})
        company_info = raw_data.get("company_info", {})
        
        context = company_info.get("description", "")[:300]
        news_text = "\n".join([f"- {n.get('title', '')}" for n in news[:3]])
        rec = stock.get("recommendation", "HOLD")
        
        prompt = PromptTemplate(
            input_variables=["company_name", "context", "news", "recommendation"],
            template="""Analyze risks and opportunities for {company_name}.

Context: {context}
News: {news}
Recommendation: {recommendation}

Format EXACTLY:
Risks:
• Risk 1 (max 10 words)
• Risk 2 (max 10 words)

Opportunities:
• Opportunity 1 (max 10 words)
• Opportunity 2 (max 10 words)

Be specific. No generic statements."""
        )
        
        try:
            response = self.llm.invoke(prompt.format(
                company_name=company_name,
                context=context if context else "Technology company",
                news=news_text if news_text else "No recent news",
                recommendation=rec
            ))
            return response.content.strip()
        except Exception as e:
            logger.error(f"Risks error: {e}")
            return """Risks:
• Market volatility may affect returns
• Limited historical data

Opportunities:
• Potential growth in sector
• Entry point for investment"""
