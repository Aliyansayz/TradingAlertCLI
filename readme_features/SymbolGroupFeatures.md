# Symbol Group Features - TradeMaster Pro CLI

## 🎯 Overview
Symbol Groups are the organizational foundation of TradeMaster Pro, allowing traders to create, manage, and analyze collections of financial instruments with customized configurations. Each group can contain multiple symbols with different timeframes, periods, and analysis settings for comprehensive market coverage.

## 🏗️ Symbol Group Architecture

### 📊 Core Symbol Group Structure
```python
# Implementation in: symbol_groups_manager.py

@dataclass
class SymbolConfig:
    """Configuration for individual symbol within a group"""
    symbol: str                    # e.g., 'EURUSD', 'AAPL', 'BTC'
    asset_type: str               # 'forex', 'stocks', 'crypto', 'indices'
    timeframe: str                # '1m', '5m', '15m', '30m', '1h', '4h', '1d'
    period: str                   # '1d', '5d', '1mo', '3mo', '6mo', '1y'
    data_source: str = "yfinance" # Data provider
    enabled: bool = True          # Active/inactive status
    
@dataclass  
class SymbolGroup:
    """Complete symbol group configuration"""
    group_id: str                 # Unique identifier
    name: str                     # Display name
    description: str              # Group description
    symbols: Dict[str, SymbolConfig]  # Symbol configurations
    created_at: str               # Creation timestamp
    updated_at: str               # Last modification
    enabled: bool = True          # Group active status
    tags: List[str] = None        # Classification tags
    metadata: Dict[str, Any] = None   # Additional settings
```

### 🎛️ Symbol Group Manager
```python
class SymbolGroupManager:
    """
    Complete CRUD system for symbol group management
    """
    
    def __init__(self, storage_path="symbol_groups/groups.json"):
        self.storage_path = storage_path
        self.groups = {}
        self.load_groups()
    
    def create_group(self, name, description, symbols, tags=None, metadata=None):
        """Create new symbol group with specified configuration"""
        
    def read_group(self, group_id):
        """Retrieve symbol group by ID"""
        
    def update_group(self, group_id, **updates):
        """Update existing symbol group"""
        
    def delete_group(self, group_id):
        """Delete symbol group and all configurations"""
        
    def list_groups(self, enabled_only=True):
        """List all available symbol groups"""
```

## 📊 Pre-configured Symbol Groups

### 🏦 Forex Trading Groups
```json
{
  "major_forex_scalping": {
    "name": "Major Forex Scalping",
    "description": "High-frequency trading on major currency pairs",
    "symbols": {
      "eurusd_1m": {"symbol": "EURUSD", "timeframe": "1m", "period": "1d"},
      "gbpusd_1m": {"symbol": "GBPUSD", "timeframe": "1m", "period": "1d"},
      "usdjpy_1m": {"symbol": "USDJPY", "timeframe": "1m", "period": "1d"}
    },
    "tags": ["forex", "scalping", "major_pairs"]
  },
  
  "forex_swing_trading": {
    "name": "Forex Swing Trading",
    "description": "Medium-term forex positions",
    "symbols": {
      "eurusd_4h": {"symbol": "EURUSD", "timeframe": "4h", "period": "1mo"},
      "gbpusd_4h": {"symbol": "GBPUSD", "timeframe": "4h", "period": "1mo"},
      "audusd_4h": {"symbol": "AUDUSD", "timeframe": "4h", "period": "1mo"}
    },
    "tags": ["forex", "swing_trading"]
  }
}
```

