"""Groq LLM client initialization and configuration."""

import os
import logging
from typing import Optional
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)


def get_groq_llm(
    model: str = "llama-3.1-70b-versatile",
    temperature: float = 0.7,
    fallback: bool = True
) -> ChatGroq:
    """
    Initialize Groq LLM client.
    
    Args:
        model: Model name (default: llama-3.1-70b-versatile)
        temperature: Sampling temperature (0.0 to 1.0)
        fallback: Whether to use fallback model on failure
        
    Returns:
        Configured ChatGroq instance
        
    Raises:
        ValueError: If GROQ_API_KEY not found or temperature invalid
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found in environment variables. "
            "Please set it in your .env file or environment."
        )
    
    if not 0.0 <= temperature <= 1.0:
        raise ValueError(f"Temperature must be between 0.0 and 1.0, got {temperature}")
    
    try:
        logger.info(f"🤖 Initializing Groq LLM with model: {model}")
        return ChatGroq(
            api_key=api_key,
            model=model,
            temperature=temperature
        )
    except Exception as e:
        if fallback:
            return get_fallback_llm(temperature)
        raise RuntimeError(f"Failed to initialize Groq LLM: {e}")


def get_research_llm(temperature: float = 0.7) -> ChatGroq:
    """
    Get Groq LLM for Research/Data Collection Agent.
    
    Uses mixtral-8x7b-32768 as per requirements.
    
    Args:
        temperature: Sampling temperature (0.0 to 1.0)
        
    Returns:
        Configured ChatGroq instance for research tasks
    """
    logger.info("🔍 Initializing Research Agent LLM: mixtral-8x7b-32768")
    return get_groq_llm(model="mixtral-8x7b-32768", temperature=temperature)


def get_analyst_llm(temperature: float = 0.7) -> ChatGroq:
    """
    Get Groq LLM for Analyst Agent.
    
    Uses llama-3.1-70b-versatile as per requirements.
    
    Args:
        temperature: Sampling temperature (0.0 to 1.0)
        
    Returns:
        Configured ChatGroq instance for analysis tasks
    """
    logger.info("📊 Initializing Analyst Agent LLM: llama-3.3-70b-versatile")
    return get_groq_llm(model="llama-3.3-70b-versatile", temperature=temperature)


def get_fallback_llm(temperature: float = 0.7) -> ChatGroq:
    """
    Get fallback Groq LLM (mixtral-8x7b-32768).
    
    Args:
        temperature: Sampling temperature (0.0 to 1.0)
        
    Returns:
        Configured ChatGroq instance with fallback model
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables.")
    
    logger.info("⚠️ Using fallback LLM: mixtral-8x7b-32768")
    return ChatGroq(
        api_key=api_key,
        model="mixtral-8x7b-32768",
        temperature=temperature
    )

