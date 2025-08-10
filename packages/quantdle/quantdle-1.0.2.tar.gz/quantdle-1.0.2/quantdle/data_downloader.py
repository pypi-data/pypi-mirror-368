"""
Quantdle Data Downloader

Handles complex data download operations including:
- Date range chunking for large requests
- Parallel file downloads
- ZIP file extraction and processing
- DataFrame creation and formatting
"""

import io
import json
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Union, Literal, TYPE_CHECKING, Optional
import warnings

import pandas as pd
import requests
from tqdm import tqdm

if TYPE_CHECKING:
    import polars as pl


class DataDownloader:
    """
    Handles all data download operations with optimizations for large datasets.
    """
    
    def __init__(self, session: requests.Session, host: str):
        """
        Initialize the data downloader.
        
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
            endpoint: API endpoint (e.g., '/data/EURUSD')
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

            # Handle common API errors gracefully for a better user experience
            if response.status_code == 403:
                # Extract symbol if this is a data endpoint like '/data/SYMBOL'
                symbol = None
                try:
                    if endpoint.startswith('/data/'):
                        symbol = endpoint.split('/')[-1]
                except Exception:
                    symbol = None

                nice_symbol = f" '{symbol}'" if symbol else ""
                warnings.warn(
                    (
                        f"Cannot download data for symbol{nice_symbol} because it is not included in your current plan. "
                        "This symbol is available on a higher tier. "
                        "Use client.get_available_symbols() to list the symbols you can access, or upgrade your plan to include this symbol."
                    )
                )
                # Return an empty set of URLs so the caller can complete gracefully
                return {"presigned_urls": []}

            if response.status_code == 404:
                # Not found (e.g., unknown symbol)
                warnings.warn(
                    "Requested resource was not found. Please double-check the symbol and timeframe, "
                    "or call client.get_available_symbols() to see what you can access."
                )
                return {"presigned_urls": []}

            if response.status_code == 401:
                raise Exception(
                    "Authentication failed (401). Please verify your API key and API key ID."
                )

            # Raise for other non-success codes
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def _download_data(
        self,
        symbol: str,
        timeframe: Literal['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1'],
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        output_format: Literal['pandas', 'polars'] = 'pandas',
        max_workers: int = 4,
        show_progress: bool = True,
        chunk_size_years: int = 5
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
            >>> df = downloader.download_data("EURUSD", "H1", "2023-01-01", "2023-12-31")
            >>> print(df.head())
                           timestamp     open     high      low    close  volume
            0   2023-01-01 22:00:00  1.07023  1.07037  1.07018  1.07032     123
            1   2023-01-01 23:00:00  1.07032  1.07045  1.07028  1.07041      89
        """
        # Convert dates to datetime objects
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
        # Check if polars is requested but not installed
        if output_format == 'polars':
            try:
                import polars as pl
            except ImportError:
                raise ImportError(
                    "Polars is not installed. Install it with: pip install quantdle[polars]"
                )
        
        # Calculate date range in years
        years_diff = (end_date - start_date).days / 365.25
        
        all_data = []
        
        if years_diff > chunk_size_years:
            # Split into chunks
            current_start = start_date
            chunks = []
            
            while current_start < end_date:
                chunk_end = min(
                    current_start + timedelta(days=int(chunk_size_years * 365.25)),
                    end_date
                )
                chunks.append((current_start, chunk_end))
                current_start = chunk_end + timedelta(days=1)
            
            if show_progress:
                print(f"Large date range detected. Downloading in {len(chunks)} chunks...")
            
            for i, (chunk_start, chunk_end) in enumerate(chunks):
                if show_progress:
                    print(f"\nChunk {i+1}/{len(chunks)}: {chunk_start.date()} to {chunk_end.date()}")
                
                chunk_data = self.__download_chunk(
                    symbol, timeframe, chunk_start, chunk_end, 
                    max_workers, show_progress
                )
                all_data.extend(chunk_data)
        else:
            # Download all at once
            all_data = self.__download_chunk(
                symbol, timeframe, start_date, end_date,
                max_workers, show_progress
            )
        
        # Combine all data into a DataFrame
        if not all_data:
            warnings.warn("No data was downloaded. Check your date range and symbol availability.")
            if output_format == 'pandas':
                return pd.DataFrame(columns=['datetime', 'open', 'high', 'low', 'close', 'volume', 'spread', 'spreadmax', 'spreadopen'])
            else:
                import polars as pl
                return pl.DataFrame(schema={
                    'datetime': pl.Datetime,
                    'open': pl.Float64,
                    'high': pl.Float64,
                    'low': pl.Float64,
                    'close': pl.Float64,
                    'volume': pl.Int64,
                    'spread': pl.Int32,
                    'spreadmax': pl.Int32,
                    'spreadopen': pl.Int32
                })
        
        # Create DataFrame
        df = pd.DataFrame(all_data)
        df['datetime'] = df['date'] + ' ' + df['time']
        df['datetime'] = pd.to_datetime(df['datetime'])

        # Set datetime as index
        df = df.set_index('datetime')

        # Drop date and time columns
        df = df.drop(columns=['date', 'time'])

        # Sort the dataframe by index
        df = df.sort_index()
        
        if output_format == 'polars':
            import polars as pl
            return pl.from_pandas(df)
        
        return df
    
    def __download_chunk(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
        max_workers: int,
        show_progress: bool
    ) -> list[dict]:
        """
        Download a single chunk of data.
        
        Args:
            symbol: Symbol code
            timeframe: Timeframe code
            start_date: Start date for this chunk
            end_date: End date for this chunk
            max_workers: Maximum number of parallel downloads
            show_progress: Whether to show progress bars
            
        Returns:
            List of raw OHLCV data dictionaries
        """
        # Get presigned URLs using simple requests
        params = {
            'timeframe': timeframe,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
        
        response = self.__make_request('GET', f'/data/{symbol}', params)
        urls = response['presigned_urls']
        
        if not urls:
            return []
        
        # Download files in parallel
        all_data = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks
            future_to_url = {
                executor.submit(self.__download_and_extract_zip, url): url 
                for url in urls
            }
            
            # Process completed downloads
            if show_progress:
                futures = tqdm(
                    as_completed(future_to_url),
                    total=len(urls),
                    desc="Downloading Quantdle Data",
                    unit=" Quantdles"
                )
            else:
                futures = as_completed(future_to_url)
            
            for future in futures:
                try:
                    data = future.result()
                    all_data.extend(data)
                except Exception as e:
                    url = future_to_url[future]
                    warnings.warn(f"Failed to download from {url}: {str(e)}")
        
        return all_data
    
    def __download_and_extract_zip(self, url: str) -> list[dict]:
        """
        Download a ZIP file and extract JSON data.
        
        Args:
            url: Presigned S3 URL for the ZIP file
            
        Returns:
            List of OHLCV data dictionaries from the ZIP
            
        Raises:
            Exception: If download or extraction fails
        """
        try:
            # Download the ZIP file directly
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Extract and parse JSON from ZIP
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                # Find the JSON file in the ZIP
                json_files = [f for f in zf.namelist() if f.endswith('.json')]
                
                if not json_files:
                    warnings.warn("No JSON files found in ZIP from URL")
                    return []
                
                all_data = []
                for json_file in json_files:
                    with zf.open(json_file) as f:
                        data = json.load(f)
                        # Assuming the JSON contains an array of OHLCV data
                        if isinstance(data, list):
                            all_data.extend(data)
                        elif isinstance(data, dict) and 'data' in data:
                            all_data.extend(data['data'])
                        else:
                            warnings.warn(f"Unexpected JSON structure in {json_file}")
                
                return all_data
                
        except Exception as e:
            raise Exception(f"Error downloading/extracting data: {str(e)}") 