"""
User interface components
"""

import pygame
from .constants import *

class UI:
    """Main UI manager"""
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.large_font = pygame.font.Font(None, 36)
        
        # UI state
        self.show_inventory = False
        self.show_market_info = False
        self.selected_market = None
        self.trade_mode = False
        self.selected_good = None
        self.trade_quantity = 1
    
    def draw_player_info(self, player):
        """Draw player information panel"""
        # Money
        money_text = self.font.render(f"Money: ${player.money:.2f}", True, BLACK)
        self.screen.blit(money_text, (10, 10))
        
        # Cargo capacity
        cargo_text = self.font.render(
            f"Cargo: {player.get_total_cargo()}/{player.max_cargo_capacity}", 
            True, BLACK
        )
        self.screen.blit(cargo_text, (10, 35))
        
        # Instructions with background panel for better readability
        instructions = [
            "WASD: Move (roads only)",
            "E: Toggle Inventory", 
            "R: Interact with Market",
            "ESC: Close menus",
            "In Trade: B=Buy, T=Sell",
            "Hold SHIFT/CTRL for MAX"
        ]
        
        # Create a semi-transparent background for instructions
        instruction_panel = pygame.Rect(5, SCREEN_HEIGHT - 115, 250, 105)
        instruction_surface = pygame.Surface((instruction_panel.width, instruction_panel.height))
        instruction_surface.set_alpha(200)  # Semi-transparent
        instruction_surface.fill(WHITE)
        self.screen.blit(instruction_surface, instruction_panel)
        pygame.draw.rect(self.screen, BLACK, instruction_panel, 1)
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, BLACK)
            self.screen.blit(text, (10, SCREEN_HEIGHT - 110 + i * 15))
    
    def draw_inventory(self, player):
        """Draw inventory panel with detailed information"""
        if not self.show_inventory:
            return
            
        # Background panel (made wider for more details)
        panel_rect = pygame.Rect(SCREEN_WIDTH - 320, 10, 310, 400)
        pygame.draw.rect(self.screen, WHITE, panel_rect)
        pygame.draw.rect(self.screen, BLACK, panel_rect, 2)
        
        # Title
        title = self.font.render("Inventory", True, BLACK)
        self.screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))
        
        # Cargo summary
        total_cargo = player.get_total_cargo()
        cargo_summary = self.small_font.render(
            f"Total Items: {total_cargo}/{player.max_cargo_capacity}", True, BLACK
        )
        self.screen.blit(cargo_summary, (panel_rect.x + 10, panel_rect.y + 35))
        
        # Headers
        headers = self.small_font.render("Item | Qty | Value Est.", True, DARK_GRAY)
        self.screen.blit(headers, (panel_rect.x + 10, panel_rect.y + 55))
        
        # Goods list with detailed info
        y_offset = 75
        total_value = 0
        
        for good_type in GOODS_TYPES:
            quantity = player.inventory[good_type]
            color = GOODS_COLORS[good_type]
            
            # Color indicator (larger)
            color_rect = pygame.Rect(panel_rect.x + 10, panel_rect.y + y_offset, 25, 20)
            pygame.draw.rect(self.screen, color, color_rect)
            pygame.draw.rect(self.screen, BLACK, color_rect, 1)
            
            # Good name and quantity
            name_text = self.small_font.render(f"{good_type[:8]}", True, BLACK)
            self.screen.blit(name_text, (panel_rect.x + 40, panel_rect.y + y_offset))
            
            # Quantity with bar indicator
            qty_text = self.small_font.render(f"{quantity:2d}", True, BLACK)
            self.screen.blit(qty_text, (panel_rect.x + 130, panel_rect.y + y_offset))
            
            # Quantity bar (visual indicator)
            if quantity > 0:
                bar_width = min(40, quantity * 4)
                bar_rect = pygame.Rect(panel_rect.x + 155, panel_rect.y + y_offset + 5, bar_width, 10)
                pygame.draw.rect(self.screen, color, bar_rect)
                pygame.draw.rect(self.screen, BLACK, bar_rect, 1)
            
            # Estimated value (base price estimate)
            base_prices = {"Bones": 12, "Treats": 15, "Toys": 20, "Food": 18, "Medicine": 25}
            estimated_value = quantity * base_prices.get(good_type, 15)
            total_value += estimated_value
            
            value_text = self.small_font.render(f"${estimated_value:3.0f}", True, DARK_GRAY)
            self.screen.blit(value_text, (panel_rect.x + 210, panel_rect.y + y_offset))
            
            y_offset += 30
        
        # Total estimated value
        pygame.draw.line(self.screen, BLACK, 
                        (panel_rect.x + 10, panel_rect.y + y_offset), 
                        (panel_rect.x + 280, panel_rect.y + y_offset), 2)
        y_offset += 10
        
        total_text = self.font.render(f"Est. Total Value: ${total_value:.0f}", True, BLACK)
        self.screen.blit(total_text, (panel_rect.x + 10, panel_rect.y + y_offset))
        
        # Capacity warning
        if total_cargo >= player.max_cargo_capacity * 0.8:  # 80% full
            warning_color = RED if total_cargo >= player.max_cargo_capacity else YELLOW
            warning_text = self.small_font.render("⚠ Inventory Nearly Full!" if total_cargo < player.max_cargo_capacity else "⚠ Inventory FULL!", True, warning_color)
            self.screen.blit(warning_text, (panel_rect.x + 10, panel_rect.y + y_offset + 25))
    
    def draw_market_info(self, market):
        """Draw market information panel"""
        if not self.show_market_info or not market:
            return
        
        # Check if this is an upgrade store
        if hasattr(market, 'is_upgrade_store') and market.is_upgrade_store:
            self.draw_upgrade_store_info(market)
            return
            
        # Background panel
        panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 50, 400, 400)
        pygame.draw.rect(self.screen, WHITE, panel_rect)
        pygame.draw.rect(self.screen, BLACK, panel_rect, 2)
        
        # Title
        title = self.font.render(f"{market.name}", True, BLACK)
        self.screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))
        
        # Market money
        money_text = self.small_font.render(f"Market Money: ${market.money:.2f}", True, BLACK)
        self.screen.blit(money_text, (panel_rect.x + 10, panel_rect.y + 35))
        
        # Goods header
        headers = self.small_font.render("Good | Qty | Price | Demand", True, BLACK)
        self.screen.blit(headers, (panel_rect.x + 10, panel_rect.y + 60))
        
        # Goods list
        y_offset = 85
        for good_type in GOODS_TYPES:
            good = market.goods[good_type]
            color = GOODS_COLORS[good_type]
            
            # Color indicator
            color_rect = pygame.Rect(panel_rect.x + 10, panel_rect.y + y_offset, 15, 15)
            pygame.draw.rect(self.screen, color, color_rect)
            pygame.draw.rect(self.screen, BLACK, color_rect, 1)
            
            # Good info
            demand_indicator = "High" if good.demand > 1.2 else "Med" if good.demand > 0.8 else "Low"
            text = self.small_font.render(
                f"{good_type[:4]} | {good.quantity:2d} | ${good.current_price:5.2f} | {demand_indicator}", 
                True, BLACK
            )
            self.screen.blit(text, (panel_rect.x + 30, panel_rect.y + y_offset))
            
            y_offset += 20
        
        # Trading interface
        if self.trade_mode:
            self.draw_trade_interface(panel_rect, market)
    
    def draw_upgrade_store_info(self, market):
        """Draw upgrade store information panel"""
        # Background panel
        panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 50, 400, 300)
        pygame.draw.rect(self.screen, (255, 248, 220), panel_rect)  # Light yellow background
        pygame.draw.rect(self.screen, BLACK, panel_rect, 3)
        
        # Get player reference
        player = self.ui_player_ref if hasattr(self, 'ui_player_ref') else None
        if not player:
            return
        
        # Title
        title = self.font.render(f"🔧 {market.name} 🔧", True, BLACK)
        self.screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))
        
        # Current capacity info
        capacity_text = self.small_font.render(f"Current Cargo Capacity: {player.max_cargo_capacity} items", True, BLACK)
        self.screen.blit(capacity_text, (panel_rect.x + 10, panel_rect.y + 45))
        
        upgrades_text = self.small_font.render(f"Upgrades Purchased: {player.capacity_upgrades}", True, BLACK)
        self.screen.blit(upgrades_text, (panel_rect.x + 10, panel_rect.y + 65))
        
        # Upgrade cost and button
        upgrade_cost = player.get_upgrade_cost()
        cost_text = self.small_font.render(f"Next Upgrade Cost: ${upgrade_cost}", True, BLACK)
        self.screen.blit(cost_text, (panel_rect.x + 10, panel_rect.y + 100))
        
        # Check if player can afford upgrade
        can_afford = player.can_afford_upgrade()
        
        # Draw upgrade button
        button_rect = pygame.Rect(panel_rect.x + 10, panel_rect.y + 130, 200, 40)
        button_color = GREEN if can_afford else GRAY
        text_color = BLACK if can_afford else WHITE
        
        pygame.draw.rect(self.screen, button_color, button_rect)
        pygame.draw.rect(self.screen, BLACK, button_rect, 2)
        
        button_text = "Press U to Upgrade!" if can_afford else "Not Enough Money"
        button_render = self.small_font.render(button_text, True, text_color)
        
        # Center text in button
        text_rect = button_render.get_rect(center=button_rect.center)
        self.screen.blit(button_render, text_rect)
        
        # Benefits description
        benefit_text = self.small_font.render("Upgrade Benefits:", True, BLACK)
        self.screen.blit(benefit_text, (panel_rect.x + 10, panel_rect.y + 190))
        
        benefit_desc = self.small_font.render("• +1 cargo capacity per upgrade", True, BLACK)
        self.screen.blit(benefit_desc, (panel_rect.x + 20, panel_rect.y + 210))
        
        benefit_desc2 = self.small_font.render("• Carry more goods = more profit!", True, BLACK)
        self.screen.blit(benefit_desc2, (panel_rect.x + 20, panel_rect.y + 230))
        
        # Instructions
        instructions = [
            "R - Exit Store",
            "U - Buy Upgrade (if affordable)"
        ]
        
        y_pos = panel_rect.y + 260
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, BLACK)
            self.screen.blit(inst_text, (panel_rect.x + 10, y_pos))
            y_pos += 16
    
    def calculate_max_buy(self, player, market, good_type):
        """Calculate maximum quantity player can buy"""
        if good_type not in market.goods:
            return 0
        
        good = market.goods[good_type]
        price_per_unit = good.current_price
        
        # Constraints:
        # 1. Player's money
        max_by_money = int(player.money / price_per_unit) if price_per_unit > 0 else 0
        
        # 2. Market's stock
        max_by_stock = good.quantity
        
        # 3. Player's cargo capacity
        max_by_capacity = player.max_cargo_capacity - player.get_total_cargo()
        
        # Return the minimum of all constraints
        return min(max_by_money, max_by_stock, max_by_capacity)
    
    def draw_trade_interface(self, panel_rect, market):
        """Draw trading interface within market panel"""
        trade_y = panel_rect.y + 250
        
        # Trade mode indicator (split into two lines for readability)
        mode_text1 = self.small_font.render("TRADE MODE - Select good with 1-5, +/- quantity", True, RED)
        mode_text2 = self.small_font.render("B to buy, T to sell | Hold SHIFT/CTRL for MAX", True, RED)
        self.screen.blit(mode_text1, (panel_rect.x + 10, trade_y))
        self.screen.blit(mode_text2, (panel_rect.x + 10, trade_y + 15))
        
        if self.selected_good:
            good = market.goods[self.selected_good]
            
            # Selected good info
            selected_text = self.small_font.render(
                f"Selected: {self.selected_good} (Qty: {self.trade_quantity})", 
                True, BLACK
            )
            self.screen.blit(selected_text, (panel_rect.x + 10, trade_y + 35))
            
            # Cost/Revenue calculation
            total_cost = good.current_price * self.trade_quantity
            cost_text = self.small_font.render(f"Total: ${total_cost:.2f}", True, BLACK)
            self.screen.blit(cost_text, (panel_rect.x + 10, trade_y + 55))
            
            # Show max quantities available
            max_buy = self.calculate_max_buy(self.ui_player_ref, market, self.selected_good) if hasattr(self, 'ui_player_ref') else 0
            max_sell = self.ui_player_ref.inventory[self.selected_good] if hasattr(self, 'ui_player_ref') else 0
            
            max_text = self.small_font.render(f"Max Buy: {max_buy} | Max Sell: {max_sell}", True, DARK_GRAY)
            self.screen.blit(max_text, (panel_rect.x + 10, trade_y + 75))
    
    def draw_markets(self, markets):
        """Draw market locations on the map as dog kennels/facilities"""
        for i, market in enumerate(markets):
            x, y = int(market.position.x), int(market.position.y)
            
            # Check if this is an upgrade store
            if hasattr(market, 'is_upgrade_store') and market.is_upgrade_store:
                self.draw_upgrade_store(x, y, market.name)
                continue
            
            # Different kennel styles for variety
            kennel_style = i % 3
            
            if kennel_style == 0:  # Traditional kennel with fence
                self.draw_fenced_kennel(x, y, market.name)
            elif kennel_style == 1:  # Barn-style building
                self.draw_barn_kennel(x, y, market.name)
            else:  # Modern clinic style
                self.draw_clinic_kennel(x, y, market.name)
    
    def draw_fenced_kennel(self, x, y, name):
        """Draw a traditional fenced kennel"""
        # Main building (kennel house)
        house_rect = pygame.Rect(x - 20, y - 20, 40, 30)
        pygame.draw.rect(self.screen, LIGHT_BROWN, house_rect)
        pygame.draw.rect(self.screen, DARK_BROWN, house_rect, 2)
        
        # Roof (triangle)
        roof_points = [(x - 22, y - 20), (x, y - 35), (x + 22, y - 20)]
        pygame.draw.polygon(self.screen, ROOF_RED, roof_points)
        pygame.draw.polygon(self.screen, BLACK, roof_points, 2)
        
        # Door
        door_rect = pygame.Rect(x - 8, y - 5, 16, 15)
        pygame.draw.rect(self.screen, DARK_BROWN, door_rect)
        
        # Fence around kennel
        fence_rect = pygame.Rect(x - 35, y - 35, 70, 60)
        pygame.draw.rect(self.screen, FENCE_BROWN, fence_rect, 3)
        
        # Fence posts
        for fx in range(x - 35, x + 40, 15):
            pygame.draw.rect(self.screen, DARK_BROWN, (fx - 2, y - 35, 4, 60))
        
        # Name plate
        name_text = self.small_font.render(name, True, BLACK)
        text_rect = name_text.get_rect(center=(x, y + 45))
        # Add a nice background with shadow effect
        shadow_rect = text_rect.inflate(8, 4)
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(self.screen, DARK_GRAY, shadow_rect)
        pygame.draw.rect(self.screen, WHITE, text_rect.inflate(8, 4))
        pygame.draw.rect(self.screen, BLACK, text_rect.inflate(8, 4), 1)
        self.screen.blit(name_text, text_rect)
    
    def draw_barn_kennel(self, x, y, name):
        """Draw a barn-style kennel"""
        # Main barn structure
        barn_rect = pygame.Rect(x - 30, y - 25, 60, 40)
        pygame.draw.rect(self.screen, FENCE_BROWN, barn_rect)
        pygame.draw.rect(self.screen, BLACK, barn_rect, 2)
        
        # Barn roof (curved top)
        roof_rect = pygame.Rect(x - 32, y - 30, 64, 20)
        pygame.draw.ellipse(self.screen, ROOF_RED, roof_rect)
        pygame.draw.ellipse(self.screen, BLACK, roof_rect, 2)
        
        # Barn doors (double doors)
        left_door = pygame.Rect(x - 20, y - 10, 18, 25)
        right_door = pygame.Rect(x + 2, y - 10, 18, 25)
        pygame.draw.rect(self.screen, DARK_BROWN, left_door)
        pygame.draw.rect(self.screen, DARK_BROWN, right_door)
        pygame.draw.rect(self.screen, BLACK, left_door, 2)
        pygame.draw.rect(self.screen, BLACK, right_door, 2)
        
        # Door handles
        pygame.draw.circle(self.screen, BLACK, (x - 5, y + 2), 2)
        pygame.draw.circle(self.screen, BLACK, (x + 5, y + 2), 2)
        
        # Name sign
        name_text = self.small_font.render(name, True, WHITE)
        text_rect = name_text.get_rect(center=(x, y + 35))
        # Wooden sign background with shadow
        sign_background = text_rect.inflate(10, 6)
        shadow_rect = sign_background.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(self.screen, BLACK, shadow_rect)
        pygame.draw.rect(self.screen, DARK_BROWN, sign_background)
        pygame.draw.rect(self.screen, BROWN, sign_background, 2)
        self.screen.blit(name_text, text_rect)
    
    def draw_clinic_kennel(self, x, y, name):
        """Draw a modern veterinary clinic style kennel"""
        # Main building
        clinic_rect = pygame.Rect(x - 25, y - 20, 50, 35)
        pygame.draw.rect(self.screen, KENNEL_GRAY, clinic_rect)
        pygame.draw.rect(self.screen, BLACK, clinic_rect, 2)
        
        # Flat modern roof
        roof_rect = pygame.Rect(x - 27, y - 25, 54, 8)
        pygame.draw.rect(self.screen, DARK_GRAY, roof_rect)
        pygame.draw.rect(self.screen, BLACK, roof_rect, 1)
        
        # Glass door/window
        glass_rect = pygame.Rect(x - 15, y - 15, 30, 25)
        pygame.draw.rect(self.screen, BLUE, glass_rect)
        pygame.draw.rect(self.screen, BLACK, glass_rect, 2)
        
        # Cross symbol (medical)
        cross_v = pygame.Rect(x - 2, y - 10, 4, 15)
        cross_h = pygame.Rect(x - 8, y - 4, 16, 4)
        pygame.draw.rect(self.screen, RED, cross_v)
        pygame.draw.rect(self.screen, RED, cross_h)
        
        # Name sign (modern style)
        name_text = self.small_font.render(name, True, BLACK)
        text_rect = name_text.get_rect(center=(x, y + 30))
        # Modern sign with shadow
        sign_background = text_rect.inflate(8, 4)
        shadow_rect = sign_background.copy()
        shadow_rect.x += 1
        shadow_rect.y += 1
        pygame.draw.rect(self.screen, GRAY, shadow_rect)
        pygame.draw.rect(self.screen, WHITE, sign_background)
        pygame.draw.rect(self.screen, BLACK, sign_background, 2)
        self.screen.blit(name_text, text_rect)
    
    def draw_upgrade_store(self, x, y, name):
        """Draw an upgrade store as a garage/workshop"""
        # Main garage building (larger than regular kennels)
        garage_rect = pygame.Rect(x - 35, y - 30, 70, 50)
        pygame.draw.rect(self.screen, CONCRETE, garage_rect)
        pygame.draw.rect(self.screen, BLACK, garage_rect, 3)
        
        # Garage door (metal rolling door texture)
        door_rect = pygame.Rect(x - 25, y - 10, 50, 35)
        pygame.draw.rect(self.screen, GRAY, door_rect)
        pygame.draw.rect(self.screen, BLACK, door_rect, 2)
        
        # Horizontal lines on garage door for texture
        for i in range(4):
            line_y = door_rect.y + 8 + i * 7
            pygame.draw.line(self.screen, DARK_GRAY, 
                           (door_rect.x, line_y), (door_rect.x + door_rect.width, line_y), 1)
        
        # Tool symbols on the walls
        # Wrench symbol (left side)
        wrench_rect = pygame.Rect(x - 30, y - 25, 8, 15)
        pygame.draw.rect(self.screen, YELLOW, wrench_rect)
        pygame.draw.circle(self.screen, YELLOW, (x - 26, y - 20), 3)
        
        # Hammer symbol (right side)
        hammer_handle = pygame.Rect(x + 22, y - 25, 3, 15)
        hammer_head = pygame.Rect(x + 20, y - 25, 8, 5)
        pygame.draw.rect(self.screen, BROWN, hammer_handle)
        pygame.draw.rect(self.screen, GRAY, hammer_head)
        
        # "Shoppe" sign (made even larger and more prominent)
        sign_rect = pygame.Rect(x - 40, y - 55, 80, 20)
        pygame.draw.rect(self.screen, YELLOW, sign_rect)
        pygame.draw.rect(self.screen, BLACK, sign_rect, 2)
        
        upgrade_text = self.small_font.render("Shoppe", True, BLACK)  # Changed from "UPGRADES" to "Shoppe"
        text_rect = upgrade_text.get_rect(center=sign_rect.center)
        self.screen.blit(upgrade_text, text_rect)
        
        # Name plate below
        name_text = self.small_font.render(name, True, BLACK)
        name_rect = name_text.get_rect(center=(x, y + 40))
        # Garage-style sign with shadow
        sign_background = name_rect.inflate(10, 6)
        shadow_rect = sign_background.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(self.screen, BLACK, shadow_rect)
        pygame.draw.rect(self.screen, YELLOW, sign_background)
        pygame.draw.rect(self.screen, BLACK, sign_background, 2)
        self.screen.blit(name_text, name_rect)
    
    def draw_player(self, player):
        """Draw the Boston Terrier player matching the reference image exactly"""
        # Position
        x, y = int(player.position.x), int(player.position.y)
        size = player.size
        
        # Body (main oval) - Brown/tan base color like the reference
        body_radius = size // 2
        body_width = body_radius + 2
        body_height = body_radius - 1
        body_rect = pygame.Rect(x - body_width, y - body_height, body_width * 2, body_height * 2)
        
        # Draw body in brown (like reference image)
        brown_color = (101, 67, 33)  # Dark brown like reference
        pygame.draw.ellipse(self.screen, brown_color, body_rect)
        
        # White chest/belly marking (prominent like in reference)
        chest_width = body_width - 2
        chest_height = body_height + 2
        chest_rect = pygame.Rect(x - chest_width//2, y - chest_height//4, chest_width, chest_height)
        pygame.draw.ellipse(self.screen, WHITE, chest_rect)
        
        # Green collar/harness (like in the reference image)
        collar_rect = pygame.Rect(x - body_width + 3, y - body_height//2, (body_width * 2) - 6, 6)
        pygame.draw.rect(self.screen, (76, 175, 80), collar_rect)  # Green like reference
        pygame.draw.rect(self.screen, (56, 142, 60), collar_rect, 1)  # Darker green border
        
        # Head (larger and positioned like reference) - Brown base
        head_x = x
        head_y = y - size // 3 - 2
        head_radius = size // 3 + 3
        pygame.draw.circle(self.screen, brown_color, (head_x, head_y), head_radius)
        
        # White face blaze (distinctive Boston Terrier marking like reference)
        blaze_points = [
            (head_x, head_y - head_radius + 4),  # Top point
            (head_x - head_radius//2 + 2, head_y + head_radius//2),  # Bottom left
            (head_x + head_radius//2 - 2, head_y + head_radius//2)   # Bottom right
        ]
        pygame.draw.polygon(self.screen, WHITE, blaze_points)
        
        # White muzzle area (like reference)
        muzzle_rect = pygame.Rect(head_x - head_radius//2 + 2, head_y + 1, head_radius - 4, head_radius//2 + 1)
        pygame.draw.ellipse(self.screen, WHITE, muzzle_rect)
        
        # Eyes (large and round like reference image)
        eye_size = 4
        left_eye = (head_x - 7, head_y - 4)
        right_eye = (head_x + 7, head_y - 4)
        
        # White eye background
        pygame.draw.circle(self.screen, WHITE, left_eye, eye_size + 1)
        pygame.draw.circle(self.screen, WHITE, right_eye, eye_size + 1)
        
        # Black pupils
        pygame.draw.circle(self.screen, BLACK, left_eye, eye_size - 1)
        pygame.draw.circle(self.screen, BLACK, right_eye, eye_size - 1)
        
        # White eye highlights
        pygame.draw.circle(self.screen, WHITE, (left_eye[0] - 1, left_eye[1] - 1), 1)
        pygame.draw.circle(self.screen, WHITE, (right_eye[0] - 1, right_eye[1] - 1), 1)
        
        # Ears (Boston Terrier style - upright triangular, brown like reference)
        left_ear_points = [
            (head_x - 12, head_y - 10),
            (head_x - 16, head_y - 18),
            (head_x - 8, head_y - 14)
        ]
        right_ear_points = [
            (head_x + 12, head_y - 10),
            (head_x + 16, head_y - 18),
            (head_x + 8, head_y - 14)
        ]
        pygame.draw.polygon(self.screen, brown_color, left_ear_points)
        pygame.draw.polygon(self.screen, brown_color, right_ear_points)
        
        # Pink inner ears (smaller and more subtle)
        left_inner_ear = [
            (head_x - 11, head_y - 11),
            (head_x - 14, head_y - 16),
            (head_x - 9, head_y - 13)
        ]
        right_inner_ear = [
            (head_x + 11, head_y - 11),
            (head_x + 14, head_y - 16),
            (head_x + 9, head_y - 13)
        ]
        pygame.draw.polygon(self.screen, (255, 192, 203), left_inner_ear)
        pygame.draw.polygon(self.screen, (255, 192, 203), right_inner_ear)
        
        # Black nose (small and round like reference)
        nose_rect = pygame.Rect(head_x - 2, head_y + 2, 4, 3)
        pygame.draw.ellipse(self.screen, BLACK, nose_rect)
        
        # Small mouth line
        mouth_start = (head_x - 2, head_y + 6)
        mouth_end = (head_x + 2, head_y + 6)
        pygame.draw.line(self.screen, BLACK, mouth_start, mouth_end, 1)
        
        # Legs and paws (brown legs with white paws like reference)
        paw_size = 6
        leg_width = 4
        leg_length = 8
        
        # Front legs (brown)
        left_front_leg = pygame.Rect(x - body_radius//2 - 2, y + body_radius - 8, leg_width, leg_length)
        right_front_leg = pygame.Rect(x + body_radius//2 - 2, y + body_radius - 8, leg_width, leg_length)
        pygame.draw.rect(self.screen, brown_color, left_front_leg)
        pygame.draw.rect(self.screen, brown_color, right_front_leg)
        
        # Back legs (brown)
        left_back_leg = pygame.Rect(x - body_radius//3 - 2, y + body_radius - 6, leg_width, leg_length)
        right_back_leg = pygame.Rect(x + body_radius//3 - 2, y + body_radius - 6, leg_width, leg_length)
        pygame.draw.rect(self.screen, brown_color, left_back_leg)
        pygame.draw.rect(self.screen, brown_color, right_back_leg)
        
        # White paws
        left_front_paw = (x - body_radius//2, y + body_radius + 2)
        right_front_paw = (x + body_radius//2, y + body_radius + 2)
        left_back_paw = (x - body_radius//3, y + body_radius + 4)
        right_back_paw = (x + body_radius//3, y + body_radius + 4)
        
        pygame.draw.circle(self.screen, WHITE, left_front_paw, paw_size)
        pygame.draw.circle(self.screen, WHITE, right_front_paw, paw_size)
        pygame.draw.circle(self.screen, WHITE, left_back_paw, paw_size)
        pygame.draw.circle(self.screen, WHITE, right_back_paw, paw_size)
        
        # Black paw pads
        pygame.draw.circle(self.screen, BLACK, left_front_paw, 2)
        pygame.draw.circle(self.screen, BLACK, right_front_paw, 2)
        pygame.draw.circle(self.screen, BLACK, left_back_paw, 2)
        pygame.draw.circle(self.screen, BLACK, right_back_paw, 2)
        
        # Tail (small brown stub)
        tail_pos = (x + body_radius - 1, y + body_radius//3)
        pygame.draw.circle(self.screen, brown_color, tail_pos, 3)
        
        # Cargo indicator (when carrying items)
        if player.get_total_cargo() > 0:
            package_rect = pygame.Rect(x + body_radius + 3, y - 4, 6, 5)
            pygame.draw.rect(self.screen, (139, 69, 19), package_rect)
            pygame.draw.rect(self.screen, BLACK, package_rect, 1)
        
        # Final outlines (dark brown instead of black for more natural look)
        outline_color = (60, 40, 20)  # Dark brown outline
        pygame.draw.ellipse(self.screen, outline_color, body_rect, 2)
        pygame.draw.circle(self.screen, outline_color, (head_x, head_y), head_radius, 2)
    
    def update(self, player, markets):
        """Update UI state - check if player moved away from market"""
        if self.selected_market and self.show_market_info:
            distance = player.position.distance_to(self.selected_market.position)
            if distance > 100:  # Auto-close when player moves away (slightly larger than interaction range)
                self.show_market_info = False
                self.trade_mode = False
                self.selected_market = None
                self.selected_good = None
    
    def handle_event(self, event, player, markets):
        """Handle UI events"""
        # Store player reference for use in other methods
        self.ui_player_ref = player
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.show_inventory = not self.show_inventory
            
            elif event.key == pygame.K_r:
                # Find nearest market
                nearest_market = None
                min_distance = float('inf')
                
                for market in markets:
                    distance = player.position.distance_to(market.position)
                    if distance < 80 and distance < min_distance:  # Interaction range
                        min_distance = distance
                        nearest_market = market
                
                if nearest_market:
                    self.selected_market = nearest_market
                    self.show_market_info = True
                    self.trade_mode = True
                else:
                    # Close market info if no market is nearby
                    self.show_market_info = False
                    self.trade_mode = False
                    self.selected_market = None
                    self.selected_good = None
            
            elif event.key == pygame.K_ESCAPE:
                self.show_inventory = False
                self.show_market_info = False
                self.trade_mode = False
                self.selected_market = None
                self.selected_good = None
            
            # Trading controls
            elif self.trade_mode and self.selected_market:
                # Check if this is an upgrade store
                if hasattr(self.selected_market, 'is_upgrade_store') and self.selected_market.is_upgrade_store:
                    if event.key == pygame.K_u:  # Upgrade key
                        if player.buy_capacity_upgrade():
                            print(f"Upgraded capacity to {player.max_cargo_capacity}!")
                        else:
                            print("Cannot afford upgrade!")
                    # No other trading controls for upgrade store
                    return
                
                # Select goods with number keys (only for regular markets)
                good_keys = {
                    pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, 
                    pygame.K_4: 3, pygame.K_5: 4
                }
                
                if event.key in good_keys:
                    good_index = good_keys[event.key]
                    if good_index < len(GOODS_TYPES):
                        self.selected_good = GOODS_TYPES[good_index]
                        self.trade_quantity = 1
                
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    if self.selected_good:
                        self.trade_quantity = min(10, self.trade_quantity + 1)
                
                elif event.key == pygame.K_MINUS:
                    if self.selected_good:
                        self.trade_quantity = max(1, self.trade_quantity - 1)
                
                elif event.key == pygame.K_b:  # Buy
                    if self.selected_good:
                        # Check for modifiers for max buy
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                            # Buy maximum possible
                            max_quantity = self.calculate_max_buy(player, self.selected_market, self.selected_good)
                            if max_quantity > 0:
                                player.buy_good(self.selected_market, self.selected_good, max_quantity)
                        else:
                            player.buy_good(self.selected_market, self.selected_good, self.trade_quantity)
                
                elif event.key == pygame.K_t:  # Sell (Trade/Transfer)
                    if self.selected_good:
                        # Check for modifiers for max sell
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                            # Sell maximum possible
                            max_quantity = min(player.inventory[self.selected_good], 10)  # Sell all or max 10
                            if max_quantity > 0:
                                player.sell_good(self.selected_market, self.selected_good, max_quantity)
                        else:
                            player.sell_good(self.selected_market, self.selected_good, self.trade_quantity)
