# import requests

# class Completions:
#     def __init__(self, base_url, headers):
#         self.url = f"{base_url}/v1/chat/completions"
#         self.headers = headers

#     def create(self, *, messages, model="shakti-01-chat", stream=False, temperature=0.7, top_p=0.95, max_tokens=1024):
#         payload = {
#             "model": model,
#             "messages": messages,
#             "stream": stream,
#             "temperature": temperature,
#             "top_p": top_p,
#             "max_tokens": max_tokens,
#         }

#         if stream:
#             return self._stream(payload)
#         else:
#             resp = requests.post(self.url, json=payload, headers=self.headers)
#             resp.raise_for_status()
#             return resp.json()

#     def _stream(self, payload):
#         with requests.post(self.url, json=payload, headers=self.headers, stream=True) as resp:
#             resp.raise_for_status()
#             for line in resp.iter_lines():
#                 if line:
#                     decoded = line.decode("utf-8")
#                     if decoded.startswith("data: "):
#                         data = decoded[6:]
#                         if data == "[DONE]":
#                             break
#                         yield data


import requests
import json
from typing import Iterator, Dict, Any, List, Optional

class Completions:
    def __init__(self, base_url: str, headers: Dict[str, str], timeout: int = 30):
        self.url = f"{base_url}/v1/chat/completions"
        self.headers = headers
        self.timeout = timeout

    def create(
        self, 
        *, 
        messages: List[Dict[str, str]], 
        model: str = "shakti-01-chat", 
        stream: bool = False, 
        temperature: float = 0.7, 
        top_p: float = 0.95, 
        max_tokens: int = 1024,
        timeout: Optional[int] = None
    ) -> Dict[str, Any] | Iterator[str]:
        """
        Create a chat completion.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use for completion
            stream: Whether to stream the response
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens to generate
            timeout: Override default timeout for this request
            
        Returns:
            Dict for non-streaming, Iterator[str] for streaming
            
        Raises:
            requests.exceptions.HTTPError: For HTTP errors
            requests.exceptions.Timeout: For timeout errors
            requests.exceptions.RequestException: For other request errors
        """
        # Validate inputs
        if not messages:
            raise ValueError("Messages cannot be empty")
        
        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")
            
        if not 0 <= top_p <= 1:
            raise ValueError("top_p must be between 0 and 1")
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
        }
        
        request_timeout = timeout or self.timeout

        if stream:
            return self._stream(payload, request_timeout)
        else:
            return self._non_stream(payload, request_timeout)
    
    def _non_stream(self, payload: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """Handle non-streaming requests with proper error handling."""
        try:
            resp = requests.post(
                self.url, 
                json=payload, 
                headers=self.headers,
                timeout=timeout
            )
            resp.raise_for_status()
            return resp.json()
            
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request timed out after {timeout} seconds")
        except requests.exceptions.HTTPError as e:
            # Try to get error details from response
            try:
                error_detail = e.response.json()
                raise Exception(f"API Error: {error_detail}")
            except:
                raise Exception(f"HTTP {e.response.status_code}: {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def _stream(self, payload: Dict[str, Any], timeout: int) -> Iterator[str]:
        """
        Handle streaming requests with proper error handling.
        
        Yields:
            JSON strings of each chunk
        """
        try:
            with requests.post(
                self.url, 
                json=payload, 
                headers=self.headers, 
                stream=True,
                timeout=timeout
            ) as resp:
                resp.raise_for_status()
                
                for line in resp.iter_lines(decode_unicode=True):
                    if line:
                        # Handle Server-Sent Events format
                        if line.startswith("data: "):
                            data = line[6:]
                            
                            # Check for stream end marker
                            if data == "[DONE]":
                                break
                            
                            # Validate JSON before yielding
                            try:
                                json.loads(data)  # Validate it's proper JSON
                                yield data
                            except json.JSONDecodeError:
                                # Log or handle malformed chunks
                                continue
                                
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Stream request timed out after {timeout} seconds")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Stream HTTP {e.response.status_code}: {e.response.reason}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Stream request failed: {str(e)}")