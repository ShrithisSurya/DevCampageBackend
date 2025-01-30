from flask import Blueprint

billing_address_bp=Blueprint('billing_address_bp',__name__)

from . import routes