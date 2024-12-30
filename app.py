import requests
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from extensions import db, login_manager
from config import Config
from models import User, Notification
from flask_login import login_user, current_user, logout_user, login_required
from forms import RegistrationForm, LoginForm
from flask_migrate import Migrate
from datetime import datetime
import threading
import time
from werkzeug.security import generate_password_hash, check_password_hash  # Import hashing functions

# Initialize Flask app with explicit template folder path
app = Flask(__name__, template_folder='ChainRadar/templates')
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize Flask-Migrate
migrate = Migrate(app, db)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Function to send a notification to Telegram
def send_telegram_notification(user, message):
    if user.telegram_chat_id:
        url = f"https://api.telegram.org/bot{Config.TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": user.telegram_chat_id, "text": message}
        try:
            requests.post(url, data=data)
        except Exception as e:
            print(f"Failed to send Telegram notification: {e}")


# Function to send a notification to Discord
def send_discord_notification(user, message):
    if user.discord_webhook:
        try:
            requests.post(user.discord_webhook, json={"content": message})
        except Exception as e:
            print(f"Failed to send Discord notification: {e}")


# Function to monitor Bitcoin addresses for transactions
def monitor_bitcoin_addresses():
    while True:
        with app.app_context():
            users = User.query.filter(User.wallet_addresses.isnot(None)).all()
            for user in users:
                addresses = user.wallet_addresses.split(",")
                for address in addresses:
                    try:
                        # Placeholder for actual API call to check Bitcoin transactions
                        response = requests.get(f"https://api.blockcypher.com/v1/btc/main/addrs/{address}")
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("n_tx") > 0:
                                message = f"New transaction detected for address: {address}"

                                # Log the notification in the database
                                notification = Notification(
                                    user_id=user.id,
                                    message=message,
                                    notification_type="transaction_alert",
                                    timestamp=datetime.utcnow()
                                )
                                db.session.add(notification)
                                db.session.commit()

                                # Send notifications via Telegram and Discord
                                send_telegram_notification(user, message)
                                send_discord_notification(user, message)

                    except Exception as e:
                        print(f"Error checking address {address}: {e}")
        time.sleep(60)  # Check every 60 seconds


# Home route to display the login form
@app.route("/")
def home():
    form = LoginForm()
    return render_template("login.html", form=form)


# Registration route with password hashing
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)  # Hash the password
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


# Login route with password verification
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):  # Verify hashed password
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Login failed. Check your username and password.", "danger")
    return render_template("login.html", form=form)


# Dashboard route for logged-in users
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", wallet=current_user.wallet_addresses)


# Logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# Monitoring route to display saved wallet addresses and notification history
@app.route("/monitoring")
@login_required
def monitoring():
    user_addresses = current_user.wallet_addresses.split(",") if current_user.wallet_addresses else []
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    return render_template("monitoring.html", addresses=user_addresses, notifications=notifications)


# Update wallet addresses and send notifications
@app.route("/update_wallet_addresses", methods=["POST"])
@login_required
def update_wallet_addresses():
    data = request.get_json()
    new_addresses = data.get("wallet_addresses", "")
    current_user.wallet_addresses = new_addresses
    db.session.commit()

    message = "Wallet addresses updated."
    notification = Notification(user_id=current_user.id, message=message, notification_type="wallet_update", timestamp=datetime.utcnow())
    db.session.add(notification)
    db.session.commit()

    send_telegram_notification(current_user, message)
    send_discord_notification(current_user, message)

    return jsonify({"message": "Wallet addresses updated successfully!"}), 200


# Update notifications route
@app.route("/update_notifications", methods=["POST"])
@login_required
def update_notifications():
    data = request.get_json()
    current_user.discord_webhook = data.get("discord_webhook", "")
    current_user.discord_user_id = data.get("discord_user_id", "")
    current_user.telegram_chat_id = data.get("telegram_chat_id", "")
    current_user.telegram_user_id = data.get("telegram_user_id", "")
    db.session.commit()
    return jsonify({"message": "Notifications updated successfully!"}), 200


# Run the Flask app and start the monitoring thread
if __name__ == "__main__":
    threading.Thread(target=monitor_bitcoin_addresses, daemon=True).start()
    app.run(host='0.0.0.0', port=5001, debug=False)