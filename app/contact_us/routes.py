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
     
@contact_us_bp.get('contact_us')
def get_contact_us():
    try:
        user_id=session.get('user_id')
        user=User.objects(id=user_id)
        if not user:
             return jsonify({"status":"error","message":"User not found"}), 404
         
        #Pagination Start
        start= max(0,int(request.args.get('start',0))) #Starting Page
        length= max(1,int(request.args.get('length',10))) #over all length of the filter page
        
        # Search keyword
        search_value = request.args.get('search[value]', '')

        # Sorting parameters
        order_column_index = int(request.args.get('order[0][column]', 0))  # Default to first column
        order_direction = request.args.get('order[0][dir]', 'asc')  # Default to ascending
        
        columns_map={
            0: None,     #Default no sorting
            1: 'id',  
            2: 'full_name',
            3: 'email',
            4: 'subject',
            5: 'message',
            6: 'added_time',
            7: 'updated_time'
        }
        
        # Determine the column to sort by
        order_column = columns_map.get(order_column_index)
        order_by = f"-{order_column}" if order_column and order_direction == 'desc' else order_column
        
        #Filter 
        contact_us_query=Contact_us.objects()
        
         # Date range filtering
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        today = request.args.get('today', 'false').lower() == 'true'
        
        if today:
            contact_us_query = contact_us_query.filter(
                added_time__gte=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            )
        elif start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                contact_us_query = contact_us_query.filter(added_time__gte=start_date, added_time__lt=end_date)
            except ValueError:
                return jsonify({"status": "error", "message": "Invalid date format. Use YYYY-MM-DD."}), 400
            
         # Apply search filter (case-insensitive)
        if search_value:
            contact_us_query = contact_us_query.filter(
                Q(full_name__icontains=search_value) |
                Q(email__icontains=search_value) |
                Q(subject__icontains=search_value) |
                Q(message__icontains=search_value) |
                Q(id__icontains=search_value)
            )
         # Total and filtered counts
        total_contact = Contact_us.objects().count()
        filtered_contact = contact_us_query.count()

        # Apply sorting and pagination
        if order_column:
            contact_us_query = contact_us_query.order_by(order_by)
        contact_us_query = contact_us_query.skip(start).limit(length)
        
         # Prepare response data
        contact_us_data = [{
            "id": str(contact.id),
            "full_name": contact.full_name,
            "email": contact.email,
            "subject": contact.subject,
            "message": contact.message,
            "added_time": contact.added_time.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_time": contact.updated_time.strftime('%Y-%m-%d %H:%M:%S') if contact.updated_time else None,
        } for contact in contact_us_query]

        # Return data in DataTables format
        return jsonify({
            "draw": int(request.args.get('draw', 1)),
            "recordsTotal": total_contact,
            "recordsFiltered": filtered_contact,
            "data": contact_us_data
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error occurred while retrieving Subscription Plans: {str(e)}"}), 500




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
        
        
        