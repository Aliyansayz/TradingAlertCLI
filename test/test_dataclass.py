#!/usr/bin/env python3
"""
Test to understand dataclass behavior
"""

from dataclasses import dataclass, field
from typing import List, Dict

@dataclass 
class TestClass:
    numbers: List[int] = field(default_factory=lambda: [1, 2, 3])
    names: Dict[str, bool] = field(default=None)
    
    def __post_init__(self):
        print("__post_init__ called!")
        if self.names is None:
            self.names = {"test": True}

def test():
    print("Creating TestClass with explicit parameters...")
    tc1 = TestClass(numbers=[4, 5, 6])
    print(f"tc1.numbers: {tc1.numbers}")
    print(f"tc1.names: {tc1.names}")
    
    print("\nCreating TestClass with no parameters...")
    tc2 = TestClass()
    print(f"tc2.numbers: {tc2.numbers}")
    print(f"tc2.names: {tc2.names}")

if __name__ == "__main__":
    test()
