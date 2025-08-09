"""
Game constants and configuration
"""

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
GREEN = (100, 255, 100)
RED = (255, 100, 100)
YELLOW = (255, 255, 100)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Additional colors for improved visuals
LIGHT_BROWN = (205, 133, 63)
DARK_BROWN = (101, 67, 33)
GRASS_GREEN = (34, 139, 34)
LIGHT_GREEN = (144, 238, 144)
FENCE_BROWN = (160, 82, 45)
KENNEL_GRAY = (169, 169, 169)
ROOF_RED = (178, 34, 34)
CONCRETE = (192, 192, 192)

# Game settings
PLAYER_SPEED = 200  # pixels per second
TRUCK_SPEED = 150   # pixels per second
MAX_CARGO_CAPACITY = 10

# Market settings
MAX_MARKETS = 5
PRICE_FLUCTUATION_RATE = 0.1  # How much prices change per second
DEMAND_CHANGE_RATE = 0.05

# Goods types
GOODS_TYPES = [
    "Bones", "Treats", "Toys", "Food", "Medicine"
]

# Colors for different goods
GOODS_COLORS = {
    "Bones": (245, 245, 220),     # Beige
    "Treats": (210, 180, 140),    # Tan
    "Toys": (255, 20, 147),       # Deep pink
    "Food": (255, 165, 0),        # Orange
    "Medicine": (0, 255, 127)     # Spring green
}

# Time settings (game minutes per real second)
TIME_SCALE = 10
GAME_DAY_LENGTH = 60  # seconds for a full game day
