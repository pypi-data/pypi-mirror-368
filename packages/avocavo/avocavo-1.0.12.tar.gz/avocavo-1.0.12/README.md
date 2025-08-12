# 🥑 Avocavo Python SDK

> Nutrition analysis made simple. Get accurate USDA nutrition data with secure authentication.

## 🚀 Quick Start

```python
import avocavo

# Login to your account (OAuth flow)
avocavo.login()

# Analyze a single ingredient
result = avocavo.analyze("1 cup brown rice")
print(f"Calories: {result.nutrition.calories}")

# Analyze a recipe
recipe = avocavo.analyze_recipe([
    "2 large eggs",
    "1 cup all-purpose flour", 
    "1/2 cup milk"
])
print(f"Total calories: {recipe.total_nutrition.calories}")
```

## 📦 Installation

```bash
pip install avocavo
```

**Requirements:**
- Python >= 3.8
- Internet connection for API access

## 🔐 Authentication

1. **Sign up** at [nutrition.avocavo.app](https://nutrition.avocavo.app)
2. **Login** via Python:
   ```python
   import avocavo
   avocavo.login()  # Opens browser for secure OAuth
   ```
3. Your credentials are stored securely in your system keyring

## 📖 Basic Usage

### Single Ingredient Analysis
```python
import avocavo

# Simple ingredient analysis
result = avocavo.analyze("1 cup quinoa, cooked")

print(f"Calories: {result.nutrition.calories}")
print(f"Protein: {result.nutrition.protein}g")
print(f"Fiber: {result.nutrition.fiber}g")

# Access USDA match information
print(f"USDA Food: {result.usda_match.description}")
print(f"Confidence: {result.usda_match.confidence_score}")
```

### Recipe Analysis
```python
# Analyze a complete recipe
ingredients = [
    "2 cups rolled oats",
    "1 banana, mashed", 
    "1/2 cup blueberries",
    "1 cup almond milk"
]

recipe = avocavo.analyze_recipe(ingredients)

# Get totals
print(f"Total Calories: {recipe.total_nutrition.calories}")
print(f"Total Protein: {recipe.total_nutrition.protein}g")

# Get per-serving (if servings specified)
print(f"Per Serving: {recipe.per_serving_nutrition.calories} calories")

# Individual ingredient breakdown
for ingredient in recipe.ingredients:
    print(f"{ingredient.original_input}: {ingredient.nutrition.calories} cal")
```

### Batch Analysis
```python
# Analyze multiple ingredients efficiently
ingredients = [
    "1 cup rice",
    "100g chicken breast",
    "1 medium apple",
    "2 tbsp olive oil"
]

results = avocavo.analyze_batch(ingredients)

for result in results:
    print(f"{result.original_input}: {result.nutrition.calories} calories")
```

## 🔧 Advanced Usage

### Using the Client Class
```python
from avocavo import NutritionAPI

# Initialize client (uses stored credentials)
client = NutritionAPI()

# Analyze with additional options
result = client.analyze_ingredient(
    "1 cup rice", 
    include_sub_nutrients=True,
    portion_precision="high"
)

# Get detailed nutrition breakdown
nutrients = result.nutrition.detailed_nutrients
for nutrient in nutrients:
    print(f"{nutrient.name}: {nutrient.amount}{nutrient.unit}")
```

### Account Management
```python
import avocavo

# Check your usage
usage = avocavo.get_account_usage()
print(f"Requests used: {usage.requests_used}/{usage.requests_limit}")

# Get current user info
user = avocavo.get_current_user()
print(f"Logged in as: {user.email}")

# Manage API keys
api_keys = avocavo.list_api_keys()
for key in api_keys:
    print(f"Key: {key.name} (Created: {key.created_at})")
```

## 🔒 Security Features

- **🔐 Secure Authentication**: OAuth flow with system keyring storage
- **🛡️ SSL Verification**: All API calls use verified HTTPS connections  
- **🔑 No Hardcoded Secrets**: Credentials stored securely, never in code
- **🚫 Input Sanitization**: All inputs properly validated and sanitized

## 📊 Data Models

### Nutrition Object
```python
nutrition = result.nutrition

# Macronutrients
print(nutrition.calories)      # kcal
print(nutrition.protein)       # grams
print(nutrition.carbs)         # grams  
print(nutrition.fat)           # grams
print(nutrition.fiber)         # grams

# Micronutrients
print(nutrition.sodium)        # mg
print(nutrition.calcium)       # mg
print(nutrition.iron)          # mg
print(nutrition.vitamin_c)     # mg
```

### USDA Match Information
```python
match = result.usda_match

print(match.fdc_id)           # USDA FDC ID
print(match.description)      # Food description
print(match.confidence_score) # Match confidence (0-1)
print(match.data_type)        # SR Legacy, Foundation, etc.
```

## 🚨 Error Handling

```python
from avocavo import ApiError

try:
    result = avocavo.analyze("invalid ingredient")
except ApiError as e:
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
    
    if e.status_code == 401:
        print("Authentication required - run avocavo.login()")
    elif e.status_code == 429:
        print("Rate limit exceeded - upgrade your plan")
```

## 📚 Examples

### Meal Planning
```python
import avocavo

# Plan a day of meals
breakfast = avocavo.analyze_recipe([
    "2 eggs, scrambled",
    "1 slice whole wheat toast",
    "1/2 avocado"
])

lunch = avocavo.analyze_recipe([
    "4 oz grilled chicken",
    "1 cup quinoa",
    "1 cup steamed broccoli"
])

dinner = avocavo.analyze_recipe([
    "6 oz salmon fillet",
    "1 cup brown rice", 
    "1 cup roasted vegetables"
])

# Calculate daily totals
daily_calories = (breakfast.total_nutrition.calories + 
                 lunch.total_nutrition.calories + 
                 dinner.total_nutrition.calories)

print(f"Daily Total: {daily_calories} calories")
```

### Recipe Scaling
```python
# Original recipe for 4 servings
original = avocavo.analyze_recipe([
    "2 cups flour",
    "4 eggs",
    "1 cup milk"
], servings=4)

# Scale to 8 servings (double)
scale_factor = 8 / 4

scaled_ingredients = []
for ingredient in original.ingredients:
    # Extract amount and scale (simplified example)
    scaled_amount = ingredient.parsed_amount * scale_factor
    scaled_ingredients.append(f"{scaled_amount} {ingredient.parsed_unit} {ingredient.parsed_food}")

scaled_recipe = avocavo.analyze_recipe(scaled_ingredients, servings=8)
```

## 🆘 Support

- **Documentation**: [nutrition.avocavo.app/docs/python](https://nutrition.avocavo.app/docs/python)
- **API Dashboard**: [nutrition.avocavo.app](https://nutrition.avocavo.app)
- **Issues**: [GitHub Issues](https://github.com/avocavo/avocavo-python/issues)
- **Email**: api-support@avocavo.com

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🔄 Migrating from avocavo-nutrition?

The old package has been deprecated due to security vulnerabilities. Migration is straightforward:

```bash
# Remove old package
pip uninstall avocavo-nutrition

# Install new secure package
pip install avocavo
```

**Code changes:**
```python
# OLD (deprecated)
import avocavo_nutrition as av
av.login()

# NEW (secure)
import avocavo
avocavo.login()
```

All functionality remains the same - only the import and security have been improved!