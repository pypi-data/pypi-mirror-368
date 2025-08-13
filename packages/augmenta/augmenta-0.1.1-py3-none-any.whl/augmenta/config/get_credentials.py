"""Manages API credentials and authentication for various services."""

import os
from typing import Dict, Set, Any
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import logging

class CredentialsManager:
    """Manages API credentials and keys for various services."""
    
    _env_loaded = False  # Class variable to track if environment has been loaded
    
    def __init__(self, env_file: str = None) -> None:
        """Initialize the credentials manager.
        
        Args:
            env_file: Optional path to a specific .env file. If not provided,
                     will search for .env files automatically.
        """
        # Only load environment if it hasn't been loaded yet or if a specific file is provided
        if not self._env_loaded or env_file:
            self._load_environment(env_file)
            if not env_file:  # Only mark as loaded if using default search
                CredentialsManager._env_loaded = True
    
    def _load_environment(self, env_file: str = None) -> None:
        """Load environment variables from .env file.
        
        Args:
            env_file: Optional path to a specific .env file
        """
        if env_file:
            # Use explicitly provided .env file
            env_path = Path(env_file).resolve()
            if env_path.exists():
                load_dotenv(env_path)
                logging.info(f"Loaded .env from specified path: {env_path}")
                return
            else:
                logging.warning(f"Specified .env file not found: {env_path}")
        
        # Use find_dotenv first - it searches upwards from current directory
        # This is the most reliable method for finding .env files
        dotenv_path = find_dotenv()
        if dotenv_path:
            load_dotenv(dotenv_path)
            logging.info(f"Loaded .env from: {dotenv_path}")
            return
        
        # Fallback search strategy if find_dotenv doesn't find anything
        search_paths = [
            # 1. Current working directory (where the command is run)
            Path.cwd() / '.env',
            # 2. User's home directory (common location)
            Path.home() / '.env',
        ]
        
        for env_path in search_paths:
            if env_path.exists():
                load_dotenv(env_path)
                logging.info(f"Loaded .env from fallback search: {env_path}")
                return
        
        # If no .env file found, that's okay - environment variables might be set directly
        logging.info("No .env file found. Using system environment variables only.")

    def get_credentials(self, required_keys: Set[str]) -> Dict[str, str]:
        """Get and validate credentials from environment or config.
        
        Args:
            required_keys: Set of required credential key names
            
        Returns:
            Dictionary of credential key-value pairs
            
        Raises:
            ValueError: If any required credentials are missing
        """
        credentials = {
            key: os.getenv(key)
            for key in required_keys
        }
        
        missing_keys = [key for key, value in credentials.items() if not value]
        
        if missing_keys:
            raise ValueError(
                f"Missing required API keys: {', '.join(missing_keys)}. "
                "Please create a .env file in your project root with the required keys. "
                "For example: BRAVE_API_KEY=your_key, OPENAI_API_KEY=your_key, etc."
            )
            
        return {k: v for k, v in credentials.items() if v}
        
    def get_required_keys(self, config_data: Dict[str, Any]) -> Set[str]:
        """Determine which API keys are required based on the configuration.
        
        Args:
            config_data: Configuration dictionary
            
        Returns:
            Set of required API key names
        """
        required_keys = set()
        
        # Check model provider
        model_provider = config_data.get("model", {}).get("provider", "").lower()
        if model_provider == "openai":
            required_keys.add("OPENAI_API_KEY")
        elif model_provider == "anthropic":
            required_keys.add("ANTHROPIC_API_KEY")
            
        # Check search engine
        search_engine = config_data.get("search", {}).get("engine", "").lower()
        if search_engine == "brave":
            required_keys.add("BRAVE_API_KEY")
        elif search_engine == "brightdata":
            required_keys.add("BRIGHTDATA_API_KEY")
            required_keys.add("BRIGHTDATA_ZONE")
        elif search_engine == "google":
            required_keys.add("GOOGLE_API_KEY")
            required_keys.add("GOOGLE_SEARCH_ENGINE_ID")
        elif search_engine == "oxylabs":
            required_keys.add("OXYLABS_USERNAME")
            required_keys.add("OXYLABS_PASSWORD")
            
        return required_keys
