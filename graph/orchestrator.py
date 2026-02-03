"""LangGraph orchestrator for multi-agent workflow with strict validation."""

import logging
from typing import TypedDict, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from agents import DataCollectorAgent, AnalystAgent
from utils import get_groq_llm

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Shared state across agent executions."""
    company_name: str
    raw_data: Dict[str, Any]
    analysis_results: Dict[str, str]
    error: Optional[str]
    validation_passed: bool


class Orchestrator:
    """LangGraph orchestrator with strict data validation."""
    
    def __init__(self, data_collector: DataCollectorAgent, analyst: AnalystAgent):
        """
        Initialize orchestrator with agent instances.
        
        Args:
            data_collector: Data Collector Agent instance
            analyst: Analyst Agent instance
        """
        self.data_collector = data_collector
        self.analyst = analyst
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build LangGraph StateGraph with validation step.
        
        Returns:
            Compiled StateGraph workflow
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes for each step
        workflow.add_node("collect_data", self._collect_data_node)
        workflow.add_node("validate_data", self._validate_data_node)
        workflow.add_node("analyze_data", self._analyze_data_node)
        
        # Define execution flow with conditional edge
        workflow.set_entry_point("collect_data")
        workflow.add_edge("collect_data", "validate_data")
        
        # Conditional: only analyze if validation passes
        workflow.add_conditional_edges(
            "validate_data",
            self._should_analyze,
            {
                True: "analyze_data",
                False: END
            }
        )
        workflow.add_edge("analyze_data", END)
        
        return workflow.compile()
    
    def _collect_data_node(self, state: AgentState) -> AgentState:
        """
        Node function for data collection.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with collected data
        """
        try:
            logger.info(f"🔍 Step 1: Collecting REAL data for: {state['company_name']}")
            
            raw_data = self.data_collector.collect_data(state["company_name"])
            
            state["raw_data"] = raw_data
            logger.info(f"✅ Data collection completed. Quality: {raw_data.get('data_quality', 'unknown')}")
            
        except Exception as e:
            logger.error(f"❌ Data collection failed: {e}")
            state["error"] = f"Data collection error: {str(e)}"
            state["raw_data"] = {"data_quality": "error"}
            state["validation_passed"] = False
        
        return state
    
    def _validate_data_node(self, state: AgentState) -> AgentState:
        """
        Node function for data validation.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with validation result
        """
        try:
            logger.info("🔍 Step 2: Validating collected data...")
            
            raw_data = state.get("raw_data", {})
            data_quality = raw_data.get("data_quality", "unknown")
            
            # Check if we have any usable data
            has_company_info = bool(raw_data.get("company_info"))
            has_news = bool(raw_data.get("news"))
            has_sources = bool(raw_data.get("sources"))
            
            # Validation passes if we have at least some data
            validation_passed = (
                data_quality != "error" and
                (has_company_info or has_news or has_sources)
            )
            
            state["validation_passed"] = validation_passed
            
            if validation_passed:
                logger.info(f"✅ Validation PASSED. Proceeding to analysis.")
            else:
                logger.warning(f"⚠️ Validation FAILED. Insufficient data - skipping analysis.")
                # Create minimal response
                state["analysis_results"] = {
                    "executive_summary": f"⚠️ **Insufficient Data**\n\nNo reliable information found for {state['company_name']}.",
                    "market_insights": "**Data Not Available**",
                    "risks_opportunities": "**Data Not Available**",
                    "data_sources": "- No sources found",
                    "data_quality": data_quality
                }
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            state["error"] = f"Validation error: {str(e)}"
            state["validation_passed"] = False
        
        return state
    
    def _should_analyze(self, state: AgentState) -> bool:
        """
        Determine if analysis should proceed based on validation.
        
        Args:
            state: Current agent state
            
        Returns:
            True if analysis should proceed, False otherwise
        """
        return state.get("validation_passed", False)
    
    def _analyze_data_node(self, state: AgentState) -> AgentState:
        """
        Node function for data analysis.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with analysis results
        """
        try:
            logger.info("🔍 Step 3: Starting FACT-BASED analysis...")
            
            if not state.get("raw_data"):
                raise ValueError("No data available for analysis")
            
            analysis_results = self.analyst.analyze(state["raw_data"])
            
            state["analysis_results"] = analysis_results
            logger.info("✅ Analysis completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            state["error"] = f"Analysis error: {str(e)}"
            state["analysis_results"] = {
                "executive_summary": "Analysis unavailable due to error",
                "market_insights": "Analysis unavailable",
                "risks_opportunities": "Analysis unavailable",
                "data_sources": "- Error occurred",
                "data_quality": "error"
            }
        
        return state
    
    def run(self, company_name: str) -> Dict[str, Any]:
        """
        Execute the multi-agent workflow with validation.
        
        Args:
            company_name: Name of company to analyze
            
        Returns:
            Final state containing analysis results
        """
        logger.info(f"🚀 Starting FACT-BASED workflow for: {company_name}")
        logger.info("="*60)
        
        # Initialize state
        initial_state: AgentState = {
            "company_name": company_name,
            "raw_data": {},
            "analysis_results": {},
            "error": None,
            "validation_passed": False
        }
        
        # Execute workflow
        final_state = self.graph.invoke(initial_state)
        
        logger.info("="*60)
        logger.info(f"✅ Workflow completed for: {company_name}")
        
        return final_state