### 📈 Stock Portfolio Groups
```json
{
  "tech_giants_day_trading": {
    "name": "Technology Giants - Day Trading",
    "description": "Large cap tech stocks for intraday trading",
    "symbols": {
      "aapl_15m": {"symbol": "AAPL", "timeframe": "15m", "period": "5d"},
      "googl_15m": {"symbol": "GOOGL", "timeframe": "15m", "period": "5d"},
      "msft_15m": {"symbol": "MSFT", "timeframe": "15m", "period": "5d"},
      "amzn_15m": {"symbol": "AMZN", "timeframe": "15m", "period": "5d"}
    },
    "tags": ["stocks", "technology", "day_trading", "large_cap"]
  },
  
  "dividend_aristocrats": {
    "name": "Dividend Aristocrats Portfolio",
    "description": "Long-term dividend growth stocks",
    "symbols": {
      "ko_1d": {"symbol": "KO", "timeframe": "1d", "period": "1y"},
      "jnj_1d": {"symbol": "JNJ", "timeframe": "1d", "period": "1y"},
      "pep_1d": {"symbol": "PEP", "timeframe": "1d", "period": "1y"}
    },
    "tags": ["stocks", "dividend", "long_term"]
  }
}
```

### 🪙 Cryptocurrency Groups
```json
{
  "crypto_major_coins": {
    "name": "Major Cryptocurrency Portfolio",
    "description": "Top cryptocurrencies by market cap",
    "symbols": {
      "btc_1h": {"symbol": "BTC-USD", "timeframe": "1h", "period": "7d"},
      "eth_1h": {"symbol": "ETH-USD", "timeframe": "1h", "period": "7d"},
      "bnb_4h": {"symbol": "BNB-USD", "timeframe": "4h", "period": "1mo"}
    },
    "tags": ["crypto", "major", "volatile"]
  },
  
  "defi_tokens": {
    "name": "DeFi Token Analysis",
    "description": "Decentralized Finance protocol tokens",
    "symbols": {
      "uni_4h": {"symbol": "UNI-USD", "timeframe": "4h", "period": "1mo"},
      "aave_4h": {"symbol": "AAVE-USD", "timeframe": "4h", "period": "1mo"},
      "comp_4h": {"symbol": "COMP-USD", "timeframe": "4h", "period": "1mo"}
    },
    "tags": ["crypto", "defi", "altcoins"]
  }
}
```

## 🔧 Group Management Operations

### ➕ Creating Symbol Groups
```python
class GroupCreationWizard:
    """
    Interactive group creation with validation
    """
    
    def create_forex_group(self):
        """Create forex-focused symbol group"""
        print("🏦 FOREX GROUP CREATION WIZARD")
        print("=" * 40)
        
        # Collect group information
        name = input("Group Name: ")
        description = input("Description: ")
        
        # Select forex pairs
        available_pairs = self.get_forex_symbols()
        selected_pairs = self.multi_select_symbols(available_pairs)
        
        # Configure timeframes
        timeframe_config = self.configure_timeframes(selected_pairs)
        
        # Create and save group
        group_id = self.symbol_manager.create_group(
            name=name,
            description=description,
            symbols=timeframe_config,
            tags=['forex']
        )
        
        return group_id
    
    def create_custom_group(self):
        """Create custom multi-asset group"""
        # Interactive multi-asset group creation
        
    def duplicate_group(self, source_group_id, new_name):
        """Create new group based on existing one"""
```

### ✏️ Editing Symbol Groups
```python
class GroupEditor:
    """
    Comprehensive group editing capabilities
    """
    
    def add_symbol_to_group(self, group_id, symbol_config):
        """Add new symbol to existing group"""
        
    def remove_symbol_from_group(self, group_id, symbol_key):
        """Remove symbol from group"""
        
    def update_symbol_config(self, group_id, symbol_key, new_config):
        """Update individual symbol configuration"""
        
    def change_group_timeframes(self, group_id, new_timeframe):
        """Batch update timeframes for all symbols in group"""
        
    def toggle_symbol_status(self, group_id, symbol_key, enabled=None):
        """Enable/disable individual symbol"""
        
    def rebalance_group(self, group_id, target_distribution):
        """Rebalance symbol weightings in group"""
```

