#!/usr/bin/env python3
"""
Examples of different ways to test the main function pattern
"""

import asyncio
import os
from dotenv import load_dotenv
from lib.google_places_client import text_search_restaurants

# Load environment variables from .env file
load_dotenv()


def test_direct_execution():
    """Example 1: Direct execution test"""
    print("=== Testing Direct Execution ===")
    
    # This simulates what happens when you run the file directly
    if __name__ == "__main__":
        print("This would run when the file is executed directly")
    
    print("This always runs")


def test_function_call():
    """Example 2: Testing the function directly"""
    print("\n=== Testing Function Call ===")
    
    async def test_restaurant_search():
        try:
            # Test with different parameters
            result1 = await text_search_restaurants("Barcelona", "spanish")
            print(f"Result 1: {type(result1)}")
            
            result2 = await text_search_restaurants("Paris", "french")
            print(f"Result 2: {type(result2)}")
            
        except Exception as e:
            print(f"Expected error (no API key): {e}")
    
    asyncio.run(test_restaurant_search())


def test_environment_setup():
    """Example 3: Testing with environment setup"""
    print("\n=== Testing Environment Setup ===")
    
    # Check if API key is set
    api_key = os.getenv("GPLACES_API_KEY")
    if api_key:
        print(f"API key is set: {api_key[:10]}...")
    else:
        print("API key not set. Set it with: export GPLACES_API_KEY='your_key_here'")


def test_main_function_pattern():
    """Example 4: Demonstrating the main function pattern"""
    print("\n=== Main Function Pattern ===")
    
    def main():
        print("This is the main function")
        return "success"
    
    # This is the standard pattern
    if __name__ == "__main__":
        result = main()
        print(f"Main function returned: {result}")
    else:
        print("This module was imported, not run directly")


if __name__ == "__main__":
    test_direct_execution()
    test_function_call()
    test_environment_setup()
    test_main_function_pattern() 