import http.client
import json
import logging
from typing import Optional, Dict, Any 

# Setting up logging
logger = logging.getLogger(__name__)

class OllamaError(Exception):
    """Custom exception to Ollama Client errors"""
    pass

class BaseClient:
    """Base class allows for stub/mock clients during testing[task 6]"""
    def generate(self, _prompt:str, _system:Optional[str]=None, _format_json:bool = True):
        raise NotImplementedError

class AiClient(BaseClient):
    """Client Wrapper around the Ollama Api
      Uses python's built-in http.client so no extra dependencies are required.
    """
    def __init__(self, host:str = "localhost", port:int = 11434, model:str = "llama3", timeout:float = 30.0):
        self.host = host
        self.port = port
        self.model = model
        self.timeout = timeout

    def check_connection(self) -> bool:
        """Task 5: Handle Ollama Unavailability at startup by pinging the 
          tags/health endpoints
        """
        try:
            conn = http.client.HTTPConnection(self.host, self.port, timeout=2)
            conn.request("GET", "/api/tags")
            res = conn.getresponse()
            return res.status == 200
        except Exception:
            return False
        
    def generate(self, prompt: str, system:Optional[str]=None, format_json: bool = True):
        """Task 1: Sends a generation request to the local Ollama instance.
         Args:
         prompt: The serialized game state
         system: Optional system prompt for guidance
         format_json: forces Ollama to return valid JSON

         returns:
          The raw text response string from Ollam.
        """
        # construct the payload
        payload:Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }    

        if system:
            payload["system"] = system
        if format_json:
            payload["format"] = "json"

        try:
            conn = http.client.HTTPConnection(self.host, self.port, timeout = self.timeout) 
            headers = {'Content-Type':'application/json'}
            conn.request('POST', '/api/generate', body=json.dumps(payload), headers=headers)
            res = conn.getresponse()
            data = json.loads(res.read().decode())

            return data.get("response", "")
        except (OSError, json.JSONDecodeError) as e:
            raise OllamaError(f"Network error communicating with Ollama: {e}")

           
class StubAiClient(BaseClient):
    """Task 6 stub Ai Client for unit testing without running local Ollam server.
       Ths allows us to test the game logic [3-strike rule]perfectly
    """
    def __init__(self, canned_responses:Optional[list[str]]=None):
        self.canned_responses = canned_responses or [{"action": "move", "direction": "north"}]
        self.call_count = 0

    def generate(self, _prompt: str, _system:Optional[str]=None, format_json: bool = True)-> str:
        """Return pre-scripted responses looping if needed"""
        response = self.canned_responses[self.call_count % len(self.canned_responses)]
        self.call_count += 1
        return response