### 🗂️ Group Organization
```python
class GroupOrganizer:
    """
    Advanced group organization and categorization
    """
    
    def categorize_by_asset_type(self):
        """Organize groups by asset class"""
        categories = {
            'forex': [],
            'stocks': [],
            'crypto': [],
            'indices': [],
            'mixed': []
        }
        
    def categorize_by_trading_style(self):
        """Organize groups by trading strategy"""
        styles = {
            'scalping': [],      # < 5 minute timeframes
            'day_trading': [],   # 5m - 1h timeframes
            'swing_trading': [], # 4h - 1d timeframes
            'position_trading': [] # > 1d timeframes
        }
        
    def categorize_by_market_cap(self):
        """Organize stock groups by market capitalization"""
        
    def create_group_hierarchy(self):
        """Create hierarchical group structure"""
```

## 🎛️ Symbol-Level Configuration

### ⚙️ Individual Symbol Settings
```python
class SymbolConfiguration:
    """
    Detailed configuration for individual symbols within groups
    """
    
    def __init__(self, symbol_key, group_id):
        self.symbol_key = symbol_key
        self.group_id = group_id
        self.config = self.load_symbol_config()
    
    def update_timeframe(self, new_timeframe):
        """Change symbol's analysis timeframe"""
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1wk', '1mo']
        if new_timeframe in valid_timeframes:
            self.config.timeframe = new_timeframe
            self.save_config()
    
    def update_period(self, new_period):
        """Change symbol's data period"""
        valid_periods = ['1d', '5d', '1wk', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max']
        if new_period in valid_periods:
            self.config.period = new_period
            self.save_config()
    
    def set_data_source(self, source):
        """Configure data source for symbol"""
        available_sources = ['yfinance', 'alpha_vantage', 'twelve_data']
        if source in available_sources:
            self.config.data_source = source
            self.save_config()
    
    def toggle_status(self):
        """Enable/disable symbol in group"""
        self.config.enabled = not self.config.enabled
        self.save_config()
```

### 📊 Symbol-Specific Indicator Settings
```python
class SymbolIndicatorConfig:
    """
    Indicator configuration at the symbol level
    """
    
    def __init__(self, symbol_key, group_id):
        self.symbol_key = symbol_key
        self.group_id = group_id
        self.indicator_settings = self.load_indicator_settings()
    
    def customize_rsi_settings(self, period=14, overbought=70, oversold=30):
        """Customize RSI parameters for this symbol"""
        self.indicator_settings['RSI'] = {
            'period': period,
            'overbought': overbought,
            'oversold': oversold,
            'enabled': True
        }
        self.save_settings()
    
    def customize_macd_settings(self, fast=12, slow=26, signal=9):
        """Customize MACD parameters for this symbol"""
        self.indicator_settings['MACD'] = {
            'fast_period': fast,
            'slow_period': slow,
            'signal_period': signal,
            'enabled': True
        }
        self.save_settings()
    
    def set_asset_optimized_indicators(self):
        """Apply asset-type optimized indicator settings"""
        asset_type = self.get_symbol_asset_type()
        
        if asset_type == 'forex':
            self.apply_forex_optimized_settings()
        elif asset_type == 'stocks':
            self.apply_stock_optimized_settings()
        elif asset_type == 'crypto':
            self.apply_crypto_optimized_settings()
```

## 🔄 Group Analysis Engine

### 📈 Batch Analysis Processing
```python
class GroupAnalysisEngine:
    """
    Analyze entire symbol groups with parallel processing
    """
    
    def __init__(self):
        self.parallel_workers = 4
        self.analysis_cache = {}
    
    def analyze_group(self, group_id, force_refresh=False):
        """
        Comprehensive analysis of all symbols in group
        
        Returns:
            - Individual symbol analysis results
            - Group-level statistics
            - Correlation analysis
            - Risk metrics
            - Portfolio-level insights
        """
        
    def analyze_symbol_correlations(self, group_data):
        """Calculate correlation matrix for symbols in group"""
        
    def calculate_group_diversification(self, group_data):
        """Measure diversification within the group"""
        
    def generate_group_sentiment(self, individual_results):
        """Aggregate individual symbol sentiments into group sentiment"""
        
    def identify_group_leaders_laggards(self, group_results):
        """Identify best and worst performing symbols"""
```

