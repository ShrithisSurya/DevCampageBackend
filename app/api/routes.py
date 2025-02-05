from . import api_bp
from flask import request, session, jsonify
from models import *
from utils.utils import *
from datetime import timedelta

@api_bp.post('/subscribers')
def create_subscriber():
    data=request.get_json()
    try:
        user_id = session.get('user_id')
        user = User.objects(id=user_id).first()

        if not user:
            log_api_request("/api/subscribers",user_id,"User not found","error","POST")
            return jsonify({"status":"error","message":"User not found"}), 404
        
        if data['email']=="":
           log_api_request("/api/subscribers",user_id,"Fill all the required Fields","error","POST")
           return jsonify({"status": "error", "message": "Please fill all the required fields."}), 400
        
        if 'tags' in data:
            tags = Tag.objects(user=user, tag_name__in=data['tags'])
            if not tags:
                log_api_request("/api/subscribers",user_id,"Tags not found","error","POST")
                return jsonify({"status":"error","message":"Tags not found"}), 404
        else:
            log_api_request("/api/subscribers",user_id,"Please fill out all the required fields","error","POST")
            return jsonify({"status":"error","message":"Please fill out all the required fields"}), 404
        
        subscriber=Subscriber(
            user=user,
            email=data['email'],
            tags=list(tags)           
        )
        subscriber.save()

        log_api_request("/api/subscribers",user_id,"Email Subscriberd Successfully","success","POST")
        return jsonify({"status": "success", "message": "Email Subscribered successfully."}), 200
    
    except Exception as e:
        log_api_request("/api/subscribers",user_id,"Error occured while adding a subscriber","error","POST")
        return jsonify({"status": "error", "message": f"Error Occured while adding a subscriber: {e}"}), 500
    

@api_bp.get('/subscribers')
def get_subscriber():
    try:
        user_id = session.get('user_id')
        user = User.objects(id=user_id).first()

        if not user:
            log_api_request("/api/subscribers",user_id,"User not found","error","GET")
            return jsonify({"status":"error","message": "User not found"}), 404

        start = int(request.args.get('start', 0))  # Pagination start
        length = int(request.args.get('length', 10))  # Page size

        # Search keyword
        search_value = request.args.get('search[value]', '')

        # Sorting
        order_column_index = int(request.args.get('order[0][column]', 0))  # Column index to sort
        order_direction = request.args.get('order[0][dir]', 'asc')  # Sort direction: asc or desc

        # Map column index to field names
        columns_map = {
            0: None,
            1: 'id',
            2: 'email',
            3: 'tags',
            4: 'added_time',
            5: 'updated_time'
        }

        # Get sorting column
        order_column = columns_map.get(order_column_index)
        if order_column:
            order_by = f"-{order_column}" if order_direction == 'desc' else order_column
        else:
            order_by = '-added_time'  # Default sorting by time

        
       
        subscriber_query = Subscriber.objects(user=user)

        # Date range filter
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        today = request.args.get('today', 'false').lower() == 'true'
        if today:
            subscriber_query = subscriber_query.filter(
                added_time__gte=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            )
        elif start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            subscriber_query = subscriber_query.filter(added_time__gte=start_date, added_time__lt=end_date)


        # Apply search filter (case-insensitive)
        if search_value:
            subscriber_query = subscriber_query.filter(
                Q(email__icontains=search_value) |
                Q(tags__icontains=search_value) |
                Q(id__icontains=search_value)
            )

        # Total logs (before filtering)
        total_subscriber = Subscriber.objects(user=str(user.id)).count()
        
        # Filtered logs count
        filtered_subscriber = subscriber_query.count()

        # Apply sorting, pagination
        subscriber_query = subscriber_query.order_by(order_by).skip(start).limit(length)
    
        # Prepare subscriber data
      # Prepare subscriber data
        subscriber_data = [{
              "id": str(subs.id),
               "email": subs.email,
               "tags": [str(tag.id) for tag in subs.tags],  # Assuming you want the Tag IDs
               "added_time": subs.added_time.strftime('%Y-%m-%d %H:%M:%S'),
               "updated_time": subs.updated_time.strftime('%Y-%m-%d %H:%M:%S') if subs.updated_time else None,
             } for subs in subscriber_query]

        
        log_api_request("/api/subscribers",user_id,"Subscribers Retrieved Successfully","success","GET")
        # Return data in DataTables format
        return jsonify({
            "draw": int(request.args.get('draw', 1)),
            "recordsTotal": total_subscriber,  # Total records in the database
            "recordsFiltered": filtered_subscriber,  # Total records after filtering
            "data": subscriber_data  # Actual data for the current page
        }), 200

    except Exception as e:
        log_api_request("/api/subscribers",user_id,"Error Occured while retrieving Subscribers","error","GET")
        return jsonify({"status": "error", "message": f"Error Occured while retrieving subscribers: {e}"}), 500
    


