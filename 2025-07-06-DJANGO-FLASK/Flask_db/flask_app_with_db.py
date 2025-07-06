import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    """User model for storing user information"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class Post(db.Model):
    """Post model for user posts"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship with User
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    
    def to_dict(self):
        """Convert post object to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id,
            'username': self.user.username
        }
    
    def __repr__(self):
        return f'<Post {self.title}>'

# Routes
@app.route('/')
def index():
    """Home page showing all users and posts"""
    users = User.query.all()
    posts = Post.query.join(User).order_by(Post.created_at.desc()).all()
    return render_template('index.html', users=users, posts=posts)

@app.route('/users')
def users():
    """Display all users"""
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Add a new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required!', 'error')
            return redirect(url_for('add_user'))
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('add_user'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'error')
            return redirect(url_for('add_user'))
        
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash(f'User {username} created successfully!', 'success')
            return redirect(url_for('users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'error')
            return redirect(url_for('add_user'))
    
    return render_template('add_user.html')

@app.route('/user/<int:user_id>')
def user_detail(user_id):
    """Display user details and their posts"""
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
    return render_template('user_detail.html', user=user, posts=posts)

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    """Add a new post"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        user_id = request.form.get('user_id')
        
        # Validation
        if not title or not content or not user_id:
            flash('All fields are required!', 'error')
            return redirect(url_for('add_post'))
        
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            flash('User does not exist!', 'error')
            return redirect(url_for('add_post'))
        
        # Create new post
        new_post = Post(title=title, content=content, user_id=user_id)
        
        try:
            db.session.add(new_post)
            db.session.commit()
            flash(f'Post "{title}" created successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating post: {str(e)}', 'error')
            return redirect(url_for('add_post'))
    
    users = User.query.all()
    return render_template('add_post.html', users=users)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    
    try:
        # Delete user's posts first
        Post.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'error')
    
    return redirect(url_for('users'))

# API Routes
@app.route('/api/users')
def api_users():
    """API endpoint to get all users"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/posts')
def api_posts():
    """API endpoint to get all posts"""
    posts = Post.query.join(User).all()
    return jsonify([post.to_dict() for post in posts])

@app.route('/api/user/<int:user_id>')
def api_user_detail(user_id):
    """API endpoint to get user details"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('500.html'), 500

# Database initialization
def init_db():
    """Initialize database and create tables"""
    with app.app_context():
        db.create_all()
        
        # Create sample data if database is empty
        if User.query.count() == 0:
            sample_user = User(username='admin', email='admin@example.com')
            sample_user.set_password('password')
            
            sample_user2 = User(username='john_doe', email='john@example.com')
            sample_user2.set_password('password123')
            
            db.session.add(sample_user)
            db.session.add(sample_user2)
            db.session.commit()
            
            # Add sample posts
            post1 = Post(title='Welcome to our blog!', 
                        content='This is the first post on our blog. Welcome everyone!',
                        user_id=sample_user.id)
            
            post2 = Post(title='Flask is awesome!', 
                        content='I love working with Flask. It makes web development so much easier.',
                        user_id=sample_user2.id)
            
            db.session.add(post1)
            db.session.add(post2)
            db.session.commit()
            
            print("Sample data created successfully!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)