### 🎯 Real-time Group Monitoring
```python
class GroupMonitor:
    """
    Real-time monitoring of symbol group performance
    """
    
    def start_group_monitoring(self, group_id, update_interval_minutes=15):
        """Start real-time monitoring for symbol group"""
        
    def check_group_alerts(self, group_id):
        """Check for any alerts within the group"""
        
    def get_group_dashboard_data(self, group_id):
        """Get real-time dashboard data for group"""
        
    def generate_group_summary_report(self, group_id):
        """Generate comprehensive group performance report"""
```

## 🚨 Alert System Integration

### 📢 Group-Level Alerts
```python
class GroupAlertSystem:
    """
    Comprehensive alert system for symbol groups
    """
    
    def setup_group_alerts(self, group_id, alert_config):
        """Configure alerts for the entire group"""
        alert_types = {
            'sentiment_change': 'Alert when group sentiment changes',
            'correlation_breakdown': 'Alert when correlations change significantly',
            'volatility_spike': 'Alert when group volatility increases',
            'new_signals': 'Alert when new trading signals appear',
            'risk_threshold': 'Alert when risk metrics exceed thresholds'
        }
        
    def check_correlation_alerts(self, group_id, threshold=0.8):
        """Alert when symbol correlations become too high"""
        
    def check_diversification_alerts(self, group_id, min_diversification=0.6):
        """Alert when group diversification drops below threshold"""
        
    def generate_daily_group_summary(self, group_id):
        """Generate daily summary email for group performance"""
```

## 🎛️ CLI Group Management Interface

### 💻 Interactive Group Management
```bash
# Access through main CLI menu
python trading_cli.py

# Symbol Group Management Menu:
# ├── 1. 📊 View All Groups
# ├── 2. ➕ Create New Group
# ├── 3. ✏️ Edit Existing Group
# ├── 4. 🗑️ Delete Group
# ├── 5. 🔄 Duplicate Group
# ├── 6. 📈 Analyze Group
# ├── 7. 🚨 Configure Group Alerts
# ├── 8. 📤 Export Group Data
# ├── 9. 📥 Import Group Configuration
# └── 0. 🔙 Back to Main Menu
```

### 🎯 CLI Group Operations
```python
class CLIGroupManager:
    """
    Command-line interface for group management
    """
    
    def cli_view_all_groups(self):
        """Display all groups in formatted table"""
        print("📊 SYMBOL GROUPS OVERVIEW")
        print("=" * 60)
        
        groups = self.group_manager.list_groups()
        for group in groups:
            print(f"🏷️  {group['name']}")
            print(f"   ID: {group['group_id']}")
            print(f"   Symbols: {len(group['symbols'])}")
            print(f"   Status: {'🟢 Active' if group['enabled'] else '🔴 Inactive'}")
            print(f"   Tags: {', '.join(group.get('tags', []))}")
            print()
    
    def cli_create_group_wizard(self):
        """Interactive group creation wizard"""
        
    def cli_edit_group_menu(self, group_id):
        """Interactive group editing menu"""
        
    def cli_analyze_group_interactive(self, group_id):
        """Interactive group analysis with real-time updates"""
```

## 📊 Group Performance Analytics

