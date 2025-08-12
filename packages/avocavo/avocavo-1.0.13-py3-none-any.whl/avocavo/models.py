"""
Data models for Avocavo Nutrition API responses
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Union


@dataclass
class Nutrition:
    """Complete nutrition information with all 29 USDA nutrition fields"""
    # Primary macronutrients
    calories_total: float = 0.0
    protein_total: float = 0.0
    total_fat_total: float = 0.0
    carbohydrates_total: float = 0.0
    fiber_total: float = 0.0
    sugar_total: float = 0.0
    
    # Fat breakdown
    saturated_fat_total: float = 0.0
    monounsaturated_fat_total: Optional[float] = None
    polyunsaturated_fat_total: Optional[float] = None
    trans_fat_total: Optional[float] = None
    cholesterol_total: float = 0.0  # mg
    
    # Minerals
    sodium_total: float = 0.0  # mg
    calcium_total: float = 0.0  # mg
    iron_total: float = 0.0  # mg
    magnesium_total: Optional[float] = None  # mg
    phosphorus_total: Optional[float] = None  # mg
    potassium_total: Optional[float] = None  # mg
    zinc_total: Optional[float] = None  # mg
    selenium_total: Optional[float] = None  # µg
    
    # Vitamins
    vitamin_a_total: Optional[float] = None  # µg
    vitamin_c_total: Optional[float] = None  # mg
    vitamin_d_iu_total: Optional[float] = None  # IU
    vitamin_e_total: Optional[float] = None  # mg
    vitamin_k_total: Optional[float] = None  # µg
    thiamin_total: Optional[float] = None  # mg (B1)
    riboflavin_total: Optional[float] = None  # mg (B2)
    niacin_total: Optional[float] = None  # mg (B3)
    vitamin_b6_total: Optional[float] = None  # mg
    vitamin_b12_total: Optional[float] = None  # µg
    folate_total: Optional[float] = None  # µg
    
    @property
    def calories(self) -> float:
        """Alias for calories_total"""
        return self.calories_total
    
    @property
    def protein(self) -> float:
        """Alias for protein_total"""
        return self.protein_total
    
    @property
    def fat(self) -> float:
        """Alias for total_fat_total"""
        return self.total_fat_total
    
    @property
    def carbs(self) -> float:
        """Alias for carbohydrates_total"""
        return self.carbohydrates_total
    
    # Additional convenience properties
    @property
    def saturated_fat(self) -> float:
        """Alias for saturated_fat_total"""
        return self.saturated_fat_total
    
    @property
    def sodium(self) -> float:
        """Alias for sodium_total"""
        return self.sodium_total
    
    @property
    def fiber(self) -> float:
        """Alias for fiber_total"""
        return self.fiber_total
    
    @property
    def sugar(self) -> float:
        """Alias for sugar_total"""
        return self.sugar_total
    
    @property
    def calcium(self) -> float:
        """Alias for calcium_total"""
        return self.calcium_total
    
    @property
    def iron(self) -> float:
        """Alias for iron_total"""
        return self.iron_total
    
    def get_non_null_nutrients(self) -> Dict[str, float]:
        """Get dictionary of all non-null nutrients"""
        nutrients = {}
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            if value is not None:
                # Remove _total suffix for cleaner display
                display_name = field_name.replace('_total', '')
                nutrients[display_name] = value
        return nutrients
    
    def count_null_nutrients(self) -> int:
        """Count how many nutrients are null/unavailable"""
        null_count = 0
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            if value is None:
                null_count += 1
        return null_count


@dataclass
class USDAMatch:
    """USDA FoodData Central match information"""
    fdc_id: int
    description: str
    data_type: str  # Foundation, SR Legacy, Survey (FNDDS), branded_food
    
    @property
    def verification_url(self) -> str:
        """Get USDA verification URL"""
        return f"https://fdc.nal.usda.gov/fdc-app.html#/food-details/{self.fdc_id}/nutrients"
    
    @property
    def is_high_quality(self) -> bool:
        """Check if this is a high-quality data source"""
        return self.data_type in ['Foundation', 'SR Legacy', 'Survey (FNDDS)']


@dataclass
class IngredientResult:
    """Single ingredient analysis result"""
    success: bool
    ingredient: str
    processing_time_ms: float
    from_cache: bool = False
    nutrition: Optional[Nutrition] = None
    usda_match: Optional[USDAMatch] = None
    verification_url: Optional[str] = None
    verification_method: str = ""
    cache_type: Optional[str] = None
    method_used: Optional[str] = None
    portion_source: Optional[str] = None  # Parsing tier information
    estimated_grams: Optional[float] = None
    ingredient_name: Optional[str] = None
    error: Optional[str] = None
    
    @property
    def calories(self) -> float:
        """Quick access to calories"""
        return self.nutrition.calories_total if self.nutrition else 0.0
    
    @property
    def has_nutrition_data(self) -> bool:
        """Check if nutrition data is available"""
        return self.nutrition is not None and self.nutrition.calories_total > 0


@dataclass
class RecipeIngredient:
    """Individual ingredient in a recipe with nutrition"""
    ingredient: str
    nutrition: Nutrition
    usda_match: Optional[USDAMatch] = None
    verification_url: Optional[str] = None
    success: bool = True


@dataclass
class RecipeNutrition:
    """Complete recipe nutrition breakdown"""
    total: Nutrition
    per_serving: Nutrition
    ingredients: List[RecipeIngredient]
    
    @property
    def ingredient_count(self) -> int:
        """Number of ingredients analyzed"""
        return len(self.ingredients)
    
    @property
    def successful_ingredients(self) -> int:
        """Number of ingredients with nutrition data"""
        return sum(1 for ing in self.ingredients if ing.success)


@dataclass
class RecipeResult:
    """Complete recipe analysis result"""
    success: bool
    recipe: Dict  # Original recipe info (ingredients, servings)
    nutrition: Optional[RecipeNutrition] = None
    processing_time_ms: float = 0.0
    usda_matches: int = 0
    error: Optional[str] = None
    
    @property
    def servings(self) -> int:
        """Number of servings in recipe"""
        return self.recipe.get('servings', 1)
    
    @property
    def calories_per_serving(self) -> float:
        """Quick access to calories per serving"""
        return self.nutrition.per_serving.calories_total if self.nutrition else 0.0
    
    @property
    def nutrition_per_serving(self) -> Optional['Nutrition']:
        """Backwards compatibility property for per-serving nutrition"""
        return self.nutrition.per_serving if self.nutrition else None
    
    @property
    def nutrition_total(self) -> Optional['Nutrition']:
        """Quick access to total nutrition"""
        return self.nutrition.total if self.nutrition else None


@dataclass
class BatchResult:
    """Batch processing result"""
    success: bool
    batch_size: int
    successful_matches: int
    results: List[IngredientResult]
    processing_time_ms: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Success rate as percentage"""
        return (self.successful_matches / self.batch_size * 100) if self.batch_size > 0 else 0.0
    
    @property
    def total_calories(self) -> float:
        """Total calories across all ingredients"""
        return sum(r.calories for r in self.results if r.success)


