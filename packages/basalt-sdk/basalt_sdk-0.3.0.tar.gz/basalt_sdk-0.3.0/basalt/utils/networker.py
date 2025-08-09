import requests
import aiohttp
from typing import Any, Dict, Optional, Tuple

from .errors import BadRequest, FetchError, Forbidden, NetworkBaseError, NotFound, Unauthorized
from .protocols import INetworker, ILogger

class Networker(INetworker):
    """
    Networker class that implements the INetworker protocol.
    Provides a method to fetch data from a given URL using HTTP methods.
    """
    def __init__(self):
        pass

    def fetch(
            self,
            url: str,
            method: str,
            body = None,
            headers = None,
            params = None
        ) -> Tuple[Optional[FetchError], Optional[Dict[str, Any]]]:
        """
        Fetch data from a given URL using the specified HTTP method. This method should never throw.

        Args:
            url (str): The URL to fetch data from.
            method (str): The HTTP method to use (e.g., 'GET', 'POST').
            body (Optional[Any]): The request payload to send (default is None).
            headers (Optional[Dict[str, str]]): The request headers to send (default is None).
            params (Optional[Dict[str, str]]): The query parameters to send (default is None).

        Returns:
            A result tuple (err, json_response), possible responses:
            - (None, json_response)
            - (FetchError, None)
        """
        try:
            response = requests.request(
                method,
                url,
                params=params,
                json=body,
                headers=headers
            )

            json_response = response.json()

            if response.status_code == 400:
                return BadRequest(json_response.get('error', json_response.get('errors', 'Bad Request'))), None

            if response.status_code == 401:
                return Unauthorized(json_response.get('error', 'Unauthorized')), None

            if response.status_code == 403:
                return Forbidden(json_response.get('error', 'Forbidden')), None

            if response.status_code == 404:
                return NotFound(json_response.get('error', 'Not Found')), None

            response.raise_for_status()

            return None, json_response

        except Exception as e:
            return NetworkBaseError(str(e)), None
            
    async def async_fetch(
            self,
            url: str,
            method: str,
            body = None,
            headers = None,
            params = None
        ) -> Tuple[Optional[FetchError], Optional[Dict[str, Any]]]:
        """
        Asynchronously fetch data from a given URL using the specified HTTP method.
        
        Args:
            url (str): The URL to fetch data from.
            method (str): The HTTP method to use (e.g., 'GET', 'POST').
            body (Optional[Any]): The request payload to send (default is None).
            headers (Optional[Dict[str, str]]): The request headers to send (default is None).
            params (Optional[Dict[str, str]]): The query parameters to send (default is None).
        
        Returns:
            A result tuple (err, json_response), possible responses:
            - (None, json_response)
            - (FetchError, None)
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    params=params,
                    json=body,
                    headers=headers
                ) as response:
                    json_response = await response.json()
                    
                    if response.status == 400:
                        return BadRequest(json_response.get('error', json_response.get('errors', 'Bad Request'))), None
                    
                    if response.status == 401:
                        return Unauthorized(json_response.get('error', 'Unauthorized')), None
                    
                    if response.status == 403:
                        return Forbidden(json_response.get('error', 'Forbidden')), None
                    
                    if response.status == 404:
                        return NotFound(json_response.get('error', 'Not Found')), None
                    
                    response.raise_for_status()
                    
                    return None, json_response
                    
        except Exception as e:
            return NetworkBaseError(str(e)), None
