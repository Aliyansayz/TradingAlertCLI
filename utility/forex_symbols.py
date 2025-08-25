"""Forex symbols supported by yfinance.

This module exposes a helper to retrieve a dictionary mapping friendly
forex pair keys to the symbols yfinance expects on Yahoo Finance.

Keys chosen are short and convenient for lookups in other code.
"""

from typing import Dict


def get_forex_symbols() -> Dict[str, str]:
	"""Return a mapping of friendly keys to yfinance forex symbols.

	The mapping includes common major and minor forex pairs. Keys are lowercase
	identifiers you can use in code (for example, 'eurusd', 'gbpusd', 'usdjpy').

	Returns:
		Dict[str, str]: mapping of friendly key -> yfinance/Yahoo symbol
	"""
	return {
		# Major pairs
		"eurusd": "EURUSD=X",
		"usdjpy": "USDJPY=X",
		"gbpusd": "GBPUSD=X",
		"usdchf": "USDCHF=X",
		"audusd": "AUDUSD=X",
		"usdcad": "USDCAD=X",
		"nzdusd": "NZDUSD=X",

		# Minor pairs
		"eurjpy": "EURJPY=X",
		"eurgbp": "EURGBP=X",
		"eurchf": "EURCHF=X",
		"eurcad": "EURCAD=X",
		"euraud": "EURAUD=X",
		"eurnzd": "EURNZD=X",
		"gbpjpy": "GBPJPY=X",
		"gbpchf": "GBPCHF=X",
		"gbpcad": "GBPCAD=X",
		"gbpaud": "GBPAUD=X",
		"gbpnzd": "GBPNZD=X",
		"audjpy": "AUDJPY=X",
		"audcad": "AUDCAD=X",
		"audchf": "AUDCHF=X",
		"audnzd": "AUDNZD=X",
		"cadjpy": "CADJPY=X",
		"cadchf": "CADCHF=X",
		"chfjpy": "CHFJPY=X",
		"nzdjpy": "NZDJPY=X",
		"nzdcad": "NZDCAD=X",
		"nzdchf": "NZDCHF=X",
	}


if __name__ == "__main__":
	# Quick smoke test when run as a script
	print(get_forex_symbols())
