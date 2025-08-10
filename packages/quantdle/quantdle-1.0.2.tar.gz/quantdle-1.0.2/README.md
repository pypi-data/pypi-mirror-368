# Quantdle Python Client

[![Tests](https://github.com/quantdle/quantdle-python/actions/workflows/test.yml/badge.svg)](https://github.com/quantdle/quantdle-python/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/quantdle/quantdle-python/branch/main/graph/badge.svg)](https://codecov.io/gh/quantdle/quantdle-python)
[![PyPI version](https://badge.fury.io/py/quantdle.svg)](https://badge.fury.io/py/quantdle)
[![Python versions](https://img.shields.io/pypi/pyversions/quantdle.svg)](https://pypi.org/project/quantdle/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A user-friendly Python client for downloading financial market data from [Quantdle](https://quantdle.com). This client simplifies the process of accessing historical market data by handling all the complexity of data downloading, extraction and processing.

## Features

- **Simple Data Access**: Download historical market data with just a few lines of code
- **High Performance**: Parallel downloads for faster data retrieval
- **Multiple Formats**: Support for both pandas and polars DataFrames
- **Smart Chunking**: Automatically handles large date ranges to avoid timeouts
- **Robust Error Handling**: Graceful handling of network issues and data errors
- **Zero Configuration**: Works out of the box with minimal setup

## Installation

Install the package using pip:

```bash
pip install quantdle
```

For polars support, install with the optional dependency:

```bash
pip install quantdle[polars]
```

## Quick Start

```python
import quantdle as qdl

# Initialize the client with your API credentials
client = qdl.Client(
    api_key="your-api-key",
    api_key_id="your-api-key-id"
)

# Download data for EURUSD
df = client.download_data(
    symbol="EURUSD",
    timeframe="H1",
    start_date="2023-01-01",
    end_date="2023-12-31"
)

print(df.head())
```

## Usage Examples

### Different Symbols and Timeframes

```python
import quantdle as qdl

# Initialize client once
client = qdl.Client(
    api_key="your-api-key",
    api_key_id="your-api-key-id"
)

# Download different symbols and timeframes
xau_data = client.download_data("XAUUSD", "D1", "2023-01-01", "2023-12-31")
eur_data = client.download_data("EURUSD", "H1", "2023-01-01", "2023-01-31")
```

### Using Polars DataFrames

```python
import quantdle as qdl

client = qdl.Client(
    api_key="your-api-key",
    api_key_id="your-api-key-id"
)

# Get data as a polars DataFrame
df = client.download_data(
    symbol="XAUUSD",
    timeframe="D1",
    start_date="2023-01-01",
    end_date="2023-12-31",
    output_format="polars"
)
```

### Listing Available Symbols

```python
import quantdle as qdl

client = qdl.Client(
    api_key="your-api-key",
    api_key_id="your-api-key-id"
)

# Get all available symbols for your account
symbols = client.get_available_symbols()
print(f"Available symbols: {symbols}")

# Get information about a specific symbol
info = client.get_symbol_info("EURUSD")
print(f"EURUSD available from {info['available_from']} to {info['available_to']}")
```

### Downloading Large Date Ranges

The client automatically handles large date ranges by splitting them into smaller chunks:

```python
import quantdle as qdl

client = qdl.Client(
    api_key="your-api-key",
    api_key_id="your-api-key-id"
)

# Download 10 years of data - will be automatically chunked
df = client.download_data(
    symbol="EURUSD",
    timeframe="H1",
    start_date="2014-01-01",
    end_date="2023-12-31",
    chunk_size_years=5  # Download in 5-year chunks
)
```

### Advanced Options

```python
import quantdle as qdl

client = qdl.Client(
    api_key="your-api-key",
    api_key_id="your-api-key-id"
)

# Customize download behavior
df = client.download_data(
    symbol="EURUSD",
    timeframe="M5",
    start_date="2023-01-01",
    end_date="2023-12-31",
    max_workers=8,           # Increase parallel downloads
    show_progress=True,      # Show progress bars
    chunk_size_years=3       # Smaller chunks for more frequent updates
)
```

## Available Timeframes

- `M1` - 1 minute
- `M5` - 5 minutes
- `M15` - 15 minutes
- `M30` - 30 minutes
- `H1` - 1 hour
- `H4` - 4 hours
- `D1` - 1 day

## DataFrame Structure

The returned DataFrame contains the following columns:

| Column | Type | Description |
|--------|------|-------------|
| timestamp | datetime | Candle timestamp |
| open | float | Opening price |
| high | float | Highest price |
| low | float | Lowest price |
| close | float | Closing price |
| volume | int | Trading volume |
| spread | int | Average spread of the bar |
| spreadmax | int | Maximum spread of the bar |
| spread_open | int | Opening spread of the bar |

## Error Handling

The client includes robust error handling:

```python
import quantdle as qdl

client = qdl.Client(
    api_key="your-api-key",
    api_key_id="your-api-key-id"
)

try:
    df = client.download_data(
        symbol="INVALID",
        timeframe="H1",
        start_date="2023-01-01",
        end_date="2023-12-31"
    )
except Exception as e:
    print(f"Error downloading data: {e}")
```

## Performance Tips

1. **Use parallel downloads**: The `max_workers` parameter controls the number of parallel downloads
2. **Choose appropriate chunk sizes**: Larger chunks mean fewer API calls but longer wait times
3. **Cache downloaded data**: Save DataFrames locally to avoid re-downloading
4. **Use polars for large datasets**: Polars DataFrames are more memory-efficient for large datasets

## API Rate Limits

Please be aware of Quantdle's API rate limits. The client automatically handles chunking to avoid timeouts, but you should still be mindful of making too many requests in a short period.

## Development & Testing

### Running Tests

The project has comprehensive test coverage with unit tests, integration tests, and end-to-end tests.

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run tests with coverage
pytest --cov=quantdle

# Run only unit tests (fast)
pytest -m unit

# Run only integration tests (may be slow)
pytest -m integration

# Run tests in parallel for speed
pytest -n auto
```

### Code Quality

We maintain high code quality standards:

```bash
# Format code with black
black quantdle tests

# Lint with flake8
flake8 quantdle

# Type checking with mypy
mypy quantdle
```

### Test Coverage

Our comprehensive test suite includes:

- **Unit Tests**: Fast, isolated tests for individual functions and classes
- **Integration Tests**: Tests that verify modules work together correctly
- **Mock Testing**: Extensive use of mocks to test API interactions without real API calls
- **Performance Tests**: Tests for large dataset handling and memory efficiency
- **Error Handling Tests**: Comprehensive error condition testing

Current test coverage is maintained above 85% with detailed reporting available in CI/CD.

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run the test suite (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Requirements

- Python 3.9 or higher
- pandas >= 1.3.0
- requests >= 2.25.0
- tqdm >= 4.60.0
- polars >= 0.16.0 (optional)

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues with the client, please open an issue on [GitHub](https://github.com/quantdle/quantdle-python/issues).

For questions about Quantdle's data or API access, please contact [Quantdle support](https://docs.quantdle.com).


