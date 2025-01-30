from flask import Blueprint
user_management_bp=Blueprint('user_management_bp',__name__)
from . import routes
