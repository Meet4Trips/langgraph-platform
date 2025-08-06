#!/usr/bin/env python3
"""
Comprehensive examples of environment variable handling in Python
"""

import os
from dotenv import load_dotenv


def example_1_basic_dotenv():
    """Example 1: Basic .env file loading"""
    print("=== Example 1: Basic .env file loading ===")
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Access environment variables
    api_key = os.getenv("GPLACES_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    print(f"Google Places API Key: {api_key[:10] if api_key else 'Not set'}...")
    print(f"OpenAI API Key: {openai_key[:10] if openai_key else 'Not set'}...")


def example_2_dotenv_with_default():
    """Example 2: .env with default values"""
    print("\n=== Example 2: .env with default values ===")
    
    load_dotenv()
    
    # Get with default value if not found
    api_key = os.getenv("GPLACES_API_KEY", "default_key")
    non_existent = os.getenv("NON_EXISTENT_KEY", "default_value")
    
    print(f"API Key: {api_key[:10] if api_key != 'default_key' else 'default_key'}...")
    print(f"Non-existent key: {non_existent}")


def example_3_conditional_loading():
    """Example 3: Conditional .env loading"""
    print("\n=== Example 3: Conditional .env loading ===")
    
    # Only load .env if it exists
    if os.path.exists(".env"):
        load_dotenv()
        print("Loaded .env file")
    else:
        print("No .env file found")
    
    api_key = os.getenv("GPLACES_API_KEY")
    print(f"API Key available: {bool(api_key)}")


def example_4_environment_specific():
    """Example 4: Environment-specific .env files"""
    print("\n=== Example 4: Environment-specific .env files ===")
    
    # Load different .env files based on environment
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        load_dotenv(".env.production")
        print("Loaded production environment")
    elif environment == "testing":
        load_dotenv(".env.testing")
        print("Loaded testing environment")
    else:
        load_dotenv(".env")
        print("Loaded development environment")
    
    api_key = os.getenv("GPLACES_API_KEY")
    print(f"API Key available: {bool(api_key)}")


def example_5_manual_override():
    """Example 5: Manual environment variable override"""
    print("\n=== Example 5: Manual environment variable override ===")
    
    # Set environment variable manually
    os.environ["CUSTOM_API_KEY"] = "manual_key_123"
    
    # Load .env (won't override manually set variables)
    load_dotenv(override=False)
    
    custom_key = os.getenv("CUSTOM_API_KEY")
    print(f"Custom API Key: {custom_key}")


def example_6_validation():
    """Example 6: Environment variable validation"""
    print("\n=== Example 6: Environment variable validation ===")
    
    load_dotenv()
    
    required_vars = ["GPLACES_API_KEY", "OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Missing required environment variables: {missing_vars}")
        print("Please set these variables in your .env file")
    else:
        print("All required environment variables are set!")


def example_7_safe_access():
    """Example 7: Safe environment variable access"""
    print("\n=== Example 7: Safe environment variable access ===")
    
    load_dotenv()
    
    def get_api_key(service_name):
        """Safely get API key for a service"""
        key = os.getenv(f"{service_name.upper()}_API_KEY")
        if not key:
            raise ValueError(f"Missing {service_name} API key")
        return key
    
    try:
        places_key = get_api_key("gplaces")
        openai_key = get_api_key("openai")
        print("All API keys retrieved successfully")
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    example_1_basic_dotenv()
    example_2_dotenv_with_default()
    example_3_conditional_loading()
    example_4_environment_specific()
    example_5_manual_override()
    example_6_validation()
    example_7_safe_access() 