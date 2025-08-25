"""Cryptocurrency symbols supported by yfinance.

This module exposes a helper to retrieve a dictionary mapping friendly
cryptocurrency keys to the symbols yfinance expects on Yahoo Finance.

Keys chosen are short and convenient for lookups in other code.
"""

from typing import Dict, List


def get_crypto_symbols() -> Dict[str, str]:
    """Return a mapping of friendly keys to yfinance crypto symbols.

    The mapping includes popular cryptocurrencies. Keys are lowercase
    identifiers you can use in code (for example, 'btc', 'eth', 'ada').

    Returns:
        Dict[str, str]: mapping of friendly key -> yfinance/Yahoo symbol
    """
    return {
        # Major cryptocurrencies
        "btc": "BTC-USD",
        "bitcoin": "BTC-USD",
        "eth": "ETH-USD", 
        "ethereum": "ETH-USD",
        "usdt": "USDT-USD",
        "tether": "USDT-USD",
        "bnb": "BNB-USD",
        "binancecoin": "BNB-USD",
        "sol": "SOL-USD",
        "solana": "SOL-USD",
        "usdc": "USDC-USD",
        "usd_coin": "USDC-USD",
        "xrp": "XRP-USD",
        "ripple": "XRP-USD",
        "steth": "STETH-USD",
        "lido_staked_ether": "STETH-USD",
        "doge": "DOGE-USD",
        "dogecoin": "DOGE-USD",
        "ada": "ADA-USD",
        "cardano": "ADA-USD",
        
        # Popular altcoins
        "avax": "AVAX-USD",
        "avalanche": "AVAX-USD", 
        "link": "LINK-USD",
        "chainlink": "LINK-USD",
        "dot": "DOT-USD",
        "polkadot": "DOT-USD",
        "matic": "MATIC-USD",
        "polygon": "MATIC-USD",
        "uni": "UNI-USD",
        "uniswap": "UNI-USD",
        "ltc": "LTC-USD",
        "litecoin": "LTC-USD",
        "bch": "BCH-USD",
        "bitcoin_cash": "BCH-USD",
        "xlm": "XLM-USD",
        "stellar": "XLM-USD",
        "algo": "ALGO-USD",
        "algorand": "ALGO-USD",
        "vet": "VET-USD",
        "vechain": "VET-USD",
        "icp": "ICP-USD",
        "internet_computer": "ICP-USD",
        "fil": "FIL-USD",
        "filecoin": "FIL-USD",
        "atom": "ATOM-USD",
        "cosmos": "ATOM-USD",
        "etc": "ETC-USD",
        "ethereum_classic": "ETC-USD",
        "xmr": "XMR-USD",
        "monero": "XMR-USD",
        "near": "NEAR-USD",
        "near_protocol": "NEAR-USD",
        "aave": "AAVE-USD",
        "grt": "GRT-USD",
        "the_graph": "GRT-USD",
        "sand": "SAND-USD",
        "the_sandbox": "SAND-USD",
        "mana": "MANA-USD",
        "decentraland": "MANA-USD",
        
        # Stablecoins
        "dai": "DAI-USD",
        "busd": "BUSD-USD",
        "binance_usd": "BUSD-USD",
        "tusd": "TUSD-USD",
        "trueusd": "TUSD-USD",
        "pax": "USDP-USD",
        "pax_dollar": "USDP-USD",
        
        # Meme coins
        "shib": "SHIB-USD",
        "shiba_inu": "SHIB-USD",
        "pepe": "PEPE-USD",
        "floki": "FLOKI-USD",
        
        # DeFi tokens
        "comp": "COMP-USD",
        "compound": "COMP-USD",
        "mkr": "MKR-USD",
        "maker": "MKR-USD",
        "snx": "SNX-USD",
        "synthetix": "SNX-USD",
        "crv": "CRV-USD",
        "curve": "CRV-USD",
        "bal": "BAL-USD",
        "balancer": "BAL-USD",
        
        # Exchange tokens
        "cro": "CRO-USD",
        "crypto_com": "CRO-USD",
        "ftt": "FTT-USD",
        "ftx_token": "FTT-USD",
        "ht": "HT-USD",
        "huobi_token": "HT-USD",
        "okb": "OKB-USD",
        "okex_token": "OKB-USD",
    }


def get_crypto_categories() -> Dict[str, List[str]]:
    """Return cryptocurrency symbols grouped by categories.
    
    Returns:
        Dict[str, List[str]]: mapping of category -> list of symbol keys
    """
    return {
        "major": ["btc", "eth", "bnb", "sol", "ada", "xrp", "doge", "avax", "dot", "matic"],
        "stablecoins": ["usdt", "usdc", "dai", "busd", "tusd", "pax"],
        "defi": ["uni", "link", "aave", "comp", "mkr", "snx", "crv", "bal", "grt"],
        "meme": ["doge", "shib", "pepe", "floki"],
        "exchange": ["bnb", "cro", "ftt", "ht", "okb"],
        "layer1": ["eth", "sol", "ada", "avax", "dot", "atom", "near", "algo"],
        "layer2": ["matic", "icp", "fil"]
    }


def get_symbols_by_category(category: str) -> List[str]:
    """Get cryptocurrency symbols for a specific category.
    
    Args:
        category: The category name (major, stablecoins, defi, etc.)
        
    Returns:
        List of symbol keys for the category
    """
    categories = get_crypto_categories()
    return categories.get(category.lower(), [])


if __name__ == "__main__":
    # Quick smoke test when run as a script
    print("Crypto symbols:")
    print(get_crypto_symbols())
    print("\nCategories:")
    for category, symbols in get_crypto_categories().items():
        print(f"{category}: {symbols[:5]}...")  # Show first 5 symbols per category