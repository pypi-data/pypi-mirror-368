"""
Quantdle Symbols API

Handles symbol-related API operations like listing available symbols
and getting symbol information.
"""

from typing import Optional
import requests


class SymbolsAPI:
    """
    Handles all symbol-related API operations.
    """
    
    def __init__(self, session: requests.Session, host: str):
        """
        Initialize the symbols API.
        
        Args:
            session: Configured requests session with authentication headers
            host: API host URL
        """
        self.__session = session
        self.__host = host
    
    def __make_request(self, method: str, endpoint: str, params: Optional[dict] = None) -> dict:
        """
        Make a request to the Quantdle API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/symbols')
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            Exception: If the request fails
        """
        url = f"{self.__host}{endpoint}"
        
        try:
            response = self.__session.request(
                method=method,
                url=url,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def get_available_symbols(self) -> list[str]:
        """
        Get the list of symbols available for your account.
        
        Returns:
            List of symbol codes (e.g., ['EURUSD', 'GBPUSD', 'XAUUSD'])
        """
        response = self.__make_request('GET', '/symbols')
        return response['symbols']
    
    def get_symbol_info(self, symbol: str) -> dict:
        """
        Get availability information for a specific symbol.
        
        Args:
            symbol: Symbol code (e.g., 'EURUSD')
            
        Returns:
            Dictionary with symbol information including available date range (dates as strings)
        """
        response = self.__make_request('GET', f'/symbols/{symbol}/range')
        return response 