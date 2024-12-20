from extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(60), nullable=False)
    telegram_chat_id = db.Column(db.String(500), nullable=True)
    telegram_user_id = db.Column(db.String(100), nullable=True)
    discord_user_id = db.Column(db.String(100),  nullable=True)
    discord_webhook = db.Column(db.String(500), nullable=True)
    wallet_addresses = db.Column(db.String(1000), nullable=True)

    # Relationship to notifications
    notifications = db.relationship('Notification', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.wallet_addresses}', '{self.discord_webhook}', '{self.telegram_chat_id}')"

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # 'Discord' or 'Telegram'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Notification('{self.notification_type}', '{self.message}', '{self.timestamp}')"

# Future Implementation: One-to-Many Relationship for Wallet Addresses
# Uncomment and modify the following code to use a separate table for wallet addresses.

# class WalletAddress(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     address = db.Column(db.String(42), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#
# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=True)
#     password = db.Column(db.String(60), nullable=False)
#     wallet_addresses = db.relationship('WalletAddress', backref='user', lazy=True)
#
#     def __repr__(self):
#         return f"User('{self.username}', '{self.email}', '{len(self.wallet_addresses)} wallets')"