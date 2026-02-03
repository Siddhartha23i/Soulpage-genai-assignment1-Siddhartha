# StockPulse AI

A multi-agent stock intelligence system that provides real-time stock analysis using AI-powered insights.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)

## Live Demo

> **[View Live App](YOUR_STREAMLIT_LINK_HERE)** ← Add your deployment link here

---

## Architecture

The system uses a **multi-agent architecture** built on LangGraph, where specialized agents handle different tasks while sharing context through a unified state.

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                              │
│                    (Company Name: "Tesla")                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LANGGRAPH ORCHESTRATOR                      │
│                   (Maintains Shared State)                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  AgentState: {company_name, raw_data, analysis_results}   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│  DATA COLLECTOR   │  │    VALIDATOR      │  │  ANALYST AGENT    │
│      AGENT        │─▶│     (Gate)        │─▶│  (LLM-Powered)    │
│                   │  │                   │  │                   │
│  • Wikipedia API  │  │  • Quality check  │  │  • Mixtral 8x7b   │
│  • News Search    │  │  • Data presence  │  │  • Llama 3.3 70b  │
│  • IndianAPI      │  │  • Pass/Fail      │  │  • Insights Gen   │
│  • Web Scraping   │  │                   │  │                   │
└───────────────────┘  └───────────────────┘  └───────────────────┘
            │                                           │
            └───────────────────┬───────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      STREAMLIT UI                               │
│         Stock Price │ Trend │ Recommendation │ Insights         │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Flow

```
START ──▶ Data Collector ──▶ Validator ──┬──▶ Analyst ──▶ END
                                         │
                                         └──▶ END (if validation fails)
```

### Context & Memory

The system maintains context between agent calls using LangGraph's `StateGraph`:

- **AgentState** (TypedDict) holds all shared data
- Each node receives the full state and returns updated state
- Context flows: `raw_data` → `validation_result` → `analysis_results`
- If validation fails, the workflow short-circuits to END

---

## Features

- Real-time stock price lookup (NSE/BSE via IndianAPI)
- Web-based fallback for global stocks
- AI-generated market insights
- Risk and opportunity analysis
- Clean, desktop-optimized UI

> **⚠️ Note:** Stock prices and real-time stock information are sourced from **IndianAPI** ([indianapi.in](https://indianapi.in)). The accuracy and availability of stock data is entirely dependent on this third-party API. For best results with Indian stocks (NSE/BSE), ensure you have a valid IndianAPI key configured.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| AI/LLM | Groq (Mixtral 8x7b, Llama 3.3 70b) |
| Orchestration | LangGraph StateGraph |
| Data Sources | Wikipedia API, DuckDuckGo, IndianAPI |

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/Siddhartha23i/Soulpage-genai-assignment1-Siddhartha.git
cd Soulpage-genai-assignment1-Siddhartha
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

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
INDIAN_API_KEY=your_indian_api_key_here  # Optional
```

Get API keys:
- **Groq**: [console.groq.com](https://console.groq.com)
- **IndianAPI**: [indianapi.in](https://indianapi.in) (optional)

### 5. Run the app

```bash
streamlit run ui/app.py
```

---

## Reproducibility

For step-by-step execution, see the **[demo.ipynb](demo.ipynb)** notebook.

---

## Project Structure

```
stockpulse-ai/
├── agents/
│   ├── data_collector.py   # Web scraping & API data collection
│   └── analyst.py          # LLM-powered analysis
├── graph/
│   └── orchestrator.py     # LangGraph workflow + state management
├── ui/
│   └── app.py              # Streamlit frontend
├── utils/
│   ├── config.py           # Settings management
│   └── llm.py              # Groq LLM initialization
├── demo.ipynb              # Reproducibility notebook
├── requirements.txt
└── README.md
```

---

## Deployment (Streamlit Cloud)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Set main file: `ui/app.py`
4. Add secrets: `GROQ_API_KEY`, `INDIAN_API_KEY`

---

## License

MIT License

---

Built with LangGraph + Groq
