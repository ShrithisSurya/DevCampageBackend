from flask import request, session, jsonify
from models import *
from . import contact_us_bp
from datetime import datetime,timedelta

@contact_us_bp.post('/contact_us')
def create_contact_us():
    data=request.get_json()
    try:
        user_id=session.get('user_id')
        user=User.objects(id=user_id).first()
        if not user:
             return jsonify({"status":"error","message":"User not found"}), 404
         
        if data['full_name']=="" or data['email']=="" or data['subject']=="" or data['message']=="":
             return jsonify({"status": "error", "message": "Please fill all the required fields."}), 400
        
        contact_us=Contact_us(
            user=user,
            full_name=data['full_name'],
            email=data['email'],
            subject=data['subject'],
            message=data['message']           
        )
        contact_us.save()
        return jsonify({"status": "success", "message": "Contact Us Created successfully."}), 200
        
    except Exception as e:
         return jsonify({"status": "error", "message": f"Error Occured while creating a Contact Us: {str(e)}"}), 500
     
@contact_us_bp.put('/contact_us')
def update_contact_us():
    data=request.get_json()
    id=request.args.get("id")
    try:
        contact_us=Contact_us.objects(id=id).first()
        if not contact_us:
            return jsonify({"status":"error","message":"Id not found for the Contact Us"})
        
        if data['full_name']=="" or data['email']=="" or data['subject']=="" or data['message']=="":
             return jsonify({"status": "error", "message": "Please fill all the required fields."}), 400
        
        contact_us.full_name=data['full_name']
        contact_us.email=data['email']
        contact_us.subject=data['subject']
        contact_us.message=data['message']
        contact_us.updated_time=datetime.now()
        contact_us.save()
        return jsonify({"status": "success", "message": "Contact Us Updated successfully."}), 200
        
        
    except Exception as e:
         return jsonify({"status": "error", "message": f"Error Occured while Updating a Contact Us: {str(e)}"}), 500
     
     
@contact_us_bp.delete('/contact_us')
def delete_contact_us():
    id=request.args.get("id")
    try:
        contact_us=Contact_us.objects(id=id).first()
        if not contact_us:
            return jsonify({"status":"error","message":"Id not found for the Contact Us"})
        
        contact_us.delete()
        return jsonify({"status": "success", "message": "Contact Us Deleted successfully."}), 200
    
    except Exception as e:
         return jsonify({"status": "error", "message": f"Error Occured while deleting a Contact Us: {str(e)}"}), 500
        
        
        