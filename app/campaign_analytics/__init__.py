from flask import Blueprint

campaign_analytics_bp=Blueprint('campaign_analytics_bp',__name__)

from . import routes