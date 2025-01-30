from flask import session,request,jsonify
from . import campaign_analytics_bp
from models import *
from datetime import time


@campaign_analytics_bp.post('/my_campaign_analytics')
def create_campaign_analtyics():
    data=request.get_json

    try:
        user_id=session.get('user_id')
        user=User.objects(id=user_id).first()

        if not user:
            return jsonify({"error":"User Not Found"}), 404
        if not id:
            return jsonify({"status":"error","message":"id not found on the session"}), 400
        
        if  data['campaign_name']=="":
            return jsonify({"status":"error","message":"please fill out this fields"}), 400
        campaign_analytics=Campaign_Analytics(
            user=user,
            campaign=data['campaign_name']
        )
        campaign_analytics.save()

    except Exception as e:
         return jsonify({"status": "error", "message": f"Error Occured while creating  a Campaign Analytics : {e}"}), 500