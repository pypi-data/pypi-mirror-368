from pydantic import SecretStr, Field
import logging
from anchorbrowser import Anchorbrowser
import getpass
import time
import os

class AnchorClient:
    """Singleton class to ensure only one Anchor Browser client instance exists"""
    _instance = None
    _client = None
    _api_key = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self):
        """Initialize API key and client only once"""
        if self._api_key is None:
            print(f"Checking for ANCHORBROWSER_API_KEY env var...")
            env_api_key = os.getenv('ANCHORBROWSER_API_KEY')
            
            if env_api_key:
                # Use environment variable directly
                self._api_key = SecretStr(env_api_key)
                print(f"Using API key from environment variable")
            else:
                # Fall back to prompt
                self._api_key = SecretStr(getpass.getpass("Enter API key for Anchor Browser: "))
                print(f"Using API key from prompt")
            
            self._client = Anchorbrowser(api_key=self._api_key.get_secret_value())
            print(f"Created new API key and client instances")
        return self._api_key, self._client

# Base configuration for all tools
class AnchorBaseTool:
    api_key: SecretStr = Field(default=SecretStr(""), description="API key for Anchor Browser")
    logger: logging.Logger = Field(default=logging.getLogger(__name__), description="Logger instance")
    client: Anchorbrowser | None = Field(default=None, description="Anchor Browser client instance")
    client_function_name: str = None  # Will be overridden by subclasses

    def __init__(self, api_key: str | SecretStr | None = None):
        super().__init__()
        print(f"Creating {self.__class__.__name__}")
        self.logger = logging.getLogger(__name__)
        # Get shared API key and client instances
        self.api_key, self.client = AnchorClient().initialize()
        print("Using shared API key and client instances")

    def _run(self, **kwargs) -> str:
        """Generic run method that calls the appropriate client function"""
        start_time = time.time()
        
        # Filter out None values
        request_body = {k: v for k, v in kwargs.items() if v is not None}

        if self.client_function_name == "perform_web_task" and "url" not in request_body:
            request_body["url"] = "https://example.com"
            request_body["prompt"] += ". Ignore the starting url."

        # Get the function name from the class attribute
        function_name = self.client_function_name
        if not function_name:
            raise ValueError(f"client_function_name not set for {self.__class__.__name__}")
        
        # Create a new session
        session = self.client.sessions.create()
        live_view_url = session.data.live_view_url
        self.logger.info(f"Session Information:xccv {session.data}")
        print(f"Live view URL: {live_view_url}")
        request_body["session_id"] = session.data.id

        # Get the function from the client
        client_func = getattr(self.client.tools, function_name)  
        self.logger.info(f"Calling {function_name} for: {kwargs.get('url', '')}")
        result = client_func(**request_body)
        
        execution_time = time.time() - start_time
        self.logger.info(f"{function_name} completed in {execution_time:.2f}s")
        if function_name == "screenshot_webpage":
            return result.text()
        elif function_name == "perform_web_task":
            return result.data
        else:
            return result
