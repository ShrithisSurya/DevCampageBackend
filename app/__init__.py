from flask import Flask,render_template
from mongoengine import connect, connection
from models import *
from app.config import Config


def create_app():
    
    app = Flask(__name__)

    app.config.from_object(Config)

    try:
        connect(host=Config.MONGO_URI)
        if connection.get_connection():
            app.logger.info("Database connected successfully.")
    except Exception as e:
        app.logger.error(f"Database connection failed: {e}")
        raise e
    

    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.email_campaign import email_campaign_bp
    app.register_blueprint(email_campaign_bp, url_prefix='/campaign')

    from app.tag import tag_bp
    app.register_blueprint(tag_bp,url_prefix='/tag')

    from app.plan_management import subscriptions_plans_bp
    app.register_blueprint(subscriptions_plans_bp,url_prefix='/plan')
    
    from app.ticket_raising import ticket_bp
    app.register_blueprint(ticket_bp,url_prefix='/ticket')

    from app.user_management import user_management_bp
    app.register_blueprint(user_management_bp,url_prefix="/user")

    from app.logs import api_logs_bp
    app.register_blueprint(api_logs_bp,url_prefix='/api_logs')

    from app.template import templates_bp
    app.register_blueprint(templates_bp,url_prefix='/template')

    from app.admin import admin_bp
    app.register_blueprint(admin_bp,url_prefix='/admin')

    from app.billing_address import billing_address_bp
    app.register_blueprint(billing_address_bp,url_prefix='/billing_add')
    
    from app.codeless_subscriber import codeless_subscriber_bp
    app.register_blueprint(codeless_subscriber_bp,url_prefix='/subscriber')
    
    from app.contact_us import contact_us_bp
    app.register_blueprint(contact_us_bp,url_prefix='/contact')
    
    from app.main import main_bp
    app.register_blueprint(main_bp)

    return app