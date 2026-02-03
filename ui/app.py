"""StockPulse AI - Multi-Agent Stock Intelligence System."""

import streamlit as st
import logging
from typing import Dict, Any
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import get_research_llm, get_analyst_llm, get_settings
from agents import DataCollectorAgent, AnalystAgent
from graph import Orchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def apply_styles():
    """Apply dark theme with good contrast for visibility."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #334155;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --accent-purple: #8b5cf6;
            --accent-blue: #3b82f6;
            --success: #22c55e;
            --danger: #ef4444;
            --warning: #f59e0b;
        }
        
        * { font-family: 'Inter', sans-serif; }
        
        .stApp { background: var(--bg-primary) !important; }
        
        /* Hero Section */
        .hero-box {
            background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 50%, #3b82f6 100%);
            border-radius: 20px;
            padding: 2.5rem;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(139, 92, 246, 0.3);
        }
        
        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            color: white;
            margin: 0;
            letter-spacing: -1px;
        }
        
        .hero-tagline {
            color: rgba(255,255,255,0.9);
            font-size: 1rem;
            font-style: italic;
            margin-top: 0.5rem;
        }
        
        /* Cards */
        .card {
            background: var(--bg-secondary);
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-radius: 16px;
            padding: 1.25rem;
            margin: 0.5rem 0;
        }
        
        .card-title {
            color: var(--text-primary);
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .card-content {
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.6;
        }
        
        /* Metric Display - Desktop Optimized */
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.5rem;
            margin: 1.5rem 0;
            padding: 0 2rem;
        }
        
        .metric-box {
            background: var(--bg-secondary);
            border-radius: 16px;
            padding: 1.5rem 1rem;
            text-align: center;
            border: 1px solid rgba(148, 163, 184, 0.15);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .metric-box:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }
        
        .metric-value {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-primary);
            white-space: nowrap;
            overflow: visible;
        }
        
        .metric-label {
            font-size: 0.85rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 0.5rem;
        }
        
        /* Trend Colors */
        .trend-up .metric-value { color: var(--success); }
        .trend-down .metric-value { color: var(--danger); }
        .trend-neutral .metric-value { color: var(--warning); }
        
        /* Price Verification Badges */
        .price-badge {
            font-size: 0.65rem;
            padding: 2px 6px;
            border-radius: 4px;
            margin-left: 4px;
            font-weight: 600;
        }
        .price-badge.verified {
            background: rgba(34, 197, 94, 0.2);
            color: var(--success);
        }
        .price-badge.estimated {
            background: rgba(245, 158, 11, 0.2);
            color: var(--warning);
        }
        
        /* Recommendation Badge */
        .rec-container {
            text-align: center;
            margin: 1.5rem 0;
        }
        
        .rec-badge {
            display: inline-block;
            padding: 1rem 3rem;
            border-radius: 50px;
            font-weight: 700;
            font-size: 1.4rem;
            text-transform: uppercase;
            letter-spacing: 3px;
            color: white;
        }
        
        .rec-buy { background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); }
        .rec-sell { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }
        .rec-hold { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
        
        .rec-confidence {
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-top: 0.75rem;
        }
        
        /* Insight Items */
        .insight-item {
            background: var(--bg-card);
            border-radius: 10px;
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            color: var(--text-primary);
            font-size: 0.9rem;
            border-left: 4px solid var(--accent-purple);
        }
        
        .insight-item.risk {
            border-left-color: var(--danger);
            background: rgba(239, 68, 68, 0.1);
        }
        
        .insight-item.opp {
            border-left-color: var(--success);
            background: rgba(34, 197, 94, 0.1);
        }
        
        /* Section Headers */
        .section-head {
            color: var(--text-primary);
            font-size: 1.15rem;
            font-weight: 600;
            margin: 1.5rem 0 0.75rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid rgba(148, 163, 184, 0.2);
        }
        
        /* Button */
        .stButton>button {
            background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
            color: white;
            font-weight: 600;
            padding: 0.875rem 2rem;
            border-radius: 12px;
            border: none;
            width: 100%;
            font-size: 1rem;
        }
        
        .stButton>button:hover {
            box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4);
        }
        
        /* Input */
        .stTextInput>div>div>input {
            background: var(--bg-secondary) !important;
            border: 2px solid rgba(148, 163, 184, 0.2) !important;
            border-radius: 12px !important;
            color: var(--text-primary) !important;
            font-size: 1rem !important;
            padding: 0.875rem 1rem !important;
        }
        
        .stTextInput>div>div>input:focus {
            border-color: var(--accent-purple) !important;
        }
        
        .stTextInput>div>div>input::placeholder {
            color: var(--text-secondary) !important;
        }
        
        /* Source Items */
        .source-box {
            background: var(--bg-card);
            border-radius: 8px;
            padding: 0.5rem 1rem;
            margin: 0.25rem 0;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }
        
        /* Hide defaults */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Fix Streamlit metric colors for dark mode */
        [data-testid="stMetricValue"] { color: var(--text-primary) !important; }
        [data-testid="stMetricLabel"] { color: var(--text-secondary) !important; }
        
        </style>
    """, unsafe_allow_html=True)


