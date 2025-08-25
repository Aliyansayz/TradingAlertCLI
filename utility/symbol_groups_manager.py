"""
Symbol Groups Management System

This module provides a comprehensive CRUD system for managing symbol groups.
Each group can contain multiple symbols with different timeframes and data sources.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import pandas as pd
from dataclasses import dataclass, asdict, field

@dataclass
class IndicatorSettings:
    """Settings for technical indicators on a symbol."""
    rsi_period: int = 14
    rsi_overbought: float = 70.0
    rsi_oversold: float = 30.0
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    bb_period: int = 20
    bb_std: float = 2.0
    sma_periods: List[int] = None
    ema_periods: List[int] = None
    stoch_k_period: int = 14
    stoch_d_period: int = 3
    adx_period: int = 14
    atr_period: int = 14
    williams_r_period: int = 14
    cci_period: int = 20
    roc_period: int = 12
    mfi_period: int = 14
    tsi_fast: int = 25
    tsi_slow: int = 13
    timeframe_strategy: str = "default-check-single-timeframe"
    
    def __post_init__(self):
        if self.sma_periods is None:
            self.sma_periods = [20, 50, 200]
        if self.ema_periods is None:
            self.ema_periods = [12, 26]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IndicatorSettings':
        """Create from dictionary."""
        return cls(**data)

@dataclass
class TimeWindowSlot:
    """Represents a time window slot for symbol execution."""
    start_time: str  # Format: "HH:MM" (24-hour format)
    end_time: str    # Format: "HH:MM" (24-hour format)
    timezone: str = "UTC"
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeWindowSlot':
        """Create from dictionary."""
        return cls(**data)
    
    def is_active_now(self) -> bool:
        """Check if current time falls within this window."""
        from datetime import datetime, time
        import pytz
        
        try:
            # Get current time in the specified timezone
            tz = pytz.timezone(self.timezone)
            current_time = datetime.now(tz).time()
            
            # Parse start and end times
            start_parts = self.start_time.split(':')
            end_parts = self.end_time.split(':')
            start_time = time(int(start_parts[0]), int(start_parts[1]))
            end_time = time(int(end_parts[0]), int(end_parts[1]))
            
            # Handle overnight windows (e.g., 22:00 to 06:00)
            if start_time <= end_time:
                # Same day window
                return start_time <= current_time <= end_time
            else:
                # Overnight window
                return current_time >= start_time or current_time <= end_time
                
        except Exception:
            # If there's any error, assume it's not active
            return False

@dataclass
class SymbolSchedulerSettings:
    """Symbol-level scheduler settings that can override group settings."""
    enabled: bool = False
    use_group_settings: bool = True  # If True, ignore symbol-level settings and use group defaults
    run_interval: int = 15  # minutes
    active_weekdays: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])  # 0=Monday, 6=Sunday
    time_windows: List[TimeWindowSlot] = field(default_factory=lambda: [TimeWindowSlot("11:00", "16:00")])  # Multiple time windows per day
    timezone: str = "UTC"
    priority: int = 1  # 1=Low, 2=Medium, 3=High
    max_concurrent_runs: int = 1  # How many instances can run simultaneously
    
    # Computed fields - these are generated, not stored
    _weekday_names: Dict[str, bool] = field(default=None, init=False, repr=False)
    _time_window_descriptions: List[str] = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        # Generate human-readable fields from the actual data
        self._weekday_names = self._generate_weekday_names()
        self._time_window_descriptions = self._generate_time_descriptions()
    
    @property
    def weekday_names(self) -> Dict[str, bool]:
        """Get human-readable weekday mapping."""
        if self._weekday_names is None:
            self._weekday_names = self._generate_weekday_names()
        return self._weekday_names
    
    @property 
    def time_window_descriptions(self) -> List[str]:
        """Get human-readable time window descriptions."""
        if self._time_window_descriptions is None:
            self._time_window_descriptions = self._generate_time_descriptions()
        return self._time_window_descriptions
    
    def _generate_weekday_names(self) -> Dict[str, bool]:
        """Generate human-readable weekday mapping."""
        weekday_map = {
            "Monday": 0 in self.active_weekdays,
            "Tuesday": 1 in self.active_weekdays,
            "Wednesday": 2 in self.active_weekdays,
            "Thursday": 3 in self.active_weekdays,
            "Friday": 4 in self.active_weekdays,
            "Saturday": 5 in self.active_weekdays,
            "Sunday": 6 in self.active_weekdays
        }
        return weekday_map
    
    def _generate_time_descriptions(self) -> List[str]:
        """Generate human-readable time window descriptions."""
        descriptions = []
        for window in self.time_windows:
            desc = self._convert_time_to_description(window.start_time, window.end_time)
            descriptions.append(desc)
        return descriptions
    
    @staticmethod
    def _convert_time_to_description(start_time: str, end_time: str) -> str:
        """Convert 24-hour time to 12-hour AM/PM format."""
        from datetime import datetime
        
        try:
            # Parse start time
            start_dt = datetime.strptime(start_time, "%H:%M")
            start_desc = start_dt.strftime("%I:%M %p").lstrip('0')
            
            # Parse end time
            end_dt = datetime.strptime(end_time, "%H:%M")
            end_desc = end_dt.strftime("%I:%M %p").lstrip('0')
            
            return f"{start_desc} - {end_desc}"
        except:
            return f"{start_time} - {end_time}"
    
    @staticmethod
    def parse_time_description(time_desc: str) -> tuple:
        """Parse user-friendly time like '8 AM - 1 PM' to 24-hour format."""
        import re
        from datetime import datetime
        
        # Pattern to match formats like "8 AM - 1 PM" or "8:30 AM - 1:45 PM"
        pattern = r'(\d{1,2}):?(\d{0,2})\s*(AM|PM)\s*-\s*(\d{1,2}):?(\d{0,2})\s*(AM|PM)'
        
        match = re.match(pattern, time_desc.upper().strip())
        if not match:
            raise ValueError(f"Invalid time format: {time_desc}. Use format like '8 AM - 1 PM'")
        
        start_hour, start_min, start_period, end_hour, end_min, end_period = match.groups()
        
        # Convert to integers and handle defaults
        start_hour = int(start_hour)
        start_min = int(start_min) if start_min else 0
        end_hour = int(end_hour)
        end_min = int(end_min) if end_min else 0
        
        # Convert to 24-hour format
        if start_period == 'PM' and start_hour != 12:
            start_hour += 12
        elif start_period == 'AM' and start_hour == 12:
            start_hour = 0
            
        if end_period == 'PM' and end_hour != 12:
            end_hour += 12
        elif end_period == 'AM' and end_hour == 12:
            end_hour = 0
        
        start_time = f"{start_hour:02d}:{start_min:02d}"
        end_time = f"{end_hour:02d}:{end_min:02d}"
        
        return start_time, end_time
    
    def get_active_weekday_names(self) -> List[str]:
        """Get list of active weekday names."""
        return [day for day, active in self.weekday_names.items() if active]
    
    def update_weekdays_from_names(self, weekday_names: Dict[str, bool]):
        """Update active weekdays from name mapping."""
        name_to_number = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
            "Friday": 4, "Saturday": 5, "Sunday": 6
        }
        
        # Update the underlying data
        self.active_weekdays = [
            name_to_number[day] for day, active in weekday_names.items() if active
        ]
        
        # Regenerate the computed fields
        self._weekday_names = self._generate_weekday_names()
        self._time_window_descriptions = self._generate_time_descriptions()
    
    def __post_init__(self):
        if self.active_weekdays is None:
            self.active_weekdays = [0, 1, 2, 3, 4]  # Weekdays only
        if self.time_windows is None:
            # Default: 11 AM to 4 PM
            self.time_windows = [
                TimeWindowSlot("11:00", "16:00", self.timezone, True)
            ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "enabled": self.enabled,
            "use_group_settings": self.use_group_settings,
            "run_interval": self.run_interval,
            "active_weekdays": self.active_weekdays,
            "weekday_names": self.weekday_names,
            "time_windows": [tw.to_dict() for tw in self.time_windows],
            "time_window_descriptions": self.time_window_descriptions,
            "timezone": self.timezone,
            "priority": self.priority,
            "max_concurrent_runs": self.max_concurrent_runs
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SymbolSchedulerSettings':
        """Create from dictionary."""
        time_windows = []
        if data.get("time_windows"):
            time_windows = [TimeWindowSlot.from_dict(tw) for tw in data["time_windows"]]
        
        # Use the provided weekdays or defaults
        active_weekdays = data.get("active_weekdays", [0, 1, 2, 3, 4])
        
        instance = cls(
            enabled=data.get("enabled", False),
            use_group_settings=data.get("use_group_settings", True),
            run_interval=data.get("run_interval", 15),
            active_weekdays=active_weekdays,
            time_windows=time_windows if time_windows else [TimeWindowSlot("11:00", "16:00")],
            timezone=data.get("timezone", "UTC"),
            priority=data.get("priority", 1),
            max_concurrent_runs=data.get("max_concurrent_runs", 1)
        )
        # Note: weekday_names and time_window_descriptions will be auto-generated in __post_init__
        
        return instance
    
    def is_active_now(self) -> bool:
        """Check if the symbol should be active based on current time and day."""
        from datetime import datetime
        import pytz
        
        if not self.enabled or self.use_group_settings:
            return False
        
        try:
            # Check if today is an active weekday
            tz = pytz.timezone(self.timezone)
            current_datetime = datetime.now(tz)
            current_weekday = current_datetime.weekday()
            
            if current_weekday not in self.active_weekdays:
                return False
            
            # Check if current time falls within any active time window
            for time_window in self.time_windows:
                if time_window.active and time_window.is_active_now():
                    return True
            
            return False
            
        except Exception:
            return False
    
    def add_time_window(self, start_time: str, end_time: str, timezone: str = None, active: bool = True):
        """Add a new time window to the schedule."""
        if timezone is None:
            timezone = self.timezone
        
        time_window = TimeWindowSlot(start_time, end_time, timezone, active)
        self.time_windows.append(time_window)
    
    def remove_time_window(self, index: int) -> bool:
        """Remove a time window by index."""
        if 0 <= index < len(self.time_windows):
            del self.time_windows[index]
            return True
        return False
    
    def get_next_run_time(self) -> Optional[str]:
        """Get the next scheduled run time."""
        from datetime import datetime, timedelta
        import pytz
        
        if not self.enabled or self.use_group_settings:
            return None
        
        try:
            tz = pytz.timezone(self.timezone)
            current_datetime = datetime.now(tz)
            
            # Look for next active time window in the next 7 days
            for days_ahead in range(7):
                check_date = current_datetime + timedelta(days=days_ahead)
                check_weekday = check_date.weekday()
                
                if check_weekday in self.active_weekdays:
                    for time_window in self.time_windows:
                        if time_window.active:
                            start_parts = time_window.start_time.split(':')
                            window_start = check_date.replace(
                                hour=int(start_parts[0]),
                                minute=int(start_parts[1]),
                                second=0,
                                microsecond=0
                            )
                            
                            # If this window is in the future, return it
                            if window_start > current_datetime:
                                return window_start.isoformat()
            
            return None
            
        except Exception:
            return None

@dataclass
class PeriodicAlertConfig:
    """Configuration for periodic alerts on a symbol."""
    enabled: bool = False
    alert_interval: int = 15  # minutes
    alert_weekdays: List[int] = None  # 0=Monday, 6=Sunday
    alert_hours: List[int] = None  # 24-hour format, None means all hours
    conditions: Dict[str, Any] = None  # Alert conditions
    last_triggered: Optional[str] = None
    alert_count: int = 0
    
    def __post_init__(self):
        if self.alert_weekdays is None:
            self.alert_weekdays = [0, 1, 2, 3, 4]  # Weekdays only
        if self.alert_hours is None:
            self.alert_hours = list(range(9, 17))  # Trading hours 9 AM - 5 PM
        if self.conditions is None:
            self.conditions = {
                "rsi_overbought": True,
                "rsi_oversold": True,
                "macd_bullish_crossover": True,
                "macd_bearish_crossover": True,
                "price_above_sma20": False,
                "price_below_sma20": False,
                "volume_spike": False
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PeriodicAlertConfig':
        """Create from dictionary."""
        return cls(**data)

@dataclass
class SymbolConfig:
    """Configuration for a single symbol within a group."""
    symbol: str
    asset_type: str  # forex, stocks, crypto, indices
    timeframe: str   # 1m, 5m, 15m, 30m, 1h, 4h, 1d, etc.
    period: str      # 1d, 5d, 1mo, 3mo, 6mo, 1y, etc.
    data_source: str = "yfinance"
    enabled: bool = True
    indicator_settings: Optional[IndicatorSettings] = None
    periodic_alerts: Optional[PeriodicAlertConfig] = None
    symbol_scheduler_settings: Optional[SymbolSchedulerSettings] = None
    trading_session: Optional[Dict[str, Any]] = None
    risk_management: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.indicator_settings is None:
            self.indicator_settings = IndicatorSettings()
        if self.periodic_alerts is None:
            self.periodic_alerts = PeriodicAlertConfig()
        if self.symbol_scheduler_settings is None:
            self.symbol_scheduler_settings = SymbolSchedulerSettings()
        if self.trading_session is None:
            self.trading_session = {
                "timezone": "UTC",
                "market_hours": {"start": "09:00", "end": "17:00"},
                "enable_after_hours": False
            }
        if self.risk_management is None:
            self.risk_management = {
                "max_position_size": 1.0,
                "stop_loss_pct": 2.0,
                "take_profit_pct": 6.0,
                "risk_reward_ratio": 3.0
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "symbol": self.symbol,
            "asset_type": self.asset_type,
            "timeframe": self.timeframe,
            "period": self.period,
            "data_source": self.data_source,
            "enabled": self.enabled,
            "indicator_settings": self.indicator_settings.to_dict() if self.indicator_settings else None,
            "periodic_alerts": self.periodic_alerts.to_dict() if self.periodic_alerts else None,
            "symbol_scheduler_settings": self.symbol_scheduler_settings.to_dict() if self.symbol_scheduler_settings else None,
            "trading_session": self.trading_session,
            "risk_management": self.risk_management
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SymbolConfig':
        """Create from dictionary."""
        indicator_settings = None
        if data.get("indicator_settings"):
            indicator_settings = IndicatorSettings.from_dict(data["indicator_settings"])
        
        periodic_alerts = None
        if data.get("periodic_alerts"):
            periodic_alerts = PeriodicAlertConfig.from_dict(data["periodic_alerts"])
        
        symbol_scheduler_settings = None
        if data.get("symbol_scheduler_settings"):
            symbol_scheduler_settings = SymbolSchedulerSettings.from_dict(data["symbol_scheduler_settings"])
        
        return cls(
            symbol=data["symbol"],
            asset_type=data["asset_type"],
            timeframe=data["timeframe"],
            period=data["period"],
            data_source=data.get("data_source", "yfinance"),
            enabled=data.get("enabled", True),
            indicator_settings=indicator_settings,
            periodic_alerts=periodic_alerts,
            symbol_scheduler_settings=symbol_scheduler_settings,
            trading_session=data.get("trading_session"),
            risk_management=data.get("risk_management")
        )

@dataclass
class GroupLevelSettings:
    """Group-level settings that can be inherited by symbols."""
    default_indicator_settings: Optional[IndicatorSettings] = None
    default_periodic_alerts: Optional[PeriodicAlertConfig] = None
    scheduler_settings: Optional[Dict[str, Any]] = None
    notification_settings: Optional[Dict[str, Any]] = None
    auto_analysis: bool = False
    analysis_interval: int = 30  # minutes
    
    def __post_init__(self):
        if self.default_indicator_settings is None:
            self.default_indicator_settings = IndicatorSettings()
        if self.default_periodic_alerts is None:
            self.default_periodic_alerts = PeriodicAlertConfig()
        if self.scheduler_settings is None:
            self.scheduler_settings = {
                "enabled": False,
                "run_interval": 15,  # minutes
                "run_weekdays": [0, 1, 2, 3, 4],
                "run_hours": list(range(9, 17)),
                "timezone": "UTC"
            }
        if self.notification_settings is None:
            self.notification_settings = {
                "email_enabled": False,
                "desktop_notifications": True,
                "sound_alerts": False,
                "log_to_file": True
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "default_indicator_settings": self.default_indicator_settings.to_dict() if self.default_indicator_settings else None,
            "default_periodic_alerts": self.default_periodic_alerts.to_dict() if self.default_periodic_alerts else None,
            "scheduler_settings": self.scheduler_settings,
            "notification_settings": self.notification_settings,
            "auto_analysis": self.auto_analysis,
            "analysis_interval": self.analysis_interval
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GroupLevelSettings':
        """Create from dictionary."""
        default_indicator_settings = None
        if data.get("default_indicator_settings"):
            default_indicator_settings = IndicatorSettings.from_dict(data["default_indicator_settings"])
        
        default_periodic_alerts = None
        if data.get("default_periodic_alerts"):
            default_periodic_alerts = PeriodicAlertConfig.from_dict(data["default_periodic_alerts"])
        
        return cls(
            default_indicator_settings=default_indicator_settings,
            default_periodic_alerts=default_periodic_alerts,
            scheduler_settings=data.get("scheduler_settings"),
            notification_settings=data.get("notification_settings"),
            auto_analysis=data.get("auto_analysis", False),
            analysis_interval=data.get("analysis_interval", 30)
        )

@dataclass
class SymbolGroup:
    """A group of symbols with their configurations."""
    group_id: str
    name: str
    description: str
    symbols: Dict[str, SymbolConfig]
    created_at: str
    updated_at: str
    enabled: bool = True
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    group_settings: Optional[GroupLevelSettings] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
        if self.group_settings is None:
            self.group_settings = GroupLevelSettings()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'group_id': self.group_id,
            'name': self.name,
            'description': self.description,
            'symbols': {k: v.to_dict() for k, v in self.symbols.items()},
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'enabled': self.enabled,
            'tags': self.tags,
            'metadata': self.metadata,
            'group_settings': self.group_settings.to_dict() if self.group_settings else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SymbolGroup':
        """Create from dictionary."""
        symbols = {k: SymbolConfig.from_dict(v) for k, v in data['symbols'].items()}
        
        group_settings = None
        if data.get('group_settings'):
            group_settings = GroupLevelSettings.from_dict(data['group_settings'])
        
        return cls(
            group_id=data['group_id'],
            name=data['name'],
            description=data['description'],
            symbols=symbols,
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            enabled=data.get('enabled', True),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {}),
            group_settings=group_settings
        )
    
    def add_symbol(self, symbol_key: str, config: SymbolConfig) -> None:
        """Add a symbol to the group."""
        self.symbols[symbol_key] = config
        self.updated_at = datetime.now().isoformat()
    
    def remove_symbol(self, symbol_key: str) -> bool:
        """Remove a symbol from the group."""
        if symbol_key in self.symbols:
            del self.symbols[symbol_key]
            self.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def update_symbol(self, symbol_key: str, config: SymbolConfig) -> bool:
        """Update a symbol's configuration."""
        if symbol_key in self.symbols:
            self.symbols[symbol_key] = config
            self.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def get_enabled_symbols(self) -> Dict[str, SymbolConfig]:
        """Get only enabled symbols."""
        return {k: v for k, v in self.symbols.items() if v.enabled}
    
    def update_symbol_indicator_settings(self, symbol_key: str, indicator_settings: IndicatorSettings) -> bool:
        """Update indicator settings for a specific symbol."""
        if symbol_key in self.symbols:
            self.symbols[symbol_key].indicator_settings = indicator_settings
            self.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def update_symbol_periodic_alerts(self, symbol_key: str, alert_config: PeriodicAlertConfig) -> bool:
        """Update periodic alert configuration for a specific symbol."""
        if symbol_key in self.symbols:
            self.symbols[symbol_key].periodic_alerts = alert_config
            self.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def update_symbol_scheduler_settings(self, symbol_key: str, scheduler_settings: SymbolSchedulerSettings) -> bool:
        """Update scheduler settings for a specific symbol."""
        if symbol_key in self.symbols:
            self.symbols[symbol_key].symbol_scheduler_settings = scheduler_settings
            self.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def get_symbols_with_alerts_enabled(self) -> Dict[str, SymbolConfig]:
        """Get symbols that have periodic alerts enabled."""
        return {
            k: v for k, v in self.symbols.items() 
            if v.enabled and v.periodic_alerts and v.periodic_alerts.enabled
        }
    
    def enable_group_scheduler(self, run_interval: int = 15, weekdays: List[int] = None, hours: List[int] = None) -> None:
        """Enable scheduler for the entire group."""
        if weekdays is None:
            weekdays = [0, 1, 2, 3, 4]  # Weekdays
        if hours is None:
            hours = list(range(9, 17))  # Trading hours
        
        self.group_settings.scheduler_settings.update({
            "enabled": True,
            "run_interval": run_interval,
            "run_weekdays": weekdays,
            "run_hours": hours
        })
        self.updated_at = datetime.now().isoformat()
    
    def disable_group_scheduler(self) -> None:
        """Disable scheduler for the entire group."""
        self.group_settings.scheduler_settings["enabled"] = False
        self.updated_at = datetime.now().isoformat()
    
    def set_first_time_periodic_alerts_for_symbol(self, symbol_key: str, 
                                                  interval: int = 15,
                                                  conditions: Dict[str, Any] = None) -> bool:
        """Set up periodic alerts for a symbol during first-time setup."""
        if symbol_key not in self.symbols:
            return False
        
        if conditions is None:
            conditions = {
                "rsi_overbought": True,
                "rsi_oversold": True,
                "macd_bullish_crossover": True,
                "macd_bearish_crossover": True
            }
        
        alert_config = PeriodicAlertConfig(
            enabled=True,
            alert_interval=interval,
            conditions=conditions
        )
        
        self.symbols[symbol_key].periodic_alerts = alert_config
        self.updated_at = datetime.now().isoformat()
        return True
    
    def apply_group_settings_to_symbol(self, symbol_key: str, override_existing: bool = False) -> bool:
        """Apply group-level settings to a specific symbol."""
        if symbol_key not in self.symbols:
            return False
        
        symbol = self.symbols[symbol_key]
        
        # Apply group indicator settings if symbol doesn't have custom ones or override is requested
        if not symbol.indicator_settings or override_existing:
            symbol.indicator_settings = IndicatorSettings.from_dict(
                self.group_settings.default_indicator_settings.to_dict()
            )
        
        # Apply group periodic alert settings if symbol doesn't have custom ones or override is requested
        if not symbol.periodic_alerts or override_existing:
            symbol.periodic_alerts = PeriodicAlertConfig.from_dict(
                self.group_settings.default_periodic_alerts.to_dict()
            )
        
        self.updated_at = datetime.now().isoformat()
        return True
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a summary of the group's analysis configuration."""
        enabled_symbols = len(self.get_enabled_symbols())
        alert_enabled_symbols = len(self.get_symbols_with_alerts_enabled())
        
        return {
            "group_id": self.group_id,
            "name": self.name,
            "total_symbols": len(self.symbols),
            "enabled_symbols": enabled_symbols,
            "alert_enabled_symbols": alert_enabled_symbols,
            "scheduler_enabled": self.group_settings.scheduler_settings.get("enabled", False),
            "auto_analysis_enabled": self.group_settings.auto_analysis,
            "analysis_interval": self.group_settings.analysis_interval
        }