### 📈 Performance Metrics
```python
class GroupPerformanceAnalyzer:
    """
    Comprehensive performance analysis for symbol groups
    """
    
    def calculate_group_statistics(self, group_results):
        """
        Calculate comprehensive group statistics
        
        Returns:
            - Average returns across symbols
            - Volatility metrics
            - Sharpe ratio for the group
            - Maximum drawdown
            - Win/loss ratios
            - Correlation statistics
        """
        
    def compare_groups(self, group_ids, time_period='1mo'):
        """Compare performance between multiple groups"""
        
    def generate_risk_report(self, group_id):
        """Generate comprehensive risk analysis report"""
        
    def calculate_optimal_position_sizing(self, group_id, total_capital, risk_per_trade=0.02):
        """Calculate optimal position sizes for group symbols"""
```

### 📊 Visualization Support
```python
class GroupVisualization:
    """
    Data preparation for group visualization
    """
    
    def prepare_correlation_heatmap_data(self, group_id):
        """Prepare data for correlation heatmap visualization"""
        
    def prepare_performance_chart_data(self, group_id, time_period='1mo'):
        """Prepare data for group performance charts"""
        
    def prepare_risk_distribution_data(self, group_id):
        """Prepare data for risk distribution analysis"""
        
    def export_visualization_data(self, group_id, format='json'):
        """Export data in format suitable for external visualization tools"""
```

## 🔧 Advanced Group Features

### 🎯 Dynamic Group Rebalancing
```python
class DynamicGroupRebalancer:
    """
    Automatically rebalance groups based on performance and risk metrics
    """
    
    def auto_rebalance_by_performance(self, group_id, rebalance_frequency='weekly'):
        """Automatically rebalance based on performance metrics"""
        
    def auto_rebalance_by_volatility(self, group_id, target_volatility=0.15):
        """Rebalance to maintain target group volatility"""
        
    def adaptive_symbol_weighting(self, group_id, weighting_method='risk_parity'):
        """Dynamically adjust symbol weightings"""
        
    def remove_underperforming_symbols(self, group_id, performance_threshold=-0.05):
        """Automatically remove consistently underperforming symbols"""
```

### 🔄 Group Templates
```python
class GroupTemplateManager:
    """
    Manage pre-configured group templates
    """
    
    def create_template(self, template_name, group_config):
        """Create reusable group template"""
        
    def apply_template(self, template_name, custom_symbols=None):
        """Create new group from template"""
        
    def list_available_templates(self):
        """List all available group templates"""
        
    def template_categories(self):
        """Organize templates by category"""
        return {
            'forex_strategies': ['major_pairs_scalping', 'exotic_pairs_swing'],
            'stock_sectors': ['tech_momentum', 'healthcare_value', 'energy_dividend'],
            'crypto_categories': ['defi_tokens', 'layer1_protocols', 'meme_coins'],
            'mixed_portfolios': ['balanced_growth', 'income_focused', 'high_risk_reward']
        }
```

## 💾 Data Management

### 🗄️ Group Data Storage
```python
class GroupDataManager:
    """
    Manage group data storage and retrieval
    """
    
    def save_group_configuration(self, group_id, config):
        """Save group configuration to persistent storage"""
        
    def backup_all_groups(self, backup_path):
        """Create backup of all group configurations"""
        
    def restore_groups_from_backup(self, backup_path):
        """Restore groups from backup file"""
        
    def export_group_to_file(self, group_id, export_format='json'):
        """Export single group configuration to file"""
        
    def import_group_from_file(self, file_path):
        """Import group configuration from file"""
```

### 📊 Group History Tracking
```python
class GroupHistoryTracker:
    """
    Track changes and performance history for groups
    """
    
    def log_group_change(self, group_id, change_type, details):
        """Log changes made to group configuration"""
        
    def get_group_change_history(self, group_id, time_period='1mo'):
        """Retrieve change history for group"""
        
    def track_group_performance_history(self, group_id):
        """Track historical performance of group"""
        
    def generate_group_evolution_report(self, group_id):
        """Generate report showing how group has evolved over time"""
```

Symbol Groups provide the organizational foundation for systematic trading analysis in TradeMaster Pro, enabling sophisticated portfolio management and comprehensive market analysis across multiple assets and timeframes.
