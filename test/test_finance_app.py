"""
Test Finance App with detailed error tracking
"""

import sys
import os
import traceback

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont

def test_finance_app():
    print("Creating QApplication...")
    app = QApplication(sys.argv)
    
    try:
        print("Importing backend components...")
        from backend.symbol_groups_manager import SymbolGroupManager
        from backend.group_analysis_engine import GroupAnalysisEngine  
        from backend.trading_cli import IndicatorSettings, PeriodicUnitTester, SchedulerSettings
        from finance_app import AnalysisWorkerThread
        
        print("Creating FinanceApp manually...")
        
        # Create a simple widget first
        window = QWidget()
        window.setWindowTitle("Finance Trade Assistant")
        window.resize(1200, 800)
        
        print("Setting up basic layout...")
        layout = QVBoxLayout(window)
        label = QLabel("Finance Trade Assistant - Loading...")
        label.setFont(QFont("Arial", 20))
        layout.addWidget(label)
        
        print("Initializing backend components...")
        
        manager = SymbolGroupManager()
        print("✓ SymbolGroupManager created")
        
        engine = GroupAnalysisEngine(max_workers=3)
        print("✓ GroupAnalysisEngine created")
        
        indicator_settings = IndicatorSettings()
        print("✓ IndicatorSettings created")
        
        scheduler_settings = SchedulerSettings()
        print("✓ SchedulerSettings created")
        
        unit_tester = PeriodicUnitTester(manager, engine)
        print("✓ PeriodicUnitTester created")
        
        # Analysis results cache
        analysis_results = {}
        
        # Worker thread
        analysis_worker = AnalysisWorkerThread(manager, engine)
        print("✓ AnalysisWorkerThread created")
        
        # Timer for periodic updates
        update_timer = QTimer()
        update_timer.start(30000)  # Update every 30 seconds
        print("✓ QTimer created and started")
        
        print("All components created successfully!")
        
        window.show()
        print("Window shown!")
        
        # Quick test run
        QTimer.singleShot(2000, app.quit)
        app.exec()
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_finance_app()
