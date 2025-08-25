"""Index symbols supported by yfinance.

This module exposes a helper to retrieve a dictionary mapping friendly
index keys to the symbols yfinance expects on Yahoo Finance.

Keys chosen are short and convenient for lookups in other code.
"""

from typing import Dict


def get_indices_symbols() -> Dict[str, str]:
	"""Return a mapping of friendly keys to yfinance symbols.

	The mapping includes common global market indices. Keys are lowercase
	identifiers you can use in code (for example, 'us30', 'sp500', 'nas100').

	Returns:
		Dict[str, str]: mapping of friendly key -> yfinance/Yahoo symbol
	"""
	return {
		# United States
		"us30": "^DJI",     # Dow Jones Industrial Average (Dow 30)
		"sp500": "^GSPC",   # S&P 500
		"nas100": "^NDX",   # Nasdaq 100
		"nasdaq": "^IXIC",  # Nasdaq Composite
		"russell2000": "^RUT",

		# Europe
		"dax": "^GDAXI",    # Germany DAX
		"ftse100": "^FTSE", # UK FTSE 100

		# Asia / Pacific
		"nikkei": "^N225",   # Nikkei 225 (Japan)
		"hangseng": "^HSI",  # Hang Seng (Hong Kong)
		"australia200": "^AXJO", # ASX 200 (Australia)

		# Canada
		"tsx": "^GSPTSE",    # S&P/TSX Composite (Canada)
	}


if __name__ == "__main__":
	# Quick smoke test when run as a script
	print(get_indices_symbols())