def display_results(results: Dict[str, Any]):
    """Display analysis results."""
    
    raw_data = results.get("raw_data", {})
    analysis = results.get("analysis_results", {})
    company = results.get("company_name", "Unknown")
    stock = raw_data.get("stock_performance", {})
    
    # Count actual sources
    sources_list = raw_data.get("sources", [])
    source_count = len(sources_list) if sources_list else 1
    
    # Company Header
    st.markdown(f"### 📊 {company}")
    
    # ===== COMPANY OVERVIEW =====
    st.markdown('<div class="section-head">📋 Company Overview</div>', unsafe_allow_html=True)
    summary = analysis.get("executive_summary", "Analyzing...")
    if "can refer to" in summary.lower():
        summary = f"**{company}** operates in the business sector. Analysis based on available market data."
    st.markdown(f'<div class="card"><div class="card-content">{summary}</div></div>', unsafe_allow_html=True)
    
    # ===== STOCK METRICS (Custom HTML - no ellipsis) =====
    st.markdown('<div class="section-head">💰 Stock Performance</div>', unsafe_allow_html=True)
    
    # Extract values
    price = stock.get("current_price", "N/A")
    change_raw = stock.get("price_change_pct", "N/A")
    if isinstance(change_raw, str):
        change_display = change_raw.split("(")[0].strip()
    else:
        change_display = str(change_raw)
    
    trend = stock.get("trend", "neutral")
    if trend == "bullish":
        trend_display = "🟢 Bullish"
        trend_class = "trend-up"
    elif trend == "bearish":
        trend_display = "🔴 Bearish"
        trend_class = "trend-down"
    else:
        trend_display = "🟡 Neutral"
        trend_class = "trend-neutral"
    
    # Check if price is verified (from live API)
    is_verified = stock.get("verified", False)
    price_badge = "✓ Live" if is_verified else "~ Est."
    price_class = "verified" if is_verified else "estimated"
    
    # Custom HTML grid for metrics (no truncation)
    st.markdown(f'''
        <div class="metric-grid">
            <div class="metric-box">
                <div class="metric-value">{price}</div>
                <div class="metric-label">💵 Price <span class="price-badge {price_class}">{price_badge}</span></div>
            </div>
            <div class="metric-box">
                <div class="metric-value">{change_display}</div>
                <div class="metric-label">📈 24hr Change</div>
            </div>
            <div class="metric-box {trend_class}">
                <div class="metric-value">{trend_display}</div>
                <div class="metric-label">📊 Trend</div>
            </div>
            <div class="metric-box">
                <div class="metric-value">{source_count}</div>
                <div class="metric-label">🌐 Sources</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # ===== RECOMMENDATION =====
    rec = stock.get("recommendation", "HOLD")
    confidence = stock.get("confidence", "Moderate")
    
    rec_class = "rec-buy" if "BUY" in rec else ("rec-sell" if rec == "SELL" else "rec-hold")
    rec_emoji = "🚀" if "BUY" in rec else ("⛔" if rec == "SELL" else "⏸️")
    
    st.markdown(f"""
        <div class="rec-container">
            <div class="rec-badge {rec_class}">{rec_emoji} {rec}</div>
            <div class="rec-confidence">Confidence: {confidence}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # ===== TWO COLUMNS: Insights + Risks =====
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-head">💡 Insights</div>', unsafe_allow_html=True)
        insights = analysis.get("market_insights", "")
        lines = [l.strip() for l in insights.split('\n') if l.strip() and ('•' in l or '-' in l)]
        
        for line in lines[:4]:
            clean = line.lstrip('•-0123456789. ')[:70]
            if clean:
                st.markdown(f'<div class="insight-item">✓ {clean}</div>', unsafe_allow_html=True)
        
        if not lines:
            st.markdown('<div class="insight-item">✓ Market data analyzed</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-head">⚖️ Risks & Opportunities</div>', unsafe_allow_html=True)
        risks_text = analysis.get("risks_opportunities", "")
        
        # Parse and display
        risk_lines = []
        opp_lines = []
        
        for line in risks_text.split('\n'):
            line = line.strip()
            if '•' in line or '-' in line:
                clean = line.lstrip('•-:RisksOpportunities ').strip()[:60]
                if clean:
                    if 'opportunit' in risks_text[:risks_text.find(line)].lower()[-50:]:
                        opp_lines.append(clean)
                    else:
                        risk_lines.append(clean)
        
        for r in risk_lines[:2]:
            st.markdown(f'<div class="insight-item risk">⚠️ {r}</div>', unsafe_allow_html=True)
        for o in opp_lines[:2]:
            st.markdown(f'<div class="insight-item opp">✅ {o}</div>', unsafe_allow_html=True)
        
        if not risk_lines and not opp_lines:
            st.markdown('<div class="insight-item risk">⚠️ Monitor market conditions</div>', unsafe_allow_html=True)
            st.markdown('<div class="insight-item opp">✅ Research entry points</div>', unsafe_allow_html=True)
    
    # ===== SOURCES =====
    with st.expander(f"📚 View {source_count} Data Sources"):
        if sources_list:
            for src in sources_list:
                st.markdown(f'<div class="source-box">🔗 {src}</div>', unsafe_allow_html=True)
        
        stock_src = stock.get("source", "")
        if stock_src:
            st.markdown(f'<div class="source-box">📈 {stock_src}</div>', unsafe_allow_html=True)
        
        st.caption(f"Quality: {raw_data.get('data_quality', 'N/A').upper()}")


def get_orchestrator():
    """Initialize AI system."""
    if 'orchestrator' not in st.session_state:
        try:
            settings = get_settings()
            research_llm = get_research_llm(temperature=settings.temperature)
            analyst_llm = get_analyst_llm(temperature=settings.temperature)
            
            data_collector = DataCollectorAgent(research_llm)
            analyst = AnalystAgent(analyst_llm)
            
            st.session_state.orchestrator = Orchestrator(data_collector, analyst)
            logger.info("✅ StockPulse ready!")
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()
    
    return st.session_state.orchestrator


def main():
    """Main application."""
    
    st.set_page_config(
        page_title="StockPulse AI",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    apply_styles()
    
    # Hero
    st.markdown("""
        <div class="hero-box">
            <h1 class="hero-title">StockPulse</h1>
            <p class="hero-tagline">"Where data meets intuition"</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Search
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        company = st.text_input("Search", placeholder="Enter company (Infosys, Tesla, Reliance...)", label_visibility="collapsed")
        if st.button("🔍 Analyze", type="primary", use_container_width=True):
            if company and len(company.strip()) >= 2:
                with st.spinner("🤖 AI analyzing..."):
                    try:
                        results = get_orchestrator().run(company.strip())
                        st.markdown("---")
                        display_results(results)
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Enter a valid company name")
    
    # Footer
    st.markdown("---")
    st.markdown('<p style="text-align:center;color:#64748b;font-size:0.85rem;">🤖 Multi-Agent AI • LangGraph • Groq</p>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
