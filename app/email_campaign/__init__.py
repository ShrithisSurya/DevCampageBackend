from flask import Blueprint

email_campaign_bp=Blueprint('email_campaign_bp',__name__)

from . import routes