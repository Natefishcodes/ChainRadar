from . import bitcoin_price_alert_bp
from flask import render_template, request, flash, redirect, url_for
import requests
import threading
import time

# Global list to store alerts
price_alerts = []


@bitcoin_price_alert_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        threshold = float(request.form.get('threshold'))
        notification_method = request.form.get('notification_method')

        price_alerts.append({
            'threshold': threshold,
            'notification_method': notification_method
        })

        flash(f"Price alert set at ${threshold} via {notification_method}", "success")
        return redirect(url_for('bitcoin_price_alert.index'))

    return render_template('bitcoin_price_alert/index.html', alerts=price_alerts)


# Background thread to monitor Bitcoin price
def monitor_bitcoin_price():
    while True:
        try:
            response = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")
            data = response.json()
            current_price = float(data["bpi"]["USD"]["rate"].replace(",", ""))

            for alert in price_alerts:
                if current_price >= alert['threshold']:
                    message = f"Bitcoin price alert: ${current_price} has crossed your threshold of ${alert['threshold']}"
                    print(message)  # Replace with Telegram or Discord notification function

                    # Remove the alert after triggering
                    price_alerts.remove(alert)

        except Exception as e:
            print(f"Error fetching Bitcoin price: {e}")

        time.sleep(60)  # Check every 60 seconds


# Start the background thread
threading.Thread(target=monitor_bitcoin_price, daemon=True).start()