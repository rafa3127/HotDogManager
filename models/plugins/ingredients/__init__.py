"""
Ingredient plugins package.

Importing this package auto-registers all ingredient methods and validators.

Author: Rafael Correa
Date: November 13, 2025
"""

# Import base first (registers Ingredient validator)
from . import ingredient_base_plugin

# Then import specific plugins
from . import pan_plugin
from . import salchicha_plugin
from . import topping_plugin
from . import salsa_plugin
from . import acompañante_plugin
