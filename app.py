from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import random
from datetime import datetime
import os

from config import Config, DevelopmentConfig
from modelos.models import db, User, Task, LootItem, UserInventory


def create_app(config_class=DevelopmentConfig):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Store session on filesystem
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = 604800  # 7 days
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize sessions
    from flask_session import Session
    Session(app)
    
    # Register CLI commands for database management
    @app.cli.command()
    def init_db():
        """Initialize the database"""
        with app.app_context():
            db.create_all()
            print("Database initialized!")
    
    @app.cli.command()
    def seed_db():
        """Seed database with initial loot items"""
        with app.app_context():
            # Check if already seeded
            if LootItem.query.first():
                print("Database already seeded!")
                return
            
            loot_items = [
                LootItem(name="Wooden Sword", rarity="common", base_reward_points=5, emoji="🗡️", description="A basic wooden sword for beginners"),
                LootItem(name="Magic Potion", rarity="common", base_reward_points=5, emoji="🧪", description="Restores your energy"),
                LootItem(name="Iron Axe", rarity="uncommon", base_reward_points=10, emoji="🪓", description="A sturdy iron tool"),
                LootItem(name="Silver Shield", rarity="rare", base_reward_points=15, emoji="🛡️", description="Legendary defense equipment"),
                LootItem(name="Golden Crown", rarity="legendary", base_reward_points=50, emoji="👑", description="The crown of champions"),
                LootItem(name="Diamond Ring", rarity="legendary", base_reward_points=50, emoji="💍", description="Sparkles with mystical power"),
                LootItem(name="Ruby Gem", rarity="rare", base_reward_points=15, emoji="💎", description="A magnificent red gem"),
                LootItem(name="Emerald Stone", rarity="rare", base_reward_points=15, emoji="🟩", description="A sacred green stone"),
                LootItem(name="Iron Helmet", rarity="uncommon", base_reward_points=10, emoji="🪖", description="Protects your head"),
                LootItem(name="Enchanted Book", rarity="uncommon", base_reward_points=10, emoji="📖", description="Contains ancient wisdom"),
            ]
            for item in loot_items:
                db.session.add(item)
            db.session.commit()
            print(f"Seeded {len(loot_items)} loot items!")
    
    # Authentication decorator
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.is_json:
                    return jsonify({'error': 'Not authenticated'}), 401
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def get_current_user():
        """Get current user from session"""
        if 'user_id' in session:
            return User.query.get(session['user_id'])
        return None
    
    # =====================
    # AUTHENTICATION ROUTES
    # =====================
    
    @app.route('/')
    def index():
        """Main app - redirects to login if not authenticated"""
        if 'user_id' in session:
            return render_template('index.html')
        return redirect(url_for('login'))
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Register new user"""
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
            
            # Validate inputs
            errors = []
            if not username or len(username) < 3:
                errors.append('Username must be at least 3 characters')
            if not email or '@' not in email:
                errors.append('Valid email required')
            if not password or len(password) < 6:
                errors.append('Password must be at least 6 characters')
            if password != confirm_password:
                errors.append('Passwords do not match')
            
            # Check if user exists
            if User.query.filter_by(username=username).first():
                errors.append('Username already taken')
            if User.query.filter_by(email=email).first():
                errors.append('Email already registered')
            
            if errors:
                if request.is_json:
                    return jsonify({'errors': errors}), 400
                return render_template('auth.html', errors=errors, mode='register'), 400
            
            # Create user
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            # Auto-login
            session['user_id'] = user.id
            session.permanent = True
            
            if request.is_json:
                return jsonify({'success': True}), 201
            return redirect(url_for('index'))
        
        return render_template('auth.html', mode='register')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login user"""
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            username = data.get('username', '')
            password = data.get('password', '')
            
            user = User.query.filter_by(username=username).first()
            
            if not user or not user.check_password(password):
                error = 'Invalid username or password'
                if request.is_json:
                    return jsonify({'error': error}), 401
                return render_template('auth.html', error=error, mode='login'), 401
            
            session['user_id'] = user.id
            session.permanent = True
            
            if request.is_json:
                return jsonify({'success': True}), 200
            return redirect(url_for('index'))
        
        return render_template('auth.html', mode='login')
    
    @app.route('/logout')
    def logout():
        """Logout user"""
        session.clear()
        return redirect(url_for('login'))
    
    # =====================
    # API ROUTES - TASKS
    # =====================
    
    @app.route('/api/tasks', methods=['GET'])
    @login_required
    def get_tasks():
        """Get all tasks for current user"""
        user = get_current_user()
        tasks = Task.query.filter_by(user_id=user.id).all()
        return jsonify([task.to_dict() for task in tasks]), 200
    
    @app.route('/api/tasks', methods=['POST'])
    @login_required
    def create_task():
        """Create new task"""
        user = get_current_user()
        data = request.get_json()
        
        # Validate
        title = data.get('title', '').strip()
        if not title or len(title) < 1:
            return jsonify({'error': 'Title is required'}), 400
        if len(title) > 200:
            return jsonify({'error': 'Title is too long'}), 400
        
        difficulty = data.get('difficulty', 'medium').lower()
        if difficulty not in Task.DIFFICULTY_POINTS:
            return jsonify({'error': 'Invalid difficulty'}), 400
        
        task = Task(
            user_id=user.id,
            title=title,
            description=data.get('description', ''),
            difficulty=difficulty,
            category=data.get('category', 'general')
        )
        db.session.add(task)
        db.session.commit()
        
        return jsonify(task.to_dict()), 201
    
    @app.route('/api/tasks/<int:task_id>/complete', methods=['PUT'])
    @login_required
    def complete_task(task_id):
        """Complete a task and award loot"""
        user = get_current_user()
        task = Task.query.filter_by(id=task_id, user_id=user.id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        if task.completed:
            return jsonify({'error': 'Task already completed'}), 400
        
        # Mark complete
        task.mark_complete()
        
        # Award points
        points = task.get_reward_points()
        user.add_points(points)
        
        # Award loot - weighted random selection by rarity
        loot_item = select_random_loot()
        
        # Add to inventory or increment quantity
        inventory_item = UserInventory.query.filter_by(
            user_id=user.id,
            loot_item_id=loot_item.id
        ).first()
        
        if inventory_item:
            inventory_item.quantity += 1
        else:
            inventory_item = UserInventory(
                user_id=user.id,
                loot_item_id=loot_item.id,
                quantity=1
            )
            db.session.add(inventory_item)
        
        db.session.commit()
        
        return jsonify({
            'task': task.to_dict(),
            'reward': {
                'points': points,
                'loot': loot_item.to_dict()
            },
            'user': user.to_dict()
        }), 200
    
    @app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
    @login_required
    def delete_task(task_id):
        """Delete a task"""
        user = get_current_user()
        task = Task.query.filter_by(id=task_id, user_id=user.id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'success': True}), 200
    
    # =====================
    # API ROUTES - INVENTORY
    # =====================
    
    @app.route('/api/inventory', methods=['GET'])
    @login_required
    def get_inventory():
        """Get user's inventory"""
        user = get_current_user()
        inventory_items = UserInventory.query.filter_by(user_id=user.id).all()
        return jsonify([item.to_dict() for item in inventory_items]), 200
    
    # =====================
    # API ROUTES - USER
    # =====================
    
    @app.route('/api/profile', methods=['GET'])
    @login_required
    def get_profile():
        """Get user profile"""
        user = get_current_user()
        return jsonify(user.to_dict()), 200
    
    # =====================
    # LOOT SELECTION
    # =====================
    
    def select_random_loot():
        """Select random loot item weighted by rarity"""
        items_by_rarity = {}
        for rarity, weight in LootItem.RARITY_WEIGHTS.items():
            items = LootItem.query.filter_by(rarity=rarity).all()
            if items:
                items_by_rarity[rarity] = (weight, items)
        
        # Build weighted list
        weighted_items = []
        for rarity, (weight, items) in items_by_rarity.items():
            weighted_items.extend([item for item in items for _ in range(int(weight * 100))])
        
        if weighted_items:
            return random.choice(weighted_items)
        
        # Fallback to any item
        return LootItem.query.first() or None
    
    # =====================
    # ERROR HANDLERS
    # =====================
    
    @app.errorhandler(404)
    def not_found(error):
        if request.is_json:
            return jsonify({'error': 'Not found'}), 404
        return render_template('index.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': 'Server error'}), 500
        return render_template('index.html'), 500
    
    return app


# Create the app
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # For production deployment
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)