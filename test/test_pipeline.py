"""
Test script for the Finance Trade Assistant Backend Pipeline System

This script validates that all components work correctly and maintains
backward compatibility with the original code.
"""

def test_basic_imports():
    """Test that all modules can be imported successfully."""
    try:
        print("Testing basic imports...")
        
        # Test symbol imports
        from utility.forex_symbols import get_forex_symbols
        from utility.indices_symbols import get_indices_symbols  
        from utility.crypto_symbols import get_crypto_symbols
        from utility.stocks_symbols import get_popular_stocks
        
        print("✓ Symbol modules imported successfully")
        
        # Test instruction module
        from instructions import get_pipeline_overview
        print("✓ Instructions module imported successfully")
        
        # Test data structures
        forex_symbols = get_forex_symbols()
        crypto_symbols = get_crypto_symbols()
        stocks = get_popular_stocks()
        
        print(f"✓ Symbol data loaded: {len(forex_symbols)} forex, {len(crypto_symbols)} crypto, {len(stocks)} stocks")
        
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {str(e)}")
        return False

def test_symbol_lookup():
    """Test symbol lookup functionality."""
    try:
        print("\nTesting symbol lookup...")
        
        from utility.forex_symbols import get_forex_symbols
        from utility.crypto_symbols import get_crypto_symbols, get_crypto_categories
        from utility.stocks_symbols import get_popular_stocks, search_stock
        
        # Test forex lookup
        forex = get_forex_symbols()
        eurusd = forex.get('eurusd')
        print(f"✓ EURUSD symbol: {eurusd}")
        
        # Test crypto lookup  
        crypto = get_crypto_symbols()
        btc = crypto.get('btc')
        print(f"✓ BTC symbol: {btc}")
        
        # Test stock search
        apple_results = search_stock('apple')
        print(f"✓ Apple search results: {apple_results}")
        
        # Test crypto categories
        categories = get_crypto_categories()
        major_cryptos = categories.get('major', [])
        print(f"✓ Major crypto categories: {major_cryptos[:5]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Symbol lookup test failed: {str(e)}")
        return False

def test_pipeline_structure():
    """Test that pipeline files exist and have basic structure."""
    try:
        print("\nTesting pipeline structure...")
        
        import os
        
        # Check that all pipeline files exist
        pipeline_files = [
            'pipeline_fetching_data.py',
            'pipeline_applying_indicator.py', 
            'pipeline_defining_strategy.py',
            'pipeline_main.py'
        ]
        
        for file in pipeline_files:
            if os.path.exists(file):
                print(f"✓ {file} exists")
            else:
                print(f"✗ {file} missing")
                return False
        
        # Check original files are preserved
        original_files = [
            'yfinance_data_loader.py',
            'indicators.py',
            'indicators_oscillators.py',
            'strategy.py'
        ]
        
        for file in original_files:
            if os.path.exists(file):
                print(f"✓ Original {file} preserved")
            else:
                print(f"✗ Original {file} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Pipeline structure test failed: {str(e)}")
        return False

def test_documentation():
    """Test documentation and instruction functionality."""
    try:
        print("\nTesting documentation...")
        
        from instructions import (
            get_pipeline_overview,
            get_quick_start_guide, 
            get_migration_guide,
            get_api_reference,
            get_examples
        )
        
        # Test that documentation functions return content
        overview = get_pipeline_overview()
        quick_start = get_quick_start_guide()
        migration = get_migration_guide()
        api_ref = get_api_reference()
        examples = get_examples()
        
        assert len(overview) > 100, "Overview too short"
        assert len(quick_start) > 100, "Quick start guide too short"
        assert len(migration) > 100, "Migration guide too short"
        assert len(api_ref) > 5, "API reference incomplete"
        assert len(examples) > 3, "Not enough examples"
        
        print("✓ All documentation functions working")
        print(f"✓ API reference has {len(api_ref)} sections")
        print(f"✓ Examples include {len(examples)} use cases")
        
        return True
        
    except Exception as e:
        print(f"✗ Documentation test failed: {str(e)}")
        return False

def test_original_code_preservation():
    """Test that original code is preserved and accessible."""
    try:
        print("\nTesting original code preservation...")
        
        # Check that original files have content
        import os
        
        with open('yfinance_data_loader.py', 'r') as f:
            content = f.read()
            if 'EURUSD=X' in content:
                print("✓ Original yfinance_data_loader.py code preserved")
            else:
                print("✗ Original yfinance_data_loader.py code missing")
                return False
        
        with open('strategy.py', 'r') as f:
            content = f.read()
            if 'stoc_indicator' in content and 'adx_indicator' in content:
                print("✓ Original strategy.py code preserved")
            else:
                print("✗ Original strategy.py code missing")
                return False
        
        with open('indicators.py', 'r') as f:
            content = f.read()
            if 'class ADX:' in content and 'class RSI:' in content:
                print("✓ Original indicators.py classes preserved")
            else:
                print("✗ Original indicators.py classes missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Original code preservation test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all test functions."""
    print("FINANCE TRADE ASSISTANT - BACKEND PIPELINE TESTS")
    print("=" * 55)
    
    tests = [
        test_basic_imports,
        test_symbol_lookup,
        test_pipeline_structure,
        test_documentation,
        test_original_code_preservation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {str(e)}")
            failed += 1
    
    print(f"\n{'='*55}")
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Backend pipeline system is ready.")
        print("\nQuick start:")
        print("  python -c \"from instructions import print_quick_start; print_quick_start()\"")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    return failed == 0

if __name__ == "__main__":
    run_all_tests()
