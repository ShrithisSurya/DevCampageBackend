from flask import request,session,jsonify
from models import *
from . import user_management_bp
from datetime import datetime,timedelta 

@user_management_bp.post('/my_user')
def add_user():
    data = request.get_json()
    try:
        user_id = session.get('user_id')
        user = User.objects(id=user_id).first()

        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        # Extract user details from the request
        if data["username"] == "" or data["email"] == "" or data["phone"] == "" or data["password"]=="" or data["subscription_plan_name"] == "" or data["billing_address"] == "":
            return jsonify({"status": "error", "message": "All fields are required"}), 400

        username = data["username"]
        email = data["email"]
        phone = data["phone"]
        password=data["password"]
        subscription_plan_name = data["subscription_plan_name"]
        billing_address = data["billing_address"]  

       
        subscription_plan = Subscription_Plan.objects(name=subscription_plan_name).first()
        if not subscription_plan:
            return jsonify({"status": "error", "message": "Subscription plan not found"}), 404
        
        new_user = User(
            username=username,
            email=email,
            phone=phone,
            password=password,
            subscription_plan=subscription_plan,  # reference to the subscription plan
        )
        new_user.set_hashed_password(data['password'])
        new_user.save()

        billing_address_obj = Billing_Address(
            address_one=billing_address.get("address_one"),
            address_two=billing_address.get("address_two"),
            city=billing_address.get("city"),
            state=billing_address.get("state"),
            country=billing_address.get("country"),
            pin_code=billing_address.get("pin_code"),
            user=new_user
        )
        billing_address_obj.save()  # Save the billing address and generate an ID       
        return jsonify({"status": "success", "message": "User added successfully"}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error occurred while adding a user: {e}"}), 500




@user_management_bp.get('/my_user')
def get_user():
    try:
        # Fetch the current user ID from the session
        user_id = session.get('user_id')
        user = User.objects(id=user_id).first()

        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        # Pagination
        start = int(request.args.get('start', 0))  # Pagination start
        length = int(request.args.get('length', 10))  # Page size

        # Search keyword
        search_value = request.args.get('search[value]', '')

        # Sorting
        order_column_index = int(request.args.get('order[0][column]', 0))  # Column index to sort
        order_direction = request.args.get('order[0][dir]', 'asc')  # Sort direction: asc or desc

        # Map column index to field names
        columns_map = {
            0: None,  # Default (e.g., no sorting)
            1: 'id',
            2: 'username',
            3: 'email',
            4: 'password',
            5: 'status',
            6: 'added_time',
            7: 'updated_time',
            8: 'subscription_plan'
        }

        # Get sorting column
        order_column = columns_map.get(order_column_index)
        order_by = f"-{order_column}" if order_column and order_direction == 'desc' else order_column

        # Initialize query
        users_query = User.objects()

        # Apply date range filter
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        today = request.args.get('today', 'false').lower() == 'true'

        if today:
            users_query = users_query.filter(
                added_time__gte=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            )
        elif start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            users_query = users_query.filter(added_time__gte=start_date, added_time__lt=end_date)

        # Apply search filter (case-insensitive)
        if search_value:
            users_query = users_query.filter(
                Q(email__icontains=search_value) |
                Q(id__icontains=search_value)
            )

        # Total and filtered counts
        total_users = User.objects.count()
        filtered_users = users_query.count()

        # Apply sorting and pagination
        if order_column:
            users_query = users_query.order_by(order_by)
        users_query = users_query.skip(start).limit(length)

        # Prepare response data using list comprehension
        users_data = [{
          "id": str(user.id),
          "username": user.username,
          "email": user.email,
          "password": user.password,
          "status": user.status,
          "added_time": user.added_time.strftime('%Y-%m-%d %H:%M:%S'),
          "updated_time": user.updated_time.strftime('%Y-%m-%d %H:%M:%S') if user.updated_time else None,
          "subscription_plan": user.subscription_plan.name if user.subscription_plan else None  # Access name only if plan exists
        } for user in users_query]

        # Return data in DataTables format
        return jsonify({
            "draw": int(request.args.get('draw', 1)),
            "recordsTotal": total_users,
            "recordsFiltered": filtered_users,
            "data": users_data
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error Occurred while retrieving User Details: {e}"}), 500

    
 
@user_management_bp.put('/my_user')
def update_user():
    data=request.get_json()
    id = request.args.get("id")
    try:
        user=User.objects(id=id).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if data['username']=="" or data['email']=="" or data['phone']=="":
            return jsonify({"status":"error","message": "please fill out these required fields"}), 400
        
        user.username=data['username']
        user.email=data['email']
        user.phone=data['phone']
        user.is_active=data['is_active']

        if 'subscription_plan' in data:
            subscription_plan = Subscription_Plan.objects(name=data['subscription_plan']).first()
            
        if subscription_plan:
            user.subscription_plan = subscription_plan  
        user.save()
        return jsonify({"status":"sucesss","message":"User updated Successfully"}), 200
    
    except Exception as e:
        return jsonify({"status":"error","message":f"Error Occured While retrieving a User : {e}"}), 500
     




         
        
     

