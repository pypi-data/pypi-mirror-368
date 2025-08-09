"""
Game entities: Player, Truck, Markets, Goods
"""

import pygame
import math
import random
from .constants import *

class Position:
    """Simple 2D position class"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

class Good:
    """Represents a type of good that can be traded"""
    def __init__(self, name, base_price=10):
        self.name = name
        self.base_price = base_price
        self.current_price = base_price
        self.demand = random.uniform(0.5, 1.5)  # Demand multiplier
    
    def update_price(self, dt):
        """Update price based on market conditions"""
        # Simple price fluctuation based on demand
        price_change = (self.demand - 1.0) * PRICE_FLUCTUATION_RATE * dt
        self.current_price += price_change
        self.current_price = max(1, self.current_price)  # Minimum price of 1
        
        # Randomly adjust demand
        if random.random() < DEMAND_CHANGE_RATE * dt:
            self.demand += random.uniform(-0.1, 0.1)
            self.demand = max(0.1, min(2.0, self.demand))

class Market:
    """Represents a market where goods can be bought and sold"""
    def __init__(self, name, position, market_type="general"):
        self.name = name
        self.position = position
        self.market_type = market_type
        self.goods = {}
        self.money = random.randint(500, 2000)
        self.is_upgrade_store = False  # Will be set to True for upgrade stores
        
        # Initialize goods with random quantities (only for regular markets)
        if market_type != "upgrade":
            for good_type in GOODS_TYPES:
                self.goods[good_type] = Good(good_type, random.randint(5, 25))
                self.goods[good_type].quantity = random.randint(0, 20)
    
    def update(self, dt):
        """Update market conditions"""
        for good in self.goods.values():
            good.update_price(dt)
            
            # Randomly generate or consume goods
            if random.random() < 0.1 * dt:  # 10% chance per second
                if random.random() < 0.6:  # 60% chance to add goods
                    good.quantity += random.randint(1, 3)
                else:  # 40% chance to consume goods
                    good.quantity = max(0, good.quantity - random.randint(1, 2))
    
    def can_buy(self, good_type, quantity):
        """Check if market can sell goods to player"""
        return (good_type in self.goods and 
                self.goods[good_type].quantity >= quantity)
    
    def can_sell(self, good_type, quantity, total_cost):
        """Check if market can buy goods from player"""
        return (good_type in self.goods and 
                self.money >= total_cost)
    
    def buy_from_market(self, good_type, quantity):
        """Player buys goods from market"""
        if self.can_buy(good_type, quantity):
            cost = self.goods[good_type].current_price * quantity
            self.goods[good_type].quantity -= quantity
            self.money += cost
            return cost
        return 0
    
    def sell_to_market(self, good_type, quantity):
        """Player sells goods to market"""
        if good_type in self.goods:
            revenue = self.goods[good_type].current_price * quantity
            if self.money >= revenue:
                self.goods[good_type].quantity += quantity
                self.money -= revenue
                return revenue
        return 0

class Player:
    """The Boston Terrier player character"""
    def __init__(self, start_x, start_y):
        self.position = Position(start_x, start_y)
        self.money = 100
        self.inventory = {good_type: 0 for good_type in GOODS_TYPES}
        self.truck = None
        self.selected_market = None
        
        # Capacity upgrades
        self.capacity_upgrades = 0  # Number of upgrades purchased
        self.max_cargo_capacity = MAX_CARGO_CAPACITY  # Current capacity
        
        # Visual properties
        self.size = 30
        self.color = BROWN
    
    def get_total_cargo(self):
        """Get total items in inventory"""
        return sum(self.inventory.values())
    
    def can_carry_more(self, quantity=1):
        """Check if player can carry more items"""
        return self.get_total_cargo() + quantity <= self.max_cargo_capacity
    
    def get_upgrade_cost(self):
        """Calculate cost for next capacity upgrade"""
        base_cost = 1000
        return base_cost * (2 ** self.capacity_upgrades)  # Exponential scaling
    
    def can_afford_upgrade(self):
        """Check if player can afford capacity upgrade"""
        return self.money >= self.get_upgrade_cost()
    
    def buy_capacity_upgrade(self):
        """Purchase a capacity upgrade"""
        cost = self.get_upgrade_cost()
        if self.can_afford_upgrade():
            self.money -= cost
            self.capacity_upgrades += 1
            self.max_cargo_capacity += 1
            return True
        return False
    
    def move(self, dx, dy, dt):
        """Move the player, restricted to paths/roads"""
        new_x = self.position.x + dx * PLAYER_SPEED * dt
        new_y = self.position.y + dy * PLAYER_SPEED * dt
        
        # Check if the new position is on a valid path
        if self.is_on_path(new_x, new_y):
            self.position.x = new_x
            self.position.y = new_y
        
        # Keep player on screen
        self.position.x = max(self.size, min(SCREEN_WIDTH - self.size, self.position.x))
        self.position.y = max(self.size, min(SCREEN_HEIGHT - self.size, self.position.y))
    
    def is_on_path(self, x, y):
        """Check if a position is on a valid path/road"""
        # Horizontal paths (every 200 pixels, y from 85 to 115, 285 to 315, etc.)
        for path_y in range(100, SCREEN_HEIGHT, 200):
            if path_y - 15 <= y <= path_y + 15:
                return True
        
        # Vertical paths (every 200 pixels, x from 135 to 165, 335 to 365, etc.)
        for path_x in range(150, SCREEN_WIDTH, 200):
            if path_x - 15 <= x <= path_x + 15:
                return True
        
        # Allow movement near markets (within 50 pixels of any market)
        # This prevents getting stuck when interacting with markets
        for market_pos in [(200, 150), (1000, 200), (150, 600), (950, 650), (600, 400)]:
            market_distance = math.sqrt((x - market_pos[0])**2 + (y - market_pos[1])**2)
            if market_distance <= 50:
                return True
        
        return False
    
    def buy_good(self, market, good_type, quantity):
        """Buy goods from a market"""
        if not market.can_buy(good_type, quantity):
            return False
        
        if not self.can_carry_more(quantity):
            return False
        
        cost = market.goods[good_type].current_price * quantity
        if self.money >= cost:
            actual_cost = market.buy_from_market(good_type, quantity)
            self.money -= actual_cost
            self.inventory[good_type] += quantity
            return True
        return False
    
    def sell_good(self, market, good_type, quantity):
        """Sell goods to a market"""
        if self.inventory[good_type] < quantity:
            return False
        
        revenue = market.sell_to_market(good_type, quantity)
        if revenue > 0:
            self.money += revenue
            self.inventory[good_type] -= quantity
            return True
        return False

class Truck:
    """Truck for faster transportation (future feature)"""
    def __init__(self, position):
        self.position = position
        self.capacity = 20
        self.speed = TRUCK_SPEED
        self.owned = False
        self.cost = 500
