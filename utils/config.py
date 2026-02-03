"""Configuration management for the Company Intelligence AI System."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    groq_api_key: str
    # Per-agent model assignment as per requirements:
    # Research Agent → mixtral-8x7b-32768
    # Analyst Agent → llama-3.3-70b-versatile
    research_model: str = "mixtral-8x7b-32768"
    analyst_model: str = "llama-3.3-70b-versatile"
    fallback_model: str = "mixtral-8x7b-32768"
    temperature: float = 0.7
    
    # Indian API for stock data (optional)
    indian_api_key: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def get_settings() -> Settings:
    """
    Get application settings.
    
    Returns:
        Settings instance with configuration values
        
    Raises:
        ValueError: If required environment variables are missing
    """
    try:
        return Settings()
    except Exception as e:
        raise ValueError(
            f"Failed to load settings. Ensure GROQ_API_KEY is set in environment or .env file. Error: {e}"
        )
