from flask import Blueprint

codeless_subscriber_bp=Blueprint('codeless_subscriber_bp',__name__)

from . import routes