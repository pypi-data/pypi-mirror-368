"""
Main game engine that coordinates all game systems
"""

import pygame
import random
from .constants import *
from .entities import Player, Market, Position
from .ui import UI

class GameEngine:
    def draw_tree(self, x, y):
        """Draw a simple tree"""
        # Trunk
        trunk_rect = pygame.Rect(x - 5, y - 10, 10, 20)
        pygame.draw.rect(self.screen, DARK_BROWN, trunk_rect)
        # Leaves (circle)
        pygame.draw.circle(self.screen, GREEN, (x, y - 15), 15)
        pygame.draw.circle(self.screen, DARK_GRAY, (x, y - 15), 15, 2)

    def draw_bush(self, x, y):
        """Draw a small bush"""
        pygame.draw.circle(self.screen, GREEN, (x, y), 8)
        pygame.draw.circle(self.screen, DARK_GRAY, (x, y), 8, 1)
    """Main game engine class"""
    def __init__(self, screen):
        self.screen = screen
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.markets = []
        self.ui = UI(screen)
        
        # Game state
        self.game_time = 0.0  # Game time in seconds
        self.day_number = 1
        
        # Initialize markets
        self.create_markets()
        
    def create_markets(self):
        """Create markets around the game world"""
        market_names = [
            "Doggy Depot", 
            "Paws & Claws Market", 
            "The Bone Zone", 
            "Furry Friends Store", 
            "Capacity Upgrades"  # Upgrade store
        ]
        
        # Create markets at different locations
        market_positions = [
            (200, 150),   # Top left
            (1000, 200),  # Top right  
            (150, 600),   # Bottom left
            (950, 650),   # Bottom right
            (600, 400)    # Center - Upgrade store
        ]
        
        for i, (name, pos) in enumerate(zip(market_names, market_positions)):
            # The last market is the upgrade store
            is_upgrade_store = (i == len(market_names) - 1)
            market = Market(name, Position(pos[0], pos[1]), "upgrade" if is_upgrade_store else "general")
            if is_upgrade_store:
                market.is_upgrade_store = True
            self.markets.append(market)
    
    def handle_event(self, event):
        """Handle game events"""
        self.ui.handle_event(event, self.player, self.markets)
    
    def update(self, dt):
        """Update game state"""
        self.game_time += dt
        
        # Handle player movement
        keys = pygame.key.get_pressed()
        dx = dy = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
        
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707  # 1/sqrt(2)
            dy *= 0.707
        
        self.player.move(dx, dy, dt)
        
        # Update markets
        for market in self.markets:
            market.update(dt)
        
        # Update UI (check for auto-close market info)
        self.ui.update(self.player, self.markets)
        
        # Check for day progression
        if self.game_time > GAME_DAY_LENGTH:
            self.advance_day()
    
    def advance_day(self):
        """Advance to the next day"""
        self.day_number += 1
        self.game_time = 0.0
        
        # Reset market conditions for new day
        for market in self.markets:
            for good in market.goods.values():
                # Add some random stock
                good.quantity += random.randint(1, 5)
                # Reset demand with some variation
                good.demand = random.uniform(0.5, 1.5)
    
    def render(self):
        """Render the game"""
        # Draw improved background
        self.draw_background()
        
        # Draw game entities
        self.ui.draw_markets(self.markets)
        self.ui.draw_player(self.player)
        
        # Draw UI elements
        self.ui.draw_player_info(self.player)
        self.ui.draw_inventory(self.player)
        self.ui.draw_market_info(self.ui.selected_market)
        
        # Draw day counter
        day_text = self.ui.large_font.render(f"Day {self.day_number}", True, BLACK)
        self.screen.blit(day_text, (SCREEN_WIDTH // 2 - 50, 10))
        
        # Draw game time progress bar
        time_progress = self.game_time / GAME_DAY_LENGTH
        bar_width = 200
        bar_rect = pygame.Rect(SCREEN_WIDTH // 2 - bar_width // 2, 50, bar_width, 10)
        pygame.draw.rect(self.screen, WHITE, bar_rect)
        pygame.draw.rect(self.screen, BLACK, bar_rect, 2)
        
        progress_rect = pygame.Rect(bar_rect.x, bar_rect.y, bar_width * time_progress, 10)
        pygame.draw.rect(self.screen, YELLOW, progress_rect)
    
    def draw_background(self):
        """Draw an improved background with varied terrain"""
        # Base grass color
        self.screen.fill(GRASS_GREEN)
        
        # Add some grass texture patches (use fixed seed for consistency)
        random.seed(42)  # Fixed seed for consistent background
        for i in range(50):
            patch_x = random.randint(0, SCREEN_WIDTH)
            patch_y = random.randint(0, SCREEN_HEIGHT)
            patch_size = random.randint(10, 30)
            color_variation = random.randint(-20, 20)
            grass_color = (
                max(0, min(255, LIGHT_GREEN[0] + color_variation)),
                max(0, min(255, LIGHT_GREEN[1] + color_variation)),
                max(0, min(255, LIGHT_GREEN[2] + color_variation))
            )
            pygame.draw.circle(self.screen, grass_color, (patch_x, patch_y), patch_size)
        
        # Reset random seed to current time
        random.seed()
        
        # Draw paths/roads (more natural looking)
        path_color = CONCRETE
        path_edge_color = DARK_GRAY
        
        # Main horizontal paths
        for y in range(100, SCREEN_HEIGHT, 200):
            # Main path
            pygame.draw.rect(self.screen, path_color, (0, y - 15, SCREEN_WIDTH, 30))
            # Path edges
            pygame.draw.rect(self.screen, path_edge_color, (0, y - 15, SCREEN_WIDTH, 3))
            pygame.draw.rect(self.screen, path_edge_color, (0, y + 12, SCREEN_WIDTH, 3))
            
            # Add some path markings (dashed lines)
            for x in range(0, SCREEN_WIDTH, 40):
                pygame.draw.rect(self.screen, YELLOW, (x, y - 2, 20, 4))
        
        # Main vertical paths
        for x in range(150, SCREEN_WIDTH, 200):
            # Main path
            pygame.draw.rect(self.screen, path_color, (x - 15, 0, 30, SCREEN_HEIGHT))
            # Path edges
            pygame.draw.rect(self.screen, path_edge_color, (x - 15, 0, 3, SCREEN_HEIGHT))
            pygame.draw.rect(self.screen, path_edge_color, (x + 12, 0, 3, SCREEN_HEIGHT))
        
        # Add some decorative elements
        self.draw_background_decorations()
    
    def draw_background_decorations(self):
        """Add trees, bushes, and other decorative elements - avoiding roads"""
        # Better positioned decorations that avoid roads
        # Roads are at: horizontal y=100,300,500,700 and vertical x=150,350,550,750,950
        decoration_positions = [
            # Top section (between y=0 and y=85)
            (80, 50), (220, 60), (280, 40), (480, 70), (600, 50), (800, 45), (1000, 65),
            # Between first horizontal road (y=115 to y=285)
            (50, 150), (200, 180), (280, 200), (400, 160), (520, 220), (680, 180), (850, 240), (1100, 200),
            # Between second horizontal road (y=315 to y=485) 
            (80, 350), (250, 400), (420, 380), (600, 450), (780, 420), (950, 380), (1050, 450),
            # Between third horizontal road (y=515 to y=685)
            (100, 550), (300, 600), (450, 580), (650, 620), (850, 600), (1000, 580),
            # Bottom section (y=715+)
            (60, 750), (400, 780), (700, 760), (900, 780)
        ]
        
        for i, (x, y) in enumerate(decoration_positions):
            # Check if position is on a road (add buffer zone)
            on_horizontal_road = any(abs(y - road_y) < 20 for road_y in [100, 300, 500, 700])
            on_vertical_road = any(abs(x - road_x) < 20 for road_x in [150, 350, 550, 750, 950])
            
            # Skip if too close to roads
            if on_horizontal_road or on_vertical_road:
                continue
                
            # Only draw trees and bushes (no fire hydrants)
            if i % 2 == 0:  # Trees
                self.draw_tree(x, y)
            else:  # Bushes
                self.draw_bush(x, y)
    
    def draw_bush(self, x, y):
        """Draw a small bush"""
        pygame.draw.circle(self.screen, GREEN, (x, y), 8)
        pygame.draw.circle(self.screen, DARK_GRAY, (x, y), 8, 1)