class SymbolGroupManager:
    """Manager class for CRUD operations on symbol groups."""
    
    def __init__(self, storage_path: str = "symbol_groups"):
        self.storage_path = storage_path
        self.groups_file = os.path.join(storage_path, "groups.json")
        self._ensure_storage_directory()
        self._groups_cache: Dict[str, SymbolGroup] = {}
        self._load_all_groups()
    
    def _ensure_storage_directory(self) -> None:
        """Ensure storage directory exists."""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
    
    def _load_all_groups(self) -> None:
        """Load all groups from storage."""
        if os.path.exists(self.groups_file):
            try:
                with open(self.groups_file, 'r') as f:
                    data = json.load(f)
                    for group_data in data.get('groups', []):
                        group = SymbolGroup.from_dict(group_data)
                        self._groups_cache[group.group_id] = group
            except Exception as e:
                print(f"Error loading groups: {str(e)}")
                self._groups_cache = {}
    
    def _save_all_groups(self) -> bool:
        """Save all groups to storage."""
        try:
            data = {
                'groups': [group.to_dict() for group in self._groups_cache.values()],
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(self.groups_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving groups: {str(e)}")
            return False
    
    def create_group(self, 
                    name: str, 
                    description: str = "", 
                    group_id: str = None) -> SymbolGroup:
        """Create a new symbol group."""
        if group_id is None:
            group_id = str(uuid.uuid4())[:8]  # Short UUID
        
        if group_id in self._groups_cache:
            raise ValueError(f"Group with ID '{group_id}' already exists")
        
        now = datetime.now().isoformat()
        group = SymbolGroup(
            group_id=group_id,
            name=name,
            description=description,
            symbols={},
            created_at=now,
            updated_at=now
        )
        
        self._groups_cache[group_id] = group
        self._save_all_groups()
        return group
    
    def save_group(self, group: SymbolGroup) -> bool:
        """Save an existing group to storage."""
        try:
            group.updated_at = datetime.now().isoformat()
            self._groups_cache[group.group_id] = group
            return self._save_all_groups()
        except Exception as e:
            print(f"Error saving group {group.group_id}: {str(e)}")
            return False
    
    def get_group(self, group_id: str) -> Optional[SymbolGroup]:
        """Get a group by ID."""
        return self._groups_cache.get(group_id)
    
    def list_groups(self, enabled_only: bool = False) -> List[SymbolGroup]:
        """List all groups."""
        groups = list(self._groups_cache.values())
        if enabled_only:
            groups = [g for g in groups if g.enabled]
        return groups
    
    def update_group(self, group_id: str, **kwargs) -> bool:
        """Update group metadata."""
        group = self._groups_cache.get(group_id)
        if not group:
            return False
        
        for key, value in kwargs.items():
            if hasattr(group, key):
                setattr(group, key, value)
        
        group.updated_at = datetime.now().isoformat()
        self._save_all_groups()
        return True
    
    def delete_group(self, group_id: str) -> bool:
        """Delete a group."""
        if group_id in self._groups_cache:
            del self._groups_cache[group_id]
            self._save_all_groups()
            return True
        return False
    
    def add_symbol_to_group(self, 
                           group_id: str, 
                           symbol_key: str, 
                           symbol: str,
                           asset_type: str,
                           timeframe: str,
                           period: str,
                           data_source: str = "yfinance",
                           enabled: bool = True) -> bool:
        """Add a symbol to a group."""
        group = self._groups_cache.get(group_id)
        if not group:
            return False
        
        config = SymbolConfig(
            symbol=symbol,
            asset_type=asset_type,
            timeframe=timeframe,
            period=period,
            data_source=data_source,
            enabled=enabled
        )
        
        group.add_symbol(symbol_key, config)
        self._save_all_groups()
        return True
    
    def configure_symbol_indicators(self, group_id: str, symbol_key: str, 
                                  indicator_settings: IndicatorSettings) -> bool:
        """Configure indicator settings for a specific symbol."""
        group = self._groups_cache.get(group_id)
        if not group:
            return False
        
        result = group.update_symbol_indicator_settings(symbol_key, indicator_settings)
        if result:
            self._save_all_groups()
        return result
    
    def configure_symbol_periodic_alerts(self, group_id: str, symbol_key: str,
                                        alert_config: PeriodicAlertConfig) -> bool:
        """Configure periodic alerts for a specific symbol."""
        group = self._groups_cache.get(group_id)
        if not group:
            return False
        
        result = group.update_symbol_periodic_alerts(symbol_key, alert_config)
        if result:
            self._save_all_groups()
        return result
    
    def configure_symbol_scheduler_settings(self, group_id: str, symbol_key: str,
                                          scheduler_settings: SymbolSchedulerSettings) -> bool:
        """Configure scheduler settings for a specific symbol."""
        group = self._groups_cache.get(group_id)
        if not group:
            return False
        
        result = group.update_symbol_scheduler_settings(symbol_key, scheduler_settings)
        if result:
            self._save_all_groups()
        return result
    
    def setup_first_time_alerts(self, group_id: str, symbol_key: str,
                               interval: int = 15, conditions: Dict[str, Any] = None) -> bool:
        """Set up periodic alerts for a symbol during first-time configuration."""
        group = self._groups_cache.get(group_id)
        if not group:
            return False
        
        result = group.set_first_time_periodic_alerts_for_symbol(symbol_key, interval, conditions)
        if result:
            self._save_all_groups()
        return result
    
    def configure_group_scheduler(self, group_id: str, enabled: bool,
                                 run_interval: int = 15, weekdays: List[int] = None,
                                 hours: List[int] = None) -> bool:
        """Configure scheduler settings for a group."""
        group = self._groups_cache.get(group_id)
        if not group:
            return False
        
        if enabled:
            group.enable_group_scheduler(run_interval, weekdays, hours)
        else:
            group.disable_group_scheduler()
        
        self._save_all_groups()
        return True
    
    def get_groups_with_alerts(self) -> List[SymbolGroup]:
        """Get all groups that have symbols with periodic alerts enabled."""
        groups_with_alerts = []
        for group in self._groups_cache.values():
            if group.enabled and group.get_symbols_with_alerts_enabled():
                groups_with_alerts.append(group)
        return groups_with_alerts
    
    def get_groups_with_scheduler(self) -> List[SymbolGroup]:
        """Get all groups that have scheduler enabled."""
        return [
            group for group in self._groups_cache.values()
            if group.enabled and group.group_settings.scheduler_settings.get("enabled", False)
        ]
    
    def apply_group_defaults_to_symbol(self, group_id: str, symbol_key: str,
                                     override_existing: bool = False) -> bool:
        """Apply group-level default settings to a specific symbol."""
        group = self._groups_cache.get(group_id)
        if not group:
            return False
        
        result = group.apply_group_settings_to_symbol(symbol_key, override_existing)
        if result:
            self._save_all_groups()
        return result
    
    def get_analysis_overview(self) -> Dict[str, Any]:
        """Get a comprehensive overview of all groups and their analysis configuration."""
        groups = list(self._groups_cache.values())
        
        total_symbols = sum(len(group.symbols) for group in groups)
        enabled_symbols = sum(len(group.get_enabled_symbols()) for group in groups)
        alert_symbols = sum(len(group.get_symbols_with_alerts_enabled()) for group in groups)
        scheduler_groups = len(self.get_groups_with_scheduler())
        
        return {
            "total_groups": len(groups),
            "enabled_groups": len([g for g in groups if g.enabled]),
            "total_symbols": total_symbols,
            "enabled_symbols": enabled_symbols,
            "alert_enabled_symbols": alert_symbols,
            "scheduler_enabled_groups": scheduler_groups,
            "groups_overview": [group.get_analysis_summary() for group in groups if group.enabled]
        }
    
    def remove_symbol_from_group(self, group_id: str, symbol_key: str) -> bool:
        """Remove a symbol from a group."""
        group = self._groups_cache.get(group_id)
        if not group:
            return False
        
        success = group.remove_symbol(symbol_key)
        if success:
            self._save_all_groups()
        return success
    
    def update_symbol_in_group(self, 
                              group_id: str, 
                              symbol_key: str, 
                              **kwargs) -> bool:
        """Update a symbol's configuration in a group."""
        group = self._groups_cache.get(group_id)
        if not group or symbol_key not in group.symbols:
            return False
        
        config = group.symbols[symbol_key]
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        group.updated_at = datetime.now().isoformat()
        self._save_all_groups()
        return True
    
    def export_group(self, group_id: str, filename: str = None) -> str:
        """Export a group to a JSON file."""
        group = self._groups_cache.get(group_id)
        if not group:
            raise ValueError(f"Group '{group_id}' not found")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"group_{group_id}_{timestamp}.json"
        
        filepath = os.path.join(self.storage_path, filename)
        with open(filepath, 'w') as f:
            json.dump(group.to_dict(), f, indent=2)
        
        return filepath
    
    def import_group(self, filepath: str, new_group_id: str = None) -> SymbolGroup:
        """Import a group from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if new_group_id:
            data['group_id'] = new_group_id
            data['created_at'] = datetime.now().isoformat()
            data['updated_at'] = datetime.now().isoformat()
        
        group = SymbolGroup.from_dict(data)
        
        if group.group_id in self._groups_cache:
            raise ValueError(f"Group with ID '{group.group_id}' already exists")
        
        self._groups_cache[group.group_id] = group
        self._save_all_groups()
        return group
    
    def get_group_summary(self, group_id: str) -> Dict[str, Any]:
        """Get a summary of a group."""
        group = self._groups_cache.get(group_id)
        if not group:
            return {}
        
        enabled_symbols = group.get_enabled_symbols()
        asset_types = {}
        timeframes = {}
        data_sources = {}
        
        for config in enabled_symbols.values():
            asset_types[config.asset_type] = asset_types.get(config.asset_type, 0) + 1
            timeframes[config.timeframe] = timeframes.get(config.timeframe, 0) + 1
            data_sources[config.data_source] = data_sources.get(config.data_source, 0) + 1
        
        return {
            'group_id': group.group_id,
            'name': group.name,
            'description': group.description,
            'total_symbols': len(group.symbols),
            'enabled_symbols': len(enabled_symbols),
            'asset_types': asset_types,
            'timeframes': timeframes,
            'data_sources': data_sources,
            'created_at': group.created_at,
            'updated_at': group.updated_at,
            'enabled': group.enabled
        }

# Predefined group templates
class GroupTemplates:
    """Predefined symbol group templates."""
    
    @staticmethod
    def create_forex_major_pairs() -> Dict[str, SymbolConfig]:
        """Create major forex pairs configuration."""
        pairs = {
            'eurusd': SymbolConfig('eurusd', 'forex', '1h', '7d'),
            'gbpusd': SymbolConfig('gbpusd', 'forex', '1h', '7d'),
            'usdjpy': SymbolConfig('usdjpy', 'forex', '1h', '7d'),
            'usdchf': SymbolConfig('usdchf', 'forex', '1h', '7d'),
            'audusd': SymbolConfig('audusd', 'forex', '1h', '7d'),
            'usdcad': SymbolConfig('usdcad', 'forex', '1h', '7d'),
            'nzdusd': SymbolConfig('nzdusd', 'forex', '1h', '7d')
        }
        return pairs
    
    @staticmethod
    def create_tech_stocks() -> Dict[str, SymbolConfig]:
        """Create tech stocks configuration."""
        stocks = {
            'aapl': SymbolConfig('AAPL', 'stocks', '30m', '5d'),
            'msft': SymbolConfig('MSFT', 'stocks', '30m', '5d'),
            'googl': SymbolConfig('GOOGL', 'stocks', '30m', '5d'),
            'amzn': SymbolConfig('AMZN', 'stocks', '30m', '5d'),
            'tsla': SymbolConfig('TSLA', 'stocks', '30m', '5d'),
            'meta': SymbolConfig('META', 'stocks', '30m', '5d'),
            'nvda': SymbolConfig('NVDA', 'stocks', '30m', '5d')
        }
        return stocks
    
    @staticmethod
    def create_crypto_portfolio() -> Dict[str, SymbolConfig]:
        """Create crypto portfolio configuration."""
        cryptos = {
            'btc': SymbolConfig('btc', 'crypto', '15m', '3d'),
            'eth': SymbolConfig('eth', 'crypto', '15m', '3d'),
            'bnb': SymbolConfig('bnb', 'crypto', '15m', '3d'),
            'sol': SymbolConfig('sol', 'crypto', '15m', '3d'),
            'ada': SymbolConfig('ada', 'crypto', '15m', '3d'),
            'doge': SymbolConfig('doge', 'crypto', '15m', '3d')
        }
        return cryptos
    
    @staticmethod
    def create_indices_portfolio() -> Dict[str, SymbolConfig]:
        """Create indices portfolio configuration."""
        indices = {
            'us30': SymbolConfig('us30', 'indices', '30m', '7d'),
            'sp500': SymbolConfig('sp500', 'indices', '30m', '7d'),
            'nas100': SymbolConfig('nas100', 'indices', '30m', '7d'),
            'dax': SymbolConfig('dax', 'indices', '30m', '7d'),
            'ftse100': SymbolConfig('ftse100', 'indices', '30m', '7d'),
            'nikkei': SymbolConfig('nikkei', 'indices', '30m', '7d')
        }
        return indices
    
    @staticmethod
    def create_mixed_portfolio() -> Dict[str, SymbolConfig]:
        """Create a mixed asset portfolio."""
        mixed = {
            'eurusd': SymbolConfig('eurusd', 'forex', '1h', '7d'),
            'aapl': SymbolConfig('AAPL', 'stocks', '30m', '5d'),
            'btc': SymbolConfig('btc', 'crypto', '15m', '3d'),
            'us30': SymbolConfig('us30', 'indices', '30m', '7d'),
            'gold': SymbolConfig('GC=F', 'commodities', '1h', '7d'),
            'oil': SymbolConfig('CL=F', 'commodities', '1h', '7d')
        }
        return mixed

def create_predefined_groups(manager: SymbolGroupManager) -> List[str]:
    """Create predefined symbol groups."""
    groups_created = []
    
    templates = [
        ('forex_majors', 'Major Forex Pairs', 'Major currency pairs with 1h timeframe', 
         GroupTemplates.create_forex_major_pairs()),
        ('tech_stocks', 'Technology Stocks', 'Major tech stocks with 30m timeframe', 
         GroupTemplates.create_tech_stocks()),
        ('crypto_top', 'Top Cryptocurrencies', 'Top crypto assets with 15m timeframe', 
         GroupTemplates.create_crypto_portfolio()),
        ('global_indices', 'Global Market Indices', 'Major global indices with 30m timeframe', 
         GroupTemplates.create_indices_portfolio()),
        ('mixed_portfolio', 'Mixed Asset Portfolio', 'Diversified portfolio across asset classes', 
         GroupTemplates.create_mixed_portfolio())
    ]
    
    for group_id, name, description, symbols in templates:
        try:
            # Check if group already exists
            if manager.get_group(group_id):
                print(f"Group '{group_id}' already exists, skipping...")
                continue
            
            group = manager.create_group(name, description, group_id)
            
            # Add symbols to group
            for symbol_key, config in symbols.items():
                manager.add_symbol_to_group(
                    group_id, symbol_key, config.symbol, config.asset_type,
                    config.timeframe, config.period, config.data_source, config.enabled
                )
            
            groups_created.append(group_id)
            print(f"Created group: {group_id} with {len(symbols)} symbols")
            
        except Exception as e:
            print(f"Error creating group {group_id}: {str(e)}")
    
    return groups_created

# Utility functions
def print_group_summary(manager: SymbolGroupManager, group_id: str) -> None:
    """Print a formatted summary of a group."""
    summary = manager.get_group_summary(group_id)
    if not summary:
        print(f"Group '{group_id}' not found")
        return
    
    print(f"\n{'='*60}")
    print(f"GROUP SUMMARY: {summary['name']} ({summary['group_id']})")
    print(f"{'='*60}")
    print(f"Description: {summary['description']}")
    print(f"Total Symbols: {summary['total_symbols']}")
    print(f"Enabled Symbols: {summary['enabled_symbols']}")
    print(f"Created: {summary['created_at']}")
    print(f"Updated: {summary['updated_at']}")
    print(f"Status: {'Enabled' if summary['enabled'] else 'Disabled'}")
    
    print(f"\nAsset Types:")
    for asset_type, count in summary['asset_types'].items():
        print(f"  {asset_type}: {count}")
    
    print(f"\nTimeframes:")
    for timeframe, count in summary['timeframes'].items():
        print(f"  {timeframe}: {count}")
    
    print(f"\nData Sources:")
    for source, count in summary['data_sources'].items():
        print(f"  {source}: {count}")

def print_all_groups(manager: SymbolGroupManager) -> None:
    """Print a summary of all groups."""
    groups = manager.list_groups()
    
    print(f"\n{'='*80}")
    print(f"ALL SYMBOL GROUPS ({len(groups)} total)")
    print(f"{'='*80}")
    
    if not groups:
        print("No groups found.")
        return
    
    for group in groups:
        enabled_symbols = len(group.get_enabled_symbols())
        status = "✅" if group.enabled else "❌"
        print(f"{status} {group.group_id:<15} | {group.name:<25} | {enabled_symbols:>3} symbols | {group.updated_at[:10]}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize manager
    manager = SymbolGroupManager()
    
    # Create predefined groups
    print("Creating predefined symbol groups...")
    created_groups = create_predefined_groups(manager)
    
    # Display all groups
    print_all_groups(manager)
    
    # Show detailed summary for one group
    if created_groups:
        print_group_summary(manager, created_groups[0])
    
    print(f"\n{'='*60}")
    print("SYMBOL GROUPS SYSTEM READY")
    print(f"{'='*60}")
    print("Use SymbolGroupManager to:")
    print("- Create custom groups")
    print("- Add/remove symbols")
    print("- Export/import groups")
    print("- Run analysis on groups")
