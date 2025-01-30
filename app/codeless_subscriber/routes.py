from flask import request,session,jsonify
from models import *
from . import codeless_subscriber_bp
from datetime import datetime , timedelta

@codeless_subscriber_bp.post('my_subscriber')
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
    
    
@codeless_subscriber_bp.get('my_subscriber')
def get_codeless_subscriber():
    try:
        user_id=session.get('user_id')
        user=User.objects(id=user_id)
        if not user:
            return jsonify({"status":"error","message":"User not found"}), 404
        
        #pagination
        start=int(request.args.get('start',0)) #pagination start
        length=int(request.args.get('length',10)) #pagination end
        
        #search keyword
        search_value=request.args.get('search[value]','') 
        
        #sorting
        order_column_index=int(request.args.get('order[0][column]',0)) #column index to start
        order_direction=request.args.get('order[0][dir]','asc') #sort direction : asc or dsc
        
        #map column index to field names
        columns_map={
            0: None, #Default no sorting
            1: 'id',
            2: 'username',
            3: 'email',
            4: 'stream',
            5: 'added_time',
            6: 'updated_time'
        }

        # Get sorting column
        order_column = columns_map.get(order_column_index)
        order_by = f"-{order_column}" if order_column and order_direction == 'desc' else order_column
        
        #Initialize Query
        codeless_subscriber_query=Codeless_Subscriber.objects()
        
         # Apply date range filter
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        today = request.args.get('today', 'false').lower() == 'true'
        
        if today:
            codeless_subscriber_query=codeless_subscriber_query.filter(
                added_time_gte=datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
            )
        elif start_date and end_date:
            start_date=datetime.strptime(start_date,'%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            codeless_subscriber_query = codeless_subscriber_query.filter(added_time__gte=start_date, added_time__lt=end_date)
            
        # Total and filtered counts
        total_codeless_subscriber = Codeless_Subscriber.objects.count()
        filtered_codeless_subscriber = codeless_subscriber_query.count()

        # Apply sorting and pagination
        if order_column:
            codeless_subscriber_query = codeless_subscriber_query.order_by(order_by)
        codeless_subscriber_query = codeless_subscriber_query.skip(start).limit(length)

        # Prepare response data using list comprehension
        codeless_subscriber_data = [{
          "id": str(codeless.id),
          "username": codeless.user.username,
          "email": codeless.email,
          "stream": codeless.stream,
          "added_time": codeless.added_time.strftime('%Y-%m-%d %H:%M:%S'),
          "updated_time": codeless.updated_time.strftime('%Y-%m-%d %H:%M:%S') if codeless.updated_time else None,
        } for codeless in codeless_subscriber_query]

        # Return data in DataTables format
        return jsonify({
            "draw": int(request.args.get('draw', 1)),
            "recordsTotal": total_codeless_subscriber,
            "recordsFiltered": filtered_codeless_subscriber,
            "data": codeless_subscriber_data
        }), 200
     
    except Exception as e:
         return jsonify({"status": "error", "message": f"Error Occurred while retrieving a Codeless Subcriber Details: {str(e)}"}), 500


                
@codeless_subscriber_bp.put('my_subscriber')
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
    
    
                
@codeless_subscriber_bp.delete('my_subscriber')
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