#!/usr/bin/env python
"""
Seed the database with initial data
Usage: python scripts/seed_db.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from modelos.models import LootItem


def seed_database():
    """Populate database with seed data"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if already seeded
        if LootItem.query.first():
            print("✓ Database already seeded!")
            return
        
        # Create loot items
        loot_items = [
            LootItem(name="Wooden Sword", rarity="common", base_reward_points=5, emoji="🗡️", 
                    description="A basic wooden sword for beginners"),
            LootItem(name="Magic Potion", rarity="common", base_reward_points=5, emoji="🧪", 
                    description="Restores your energy"),
            LootItem(name="Iron Axe", rarity="uncommon", base_reward_points=10, emoji="🪓", 
                    description="A sturdy iron tool"),
            LootItem(name="Silver Shield", rarity="rare", base_reward_points=15, emoji="🛡️", 
                    description="Legendary defense equipment"),
            LootItem(name="Golden Crown", rarity="legendary", base_reward_points=50, emoji="👑", 
                    description="The crown of champions"),
            LootItem(name="Diamond Ring", rarity="legendary", base_reward_points=50, emoji="💍", 
                    description="Sparkles with mystical power"),
            LootItem(name="Ruby Gem", rarity="rare", base_reward_points=15, emoji="💎", 
                    description="A magnificent red gem"),
            LootItem(name="Emerald Stone", rarity="rare", base_reward_points=15, emoji="🟩", 
                    description="A sacred green stone"),
            LootItem(name="Iron Helmet", rarity="uncommon", base_reward_points=10, emoji="🪖", 
                    description="Protects your head"),
            LootItem(name="Enchanted Book", rarity="uncommon", base_reward_points=10, emoji="📖", 
                    description="Contains ancient wisdom"),
        ]
        
        for item in loot_items:
            db.session.add(item)
        
        db.session.commit()
        print(f"✓ Seeded {len(loot_items)} loot items!")


if __name__ == '__main__':
    seed_database()