@dataclass
class Usage:
    """API usage information"""
    current_month: int
    monthly_limit: Optional[int]  # None = unlimited
    remaining: Union[int, str]
    percentage_used: float
    reset_date: str
    days_until_reset: int
    
    @property
    def is_unlimited(self) -> bool:
        """Check if plan has unlimited usage"""
        return self.monthly_limit is None
    
    @property
    def is_near_limit(self) -> bool:
        """Check if usage is near monthly limit (>80%)"""
        return self.percentage_used > 80.0


@dataclass
class PlanFeatures:
    """Available features for a plan"""
    batch_processing: bool = False
    max_batch_size: int = 1
    priority_support: bool = False
    analytics_dashboard: bool = False
    webhook_notifications: bool = False
    custom_integrations: bool = False


@dataclass
class Account:
    """Account information"""
    email: str
    api_tier: str
    subscription_status: str
    usage: Usage
    features: Optional[PlanFeatures] = None
    
    @property
    def plan_name(self) -> str:
        """Formatted plan name"""
        return self.api_tier.title()
    
    @property
    def is_trial(self) -> bool:
        """Check if account is on trial"""
        return self.api_tier.lower() == 'trial'
    
    @property
    def is_paid_plan(self) -> bool:
        """Check if account has a paid subscription"""
        return self.api_tier.lower() in ['starter', 'professional', 'enterprise']


@dataclass
class APIFeature:
    """API feature description"""
    name: str
    description: str
    available_in: List[str]  # List of tiers where available
    example: Optional[str] = None


# Available API features
AVAILABLE_FEATURES = [
    APIFeature(
        name="Ingredient Analysis",
        description="Get complete nutrition data for any recipe ingredient",
        available_in=["developer", "trial", "starter", "professional", "enterprise"],
        example="av.analyze_ingredient('2 cups chocolate chips')"
    ),
    APIFeature(
        name="Recipe Analysis", 
        description="Analyze complete recipes with per-serving calculations",
        available_in=["developer", "trial", "starter", "professional", "enterprise"],
        example="av.analyze_recipe(['2 cups flour', '1 cup milk'], servings=8)"
    ),
    APIFeature(
        name="USDA Verification",
        description="Real FDC IDs and verification URLs from USDA FoodData Central",
        available_in=["developer", "trial", "starter", "professional", "enterprise"]
    ),
    APIFeature(
        name="Smart Caching",
        description="Intelligent caching system for improved performance",
        available_in=["developer", "trial", "starter", "professional", "enterprise"]
    ),
    APIFeature(
        name="Batch Processing",
        description="Analyze multiple ingredients efficiently in one request",
        available_in=["trial", "starter", "professional", "enterprise"],
        example="av.analyze_batch(['1 cup rice', '2 tbsp oil'])"
    ),
    APIFeature(
        name="Priority Support",
        description="Priority email support with dedicated assistance",
        available_in=["professional", "enterprise"]
    ),
    APIFeature(
        name="Analytics Dashboard",
        description="Detailed usage analytics and performance metrics",
        available_in=["starter", "professional", "enterprise"]
    ),
    APIFeature(
        name="Webhook Notifications",
        description="Real-time notifications for usage limits and updates",
        available_in=["professional", "enterprise"]
    ),
    APIFeature(
        name="Custom Integrations",
        description="Custom API endpoints and white-label options",
        available_in=["enterprise"]
    )
]


def get_features_for_tier(tier: str) -> List[APIFeature]:
    """Get available features for a specific tier"""
    return [feature for feature in AVAILABLE_FEATURES if tier.lower() in feature.available_in]


def is_feature_available(tier: str, feature_name: str) -> bool:
    """Check if a feature is available for a tier"""
    tier_features = get_features_for_tier(tier)
    return any(f.name == feature_name for f in tier_features)