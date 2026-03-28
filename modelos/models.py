from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication and progression"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    
    # Relationships
    tasks = db.relationship('Task', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    inventory = db.relationship('UserInventory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def calculate_level(self):
        """Calculate level based on points (every 100 points = 1 level)"""
        self.level = max(1, self.total_points // 100 + 1)
    
    def add_points(self, points):
        """Add points and update level"""
        self.total_points += points
        self.calculate_level()
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'total_points': self.total_points,
            'level': self.level,
            'created_at': self.created_at.isoformat()
        }


class LootItem(db.Model):
    """Loot item definition (rewards available in the game)"""
    __tablename__ = 'loot_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(500))
    rarity = db.Column(db.String(50), nullable=False)  # common, uncommon, rare, legendary
    base_reward_points = db.Column(db.Integer, default=0)
    emoji = db.Column(db.String(10), default='🎁')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user_inventories = db.relationship('UserInventory', backref='loot_item', lazy='dynamic', cascade='all, delete-orphan')
    
    # Rarity weights for random selection
    RARITY_WEIGHTS = {
        'common': 0.60,
        'uncommon': 0.25,
        'rare': 0.10,
        'legendary': 0.05
    }
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'rarity': self.rarity,
            'base_reward_points': self.base_reward_points,
            'emoji': self.emoji
        }


class Task(db.Model):
    """User task/quest"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(1000))
    difficulty = db.Column(db.String(50), default='medium')  # easy, medium, hard, legendary
    category = db.Column(db.String(100), default='general')  # work, health, learning, chores, general
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    
    # Difficulty points mapping
    DIFFICULTY_POINTS = {
        'easy': 1,
        'medium': 5,
        'hard': 10,
        'legendary': 25
    }
    
    def get_reward_points(self):
        """Get points for completing this task"""
        return self.DIFFICULTY_POINTS.get(self.difficulty, 5)
    
    def mark_complete(self):
        """Mark task as completed"""
        self.completed = True
        self.completed_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty,
            'category': self.category,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'reward_points': self.get_reward_points()
        }


class UserInventory(db.Model):
    """User's inventory of looted items"""
    __tablename__ = 'user_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    loot_item_id = db.Column(db.Integer, db.ForeignKey('loot_items.id'), nullable=False)
    acquired_at = db.Column(db.DateTime, default=datetime.utcnow)
    quantity = db.Column(db.Integer, default=1)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'loot_item_id', name='uq_user_loot'),)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'loot_item': self.loot_item.to_dict(),
            'quantity': self.quantity,
            'acquired_at': self.acquired_at.isoformat()
        }
