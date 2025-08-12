"""
Avocavo Python SDK
Nutrition analysis made simple with secure USDA data access
"""

from .client import NutritionAPI, ApiError
from .auth import login, logout, get_current_user, list_api_keys, create_api_key, switch_api_key, switch_to_api_key, delete_api_key, auto_setup_api_key
from .models import (
    Nutrition, 
    USDAMatch, 
    IngredientResult, 
    RecipeResult, 
    BatchResult,
    Account,
    Usage
)

# Version - Fresh start with secure package
__version__ = "1.0.12"
__author__ = "Avocavo"
__email__ = "api-support@avocavo.com"
__description__ = "Avocavo Python SDK - Nutrition analysis made simple"

# Quick access functions
from .client import analyze, analyze_ingredient, analyze_recipe, analyze_batch, get_account_usage

__all__ = [
    # Main client
    'NutritionAPI',
    'ApiError',
    
    # Authentication
    'login',
    'logout', 
    'get_current_user',
    
    # API Key Management
    'list_api_keys',
    'create_api_key',
    'switch_api_key',
    'switch_to_api_key',
    'delete_api_key',
    'auto_setup_api_key',
    
    # Data models
    'Nutrition',
    'USDAMatch',
    'IngredientResult',
    'RecipeResult', 
    'BatchResult',
    'Account',
    'Usage',
    
    # Quick functions
    'analyze',
    'analyze_ingredient',
    'analyze_recipe',
    'analyze_batch',
    'get_account_usage',
    
    # API key management (when using NutritionAPI client)
    # Access via: client.list_api_keys(), client.create_api_key(), etc.
    
    # Package info
    '__version__',
    '__author__',
    '__email__',
    '__description__'
]