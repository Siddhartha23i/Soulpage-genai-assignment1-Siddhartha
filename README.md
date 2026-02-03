# StockPulse AI

A multi-agent stock intelligence system that provides real-time stock analysis using AI-powered insights.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)

## 🚀 Live Demo

> **[View Live App](YOUR_STREAMLIT_LINK_HERE)** ← Add your deployment link here

---

## What It Does

StockPulse AI analyzes companies by:

1. **Collecting data** from multiple sources (Wikipedia, news, stock APIs)
2. **Processing insights** using LLM-powered analysis
3. **Generating recommendations** based on market trends

The system uses a multi-agent architecture where specialized agents handle different tasks:

- **Data Collector Agent** → Gathers company info, news, and stock prices
- **Analyst Agent** → Analyzes data and generates buy/sell recommendations

## Features

- Real-time stock price lookup (NSE/BSE via IndianAPI)
- Web-based fallback for global stocks
- AI-generated market insights
- Risk and opportunity analysis
- Clean, desktop-optimized UI

## Tech Stack

- **Frontend**: Streamlit
- **AI/LLM**: Groq (Mixtral, Llama 3.3)
- **Orchestration**: LangGraph
- **Data Sources**: Wikipedia API, DuckDuckGo Search, IndianAPI

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/stockpulse-ai.git
cd stockpulse-ai
```

### 2. Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
INDIAN_API_KEY=your_indian_api_key_here  # Optional, for NSE/BSE stocks
```

Get your API keys:
- **Groq**: [console.groq.com](https://console.groq.com)
- **IndianAPI**: [indianapi.in](https://indianapi.in) (optional)

### 5. Run the app

```bash
streamlit run ui/app.py
```

Open `http://localhost:8501` in your browser.

---

## Deployment on Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set the main file path: `ui/app.py`
5. Add secrets in Streamlit dashboard:
   - `GROQ_API_KEY`
   - `INDIAN_API_KEY` (optional)

---

## Project Structure

```
stockpulse-ai/
├── agents/
│   ├── data_collector.py   # Web scraping & API data collection
│   └── analyst.py          # LLM-powered analysis
├── graph/
│   └── orchestrator.py     # LangGraph workflow orchestration
├── ui/
│   └── app.py              # Streamlit frontend
├── utils/
│   ├── config.py           # Settings management
│   └── llm.py              # Groq LLM initialization
├── requirements.txt
└── README.md
```

---

## License

MIT License - feel free to use and modify.

---

Built with ❤️ using LangGraph and Groq
