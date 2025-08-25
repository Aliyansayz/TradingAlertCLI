"""Stock symbols and tickers.

This module provides mappings for popular stock symbols and market sectors
to facilitate easy access to stock data through yfinance.

Keys chosen are short and convenient for lookups in other code.
"""

from typing import Dict, List


def get_popular_stocks() -> Dict[str, str]:
    """Return a mapping of friendly keys to popular stock symbols.

    The mapping includes major US stocks across different sectors.
    Keys are lowercase identifiers for easy reference.

    Returns:
        Dict[str, str]: mapping of friendly key -> stock ticker symbol
    """
    return {
        # Technology giants (FAANG+)
        "apple": "AAPL",
        "aapl": "AAPL",
        "microsoft": "MSFT",
        "msft": "MSFT",
        "alphabet": "GOOGL",
        "google": "GOOGL",
        "googl": "GOOGL",
        "amazon": "AMZN",
        "amzn": "AMZN",
        "meta": "META",
        "facebook": "META",
        "netflix": "NFLX",
        "nflx": "NFLX",
        "tesla": "TSLA",
        "tsla": "TSLA",
        "nvidia": "NVDA",
        "nvda": "NVDA",
        
        # Major tech companies
        "oracle": "ORCL",
        "orcl": "ORCL",
        "salesforce": "CRM",
        "crm": "CRM",
        "adobe": "ADBE",
        "adbe": "ADBE",
        "intel": "INTC",
        "intc": "INTC",
        "amd": "AMD",
        "cisco": "CSCO",
        "csco": "CSCO",
        "ibm": "IBM",
        "qualcomm": "QCOM",
        "qcom": "QCOM",
        "broadcom": "AVGO",
        "avgo": "AVGO",
        
        # Financial sector
        "berkshire": "BRK-B",
        "brk": "BRK-B",
        "jpmorgan": "JPM",
        "jpm": "JPM",
        "visa": "V",
        "mastercard": "MA",
        "ma": "MA",
        "bank_america": "BAC",
        "bac": "BAC",
        "wells_fargo": "WFC",
        "wfc": "WFC",
        "goldman": "GS",
        "gs": "GS",
        "morgan_stanley": "MS",
        "ms": "MS",
        "american_express": "AXP",
        "axp": "AXP",
        
        # Healthcare & Pharmaceuticals
        "johnson_johnson": "JNJ",
        "jnj": "JNJ",
        "pfizer": "PFE",
        "pfe": "PFE",
        "unitedhealth": "UNH",
        "unh": "UNH",
        "abbvie": "ABBV",
        "abbv": "ABBV",
        "merck": "MRK",
        "mrk": "MRK",
        "eli_lilly": "LLY",
        "lly": "LLY",
        "bristol_myers": "BMY",
        "bmy": "BMY",
        
        # Consumer goods
        "procter_gamble": "PG",
        "pg": "PG",
        "coca_cola": "KO",
        "ko": "KO",
        "walmart": "WMT",
        "wmt": "WMT",
        "home_depot": "HD",
        "hd": "HD",
        "mcdonalds": "MCD",
        "mcd": "MCD",
        "nike": "NKE",
        "nke": "NKE",
        "disney": "DIS",
        "dis": "DIS",
        
        # Energy
        "exxon": "XOM",
        "xom": "XOM",
        "chevron": "CVX",
        "cvx": "CVX",
        "conocophillips": "COP",
        "cop": "COP",
        
        # Industrial
        "boeing": "BA",
        "ba": "BA",
        "caterpillar": "CAT",
        "cat": "CAT",
        "ge": "GE",
        "general_electric": "GE",
        "honeywell": "HON",
        "hon": "HON",
        
        # Telecommunications
        "verizon": "VZ",
        "vz": "VZ",
        "at_t": "T",
        "att": "T",
        "comcast": "CMCSA",
        "cmcsa": "CMCSA",
        
        # Transportation
        "fedex": "FDX",
        "fdx": "FDX",
        "ups": "UPS",
        "delta": "DAL",
        "dal": "DAL",
        "southwest": "LUV",
        "luv": "LUV",
        
        # Real Estate
        "american_tower": "AMT",
        "amt": "AMT",
        "crown_castle": "CCI",
        "cci": "CCI",
        
        # Utilities
        "nextera": "NEE",
        "nee": "NEE",
        "dominion": "D",
        
        # Emerging/Growth stocks
        "zoom": "ZM",
        "zm": "ZM",
        "slack": "WORK",
        "work": "WORK",
        "spotify": "SPOT",
        "spot": "SPOT",
        "uber": "UBER",
        "lyft": "LYFT",
        "airbnb": "ABNB",
        "abnb": "ABNB",
        "snowflake": "SNOW",
        "snow": "SNOW",
        "palantir": "PLTR",
        "pltr": "PLTR",
        "square": "SQ",
        "sq": "SQ",
        "paypal": "PYPL",
        "pypl": "PYPL",
        "shopify": "SHOP",
        "shop": "SHOP",
    }


