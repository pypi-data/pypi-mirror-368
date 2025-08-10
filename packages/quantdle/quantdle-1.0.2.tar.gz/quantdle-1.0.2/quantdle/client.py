"""
Quantdle Python Client

A user-friendly Python client for downloading financial market data from Quantdle.
Automatically handles data downloading, extraction, and conversion to pandas/polars DataFrames.
"""

from datetime import datetime
from typing import Union, Literal, TYPE_CHECKING, Optional, Any, Type

import pandas as pd
import requests

from .symbols import SymbolsAPI
from .data_downloader import DataDownloader

if TYPE_CHECKING:
    import polars as pl


class Client:
    """
    High-level client for downloading financial market data from Quantdle.
    
    This client simplifies the process of downloading historical market data by:
    - Automatically handling API authentication
    - Downloading data files in parallel for better performance
    - Extracting and combining data into a single DataFrame
    - Supporting both pandas and polars DataFrames
    - Automatically chunking large date ranges to avoid timeouts
    
    The client is organized into specialized modules:
    - SymbolsAPI: Handle symbol listing and information
    - DataDownloader: Handle complex data download operations
    
    Example:
        >>> import quantdle as qdl
        >>> client = qdl.Client(api_key="your-api-key", api_key_id="your-key-id")
        >>> df = client.download_data("EURUSD", "H1", "2023-01-01", "2023-12-31")
    """
    
    def __init__(self, api_key: str, api_key_id: str, host: str = "https://hist.quantdle.com"):
        """
        Initialize the Quantdle client.
        
        Args:
            api_key: Your Quantdle API key
            api_key_id: Your Quantdle API key ID
            host: API host URL (default: https://hist.quantdle.com)
        """
        self.api_key = api_key
        self.api_key_id = api_key_id
        self.__host = host.rstrip('/')  # Remove trailing slash
        
        # Create session for connection pooling and better performance
        self.__session = requests.Session()
        self.__session.headers.update({
            'x-api-key': api_key,
            'x-api-key-id': api_key_id,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Initialize specialized API modules
        self.__symbols_api = SymbolsAPI(self.__session, self.__host)
        self.__data_downloader = DataDownloader(self.__session, self.__host)
        
    def get_available_symbols(self) -> list[str]:
        """
        Get the list of symbols available for your account.
        
        Returns:
            List of symbol codes (e.g., ['EURUSD', 'GBPUSD', 'XAUUSD'])
        """
        return self.__symbols_api.get_available_symbols()
    
    def get_symbol_info(self, symbol: str) -> dict:
        """
        Get availability information for a specific symbol.
        
        Args:
            symbol: Symbol code (e.g., 'EURUSD')
            
        Returns:
            Dictionary with symbol information including available date range (dates as strings)
        """
        return self.__symbols_api.get_symbol_info(symbol)
    
    def download_data(
        self,
        symbol: str,
        timeframe: Literal['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1'],
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        output_format: Literal['pandas', 'polars'] = 'pandas',
        max_workers: int = 4,
        show_progress: bool = True
    ) -> Union[pd.DataFrame, "pl.DataFrame"]:
        """
        Download historical market data for a symbol and timeframe.
        
        This method handles all the complexity of downloading data:
        - Automatically chunks large date ranges to avoid API timeouts
        - Downloads multiple files in parallel for better performance
        - Extracts and combines all data into a single DataFrame
        - Shows progress bars for long downloads
        
        Args:
            symbol: Symbol code (e.g., 'EURUSD', 'XAUUSD')
            timeframe: Timeframe (one of: M1, M5, M15, M30, H1, H4, D1)
            start_date: Start date (inclusive) as string 'YYYY-MM-DD' or datetime
            end_date: End date (inclusive) as string 'YYYY-MM-DD' or datetime
            output_format: Output format ('pandas' or 'polars')
            max_workers: Maximum number of parallel downloads (default: 4)
            show_progress: Show progress bars during download (default: True)
            chunk_size_years: Years per chunk for large date ranges (default: 5)
            
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
            
        Example:
            >>> df = client.download_data("EURUSD", "H1", "2023-01-01", "2023-12-31")
            >>> print(df.head())
                           datetime     open     high      low    close  volume  spread  spreadmax  spreadopen
            0   2023-01-01 22:00:00  1.07023  1.07037  1.07018  1.07032     123      10         19         16
            1   2023-01-01 23:00:00  1.07032  1.07045  1.07028  1.07041      89      12         14         8
        """
        return self.__data_downloader._download_data(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            output_format=output_format,
            max_workers=max_workers,
            show_progress=show_progress
        )
    
    def __enter__(self) -> "Client":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> None:
        """Context manager exit."""
        if hasattr(self, '_Client__session'):
            self.__session.close()
    
    def __del__(self) -> None:
        """Clean up the session when the client is destroyed."""
        if hasattr(self, '_Client__session'):
            self.__session.close()
