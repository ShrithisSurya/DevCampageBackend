from flask import Blueprint

api_logs_bp=Blueprint('api_logs_bp',__name__)

from . import routes