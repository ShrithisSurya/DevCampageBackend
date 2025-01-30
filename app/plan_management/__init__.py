from flask import Blueprint

subscriptions_plans_bp=Blueprint('subscriptions_plans_bp',__name__)

from . import routes