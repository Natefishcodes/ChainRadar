from flask import Blueprint

bitcoin_price_alert_bp = Blueprint(
    'bitcoin_price_alert',
    __name__,
    template_folder='templates',
    url_prefix='/plugin/price_alert'
)

from . import routes

def initialize(app):
    app.register_blueprint(bitcoin_price_alert_bp)