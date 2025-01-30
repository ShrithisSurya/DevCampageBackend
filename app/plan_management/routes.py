from flask import request,session,jsonify
from . import subscriptions_plans_bp
from models import *
from datetime import datetime,timedelta


@subscriptions_plans_bp.post('/my_plan')
def add_plan():
    data=request.get_json()
    try:
        user_id = session.get('user_id')
        user = User.objects(id=user_id).first()
        if not user:
            return jsonify({"status":"error","message": "User not found"}), 404
        
        if data['name']=="" or data['price']=="" or data['email_quota']=="" or data['api_quota']=="" or data['description']=="":
            return jsonify({"status": "error", "message": "Please fill out these required fields."}), 400
        
        plans=Subscription_Plan(
            name=data['name'],
            price=data['price'],
            email_quota=data['email_quota'],
            api_quota=data['api_quota'],
            description=data['description']
        )

        plans.save()
        return jsonify({"status":"success","message":"Plan added sucessfully."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error Occured while adding a Plan. : {str(e)}"}), 500
    
@subscriptions_plans_bp.get('/my_plan')
def get_plan():
    try:
        # Get the user ID from the session
        user_id = session.get('user_id')
        user = User.objects(id=user_id).first()

        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        # Pagination parameters
        start = max(0, int(request.args.get('start', 0)))  # Ensure non-negative
        length = max(1, int(request.args.get('length', 10)))  # Ensure minimum page size

        # Search keyword
        search_value = request.args.get('search[value]', '')

        # Sorting parameters
        order_column_index = int(request.args.get('order[0][column]', 0))  # Default to first column
        order_direction = request.args.get('order[0][dir]', 'asc')  # Default to ascending

        # Map column index to field names
        columns_map = {
            0: None,  # Default (no sorting)
            1: 'id',
            2: 'name',
            3: 'price',
            4: 'email_quota',
            5: 'api_quota',
            6: 'description',
            7: 'added_time',
            8: 'updated_time'
        }

        # Determine the column to sort by
        order_column = columns_map.get(order_column_index)
        order_by = f"-{order_column}" if order_column and order_direction == 'desc' else order_column

        # Initialize query for user-specific plans
        plans = Subscription_Plan.objects()

        # Date range filtering
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        today = request.args.get('today', 'false').lower() == 'true'

        if today:
            plans = plans.filter(
                added_time__gte=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            )
        elif start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                plans = plans.filter(added_time__gte=start_date, added_time__lt=end_date)
            except ValueError:
                return jsonify({"status": "error", "message": "Invalid date format. Use YYYY-MM-DD."}), 400

        # Apply search filter (case-insensitive)
        if search_value:
            plans = plans.filter(
                Q(name__icontains=search_value) |
                Q(price__icontains=search_value) |
                Q(email_quota__icontains=search_value) |
                Q(api_quota__icontains=search_value) |
                Q(id__icontains=search_value)
            )

        # Total and filtered counts
        total_plans = Subscription_Plan.objects().count()
        filtered_plans = plans.count()

        # Apply sorting and pagination
        if order_column:
            plans = plans.order_by(order_by)
        plans = plans.skip(start).limit(length)

        # Prepare response data
        plans_data = [{
            "id": str(plan.id),
            "name": plan.name,
            "price": plan.price,
            "email_quota": plan.email_quota,
            "api_quota": plan.api_quota,
            "description":plan.description,
            "added_time": plan.added_time.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_time": plan.updated_time.strftime('%Y-%m-%d %H:%M:%S') if plan.updated_time else None,
        } for plan in plans]

        # Return data in DataTables format
        return jsonify({
            "draw": int(request.args.get('draw', 1)),
            "recordsTotal": total_plans,
            "recordsFiltered": filtered_plans,
            "data": plans_data
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error occurred while retrieving Subscription Plans: {str(e)}"}), 500


  
    


@subscriptions_plans_bp.put('/my_plan')
def update_plan():
    data=request.get_json()
    id=request.args.get('id')
    try:
        if data['name']=="" or data['price']=="" or data['email_quota']=="" or data['api_quota']=="" or data['description']=="":
            return jsonify({"status":"error","message": "please fill out these required fields."}), 400
        
        plans=Subscription_Plan.objects(id=id).first()

        if not plans:
            return jsonify({"status":"error","message":"Plans not found"}), 404
        
        plans.name=data['name']
        plans.price=data['price']
        plans.email_quota=data['email_quota']
        plans.api_quota=data['api_quota']
        plans.description=data['description']
        plans.updated_time=datetime.now()
        plans.save()
        return jsonify({"status":"sucesss","message":"Plan updated Sucessfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error Occured while updating a Plan. : {e}"}), 500
    

@subscriptions_plans_bp.delete('/my_plan')
def delete_plan():
    id=request.args.get('id')
    try:
        plans=Subscription_Plan.objects(id=id).first()

        if not plans:
            return jsonify({"status":"error","message":"Plans not found."}), 404
        
        plans.delete()
        return jsonify({"status":"success","message":"Plan Sucessfully deleted."}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error Occured while deleting Plan: {e}"}), 500



    