def get_sector_stocks() -> Dict[str, List[str]]:
    """Return stock symbols grouped by market sectors.
    
    Returns:
        Dict[str, List[str]]: mapping of sector -> list of stock symbols
    """
    return {
        "technology": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "ORCL", "CRM", "ADBE", "INTC"],
        "healthcare": ["JNJ", "PFE", "UNH", "ABBV", "MRK", "LLY", "BMY"],
        "financial": ["JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "AXP", "BRK-B"],
        "consumer_discretionary": ["TSLA", "HD", "MCD", "NKE", "DIS", "AMZN"],
        "consumer_staples": ["PG", "KO", "WMT"],
        "energy": ["XOM", "CVX", "COP"],
        "industrial": ["BA", "CAT", "GE", "HON"],
        "telecommunications": ["VZ", "T", "CMCSA"],
        "utilities": ["NEE", "D"],
        "real_estate": ["AMT", "CCI"],
        "growth": ["ZM", "SPOT", "UBER", "ABNB", "SNOW", "PLTR", "SQ", "PYPL", "SHOP"]
    }


def get_market_cap_categories() -> Dict[str, List[str]]:
    """Return stock symbols grouped by market capitalization.
    
    Returns:
        Dict[str, List[str]]: mapping of market cap category -> list of symbols
    """
    return {
        "mega_cap": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK-B"],
        "large_cap": ["JPM", "V", "JNJ", "WMT", "PG", "UNH", "HD", "MA", "DIS", "NFLX"],
        "mid_cap": ["ZM", "SPOT", "SQ", "PYPL", "SNOW"],
        "small_cap": ["PLTR", "ABNB", "WORK"]
    }


def get_stocks_by_sector(sector: str) -> List[str]:
    """Get stock symbols for a specific sector.
    
    Args:
        sector: The sector name (technology, healthcare, financial, etc.)
        
    Returns:
        List of stock symbols for the sector
    """
    sectors = get_sector_stocks()
    return sectors.get(sector.lower(), [])


def get_stocks_by_market_cap(category: str) -> List[str]:
    """Get stock symbols for a specific market cap category.
    
    Args:
        category: The market cap category (mega_cap, large_cap, etc.)
        
    Returns:
        List of stock symbols for the category
    """
    categories = get_market_cap_categories()
    return categories.get(category.lower(), [])


def search_stock(query: str) -> List[str]:
    """Search for stocks by company name or symbol.
    
    Args:
        query: Search term (company name or symbol)
        
    Returns:
        List of matching stock symbols
    """
    stocks = get_popular_stocks()
    query_lower = query.lower()
    
    matches = []
    for key, symbol in stocks.items():
        if query_lower in key or query_lower == symbol.lower():
            matches.append(symbol)
    
    return list(set(matches))  # Remove duplicates


if __name__ == "__main__":
    # Quick smoke test when run as a script
    print("Popular stocks sample:")
    stocks = get_popular_stocks()
    for i, (key, symbol) in enumerate(stocks.items()):
        if i < 10:  # Show first 10
            print(f"  {key}: {symbol}")
        else:
            break
    
    print(f"\nTotal stocks: {len(stocks)}")
    
    print("\nSectors:")
    for sector, symbols in get_sector_stocks().items():
        print(f"  {sector}: {len(symbols)} stocks")
        
    print("\nSearch test for 'apple':")
    print(search_stock("apple"))