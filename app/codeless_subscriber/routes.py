from flask import request,session,jsonify
from models import *
from . import codeless_subscriber_bp
from datetime import datetime , timedelta

@codeless_subscriber_bp.post('/my_subscriber')
def create_codeless_subcriber():
    data=request.get_json()
    try:
        user_id=session.get('user_id')
        user=User.objects(id=user_id).first()
        if not user:
            return jsonify({"status":"error","message":"User not found"}), 404
                
        if data['email']=="":
            return jsonify({"status":"error","message":"Please fill out the required fields"}), 400
        
        codeless_subscriber=Codeless_Subscriber(
            user=user,
            email=data['email']          
        )
        codeless_subscriber.save()
        return jsonify({"status":"success","message":"Codeless Subscriber Created Successfully"}), 200
    
    except Exception as e:
        return jsonify({"status":"error","message": f"Error Occured While creating a Codeless Subscriber :{str(e)}"}), 404
    
                
@codeless_subscriber_bp.put('/my_subscriber')
def update_codeless_subscriber():
    data=request.get_json()
    id=request.args.get('id')
    try:
        codeless_subscriber=Codeless_Subscriber.objects(id=id).first()
        if not codeless_subscriber:
            return jsonify({"status":"error","message":"Id not found for the Codeless Subscriber"}), 404
        
        if data['email']=="":
            return jsonify({"status":"error","message":"Please Fill all the required files "}), 400
    
        codeless_subscriber.email=data['email']
        codeless_subscriber.updated_time=datetime.now()
        codeless_subscriber.save()
        return jsonify({"status":"success","message":"Codeless Subscriber Updated Sucessfully"}), 200
    
    
    except Exception as e:
        return jsonify({"status":"error","message": f"Error Occured while Updating a Codeless Subscriber : {str(e)}"}), 500
       
                
@codeless_subscriber_bp.delete('/my_subscriber')
def delete_codeless_subscriber():
    id=request.args.get('id')
    try:
        codeless_subscriber=Codeless_Subscriber.objects(id=id).first()
        if not codeless_subscriber:
            return jsonify({"status":"error","message":"Id not found for the Codeless Subscriber"}), 404
        
        codeless_subscriber.delete()
        return jsonify({"status":"success","message":"Codeless Subscriber Deleted Sucessfully"}), 200
    
    
    except Exception as e:
        return jsonify({"status":"error","message": f"Error Occured while Deleting a Codeless Subscriber : {str(e)}"}), 500