@api_bp.put('/subscribers')
def update_subscriber():

    data=request.get_json()
    id=request.args.get("id")

    try:
        user_id = session.get('user_id')
        user = User.objects(id=user_id)
        if not user:
            log_api_request("/api/subscribers",user_id,"Subscribers not found for the user","error","PUT")
            return jsonify({"status":"error","message":"User not found"}), 404

        if not id:
            log_api_request("/api/subscribers",user_id,"Id not found for the subcriber","error","PUT")
            return jsonify({"status": "error", "message": "Id not found for the subscriber."}), 400
        
        if data['email']=="" or data['tag']=="":
           log_api_request("/api/subscribers",user_id,"Subscribers,Fill all the required Fields","error","PUT")
           return jsonify({"status": "error", "message": "Please fill all the required fields."}), 400
        
        subscriber = Subscriber.objects(id=id).first()
        if not subscriber:
            log_api_request("/api/subscribers",user_id,"Subscribers not found","error","PUT")
            return jsonify({"status": "error", "message": "Subscriber not found."}), 404
        
        
        subscriber.email = data['email']
        subscriber.tag = data['tag']
        subscriber.updated_time = datetime.now()
        subscriber.save()
        log_api_request("/api/subscribers",user_id,"Subscribers Updated Successfully","success","PUT")
        return jsonify({"status": "success", "message": "Subscriber updated successfully."}), 200
    
    except Exception as e:

        log_api_request("/api/subscribers",user_id,"Error Occured while retrieveing","error","PUT")
        return jsonify({"status": "error", "message": f"Error Occured while retrieving subscribers: {e}"}), 500
    


@api_bp.delete('/subscribers')
def delete_subscriber():
    id=request.args.get("id")

    try:
        user_id = session.get('user_id')
        user = User.objects(id=user_id)
        if not user:
            log_api_request("/api/subscribers",user_id,"User not found","error","DELETE")
            return jsonify({"status":"error","message": "User not found"}),404
        
        if not id:
            log_api_request("/api/subscribers",user_id,"id not found","error","DELETE")
            return jsonify({"status": "error", "message": "Id not found for the subscriber."}), 400
        
        subscriber = Subscriber.objects(id=id).first()

        if not subscriber:
            log_api_request("/api/subscribers",user_id,"Subcribers not found","error","DELETE")
            return jsonify({"status": "error", "message": "Subscribers not found."}), 404
        
        
        subscriber.delete()
        log_api_request("/api/subscribers",user_id,"Subscribers Deleted Successfully","Success","DELETE")
        return jsonify({"status": "success", "message": "Subscriber deleted successfully."}), 200

        
    except Exception as e:
         log_api_request("/api/subscribers",user_id,"Error occured while deleting subscriber","error","DELETE")
         return jsonify({"status": "error", "message": f"Error Occured while deleting subscribers: {e}"}), 500












































































































































































































































