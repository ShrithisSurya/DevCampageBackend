from flask import session,request,jsonify
from models import *
from . import billing_address_bp
from datetime import datetime,timedelta 

@billing_address_bp.post('/my_bill')
def create_billing_address():
    data = request.get_json()
    try:
        user_id = session.get('user_id')
        user = User.objects(id=user_id).first()
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        if data['address_one'] == "" or data['address_two'] == "" or data['city'] == "" or data['state'] == "" or data['country'] == "" or data['pin_code'] == "":
            return jsonify({"status": "error", "message": "Please fill all the required fields."}), 400
        
        billing_address = Billing_Address(
            user=user,
            address_one=data['address_one'],
            address_two=data['address_two'],
            city=data['city'],
            state=data['state'],
            country=data['country'],
            pin_code=data['pin_code']
        )
        
        billing_address.save()
        return jsonify({"status": "success", "message": "Billing Address Created successfully."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error occurred while creating a Billing Address: {str(e)}"}), 500

    

@billing_address_bp.get('my_bill')
def get_billing_address():
    try:
        user_id=session.get('user_id')
        user=User.objects(id=user_id).first()
        if not user:
            return jsonify({"status":"error","message":"User not found"}), 404
        
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
            2: 'address_one',
            3: 'address_two',
            4: 'city',
            5: 'state',
            6: 'country',
            7: 'pincode',
            8: 'added_time',
            9: 'updated_time'
        }

        # Determine the column to sort by
        order_column = columns_map.get(order_column_index)
        order_by = f"-{order_column}" if order_column and order_direction == 'desc' else order_column

        # Initialize query for user-specific plans
        billing_address_query = Billing_Address.objects()

        # Date range filtering
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        today = request.args.get('today', 'false').lower() == 'true'

        if today:
            billing_address_query = billing_address_query.filter(
                added_time__gte=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            )
        elif start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                billing_address_query = billing_address_query.filter(added_time__gte=start_date, added_time__lt=end_date)
            except ValueError:
                return jsonify({"status": "error", "message": "Invalid date format. Use YYYY-MM-DD."}), 400

        # Apply search filter (case-insensitive)
        if search_value:
            billing_address_query = billing_address_query.filter(
                Q(address_one__icontains=search_value) |
                Q(address_two__icontains=search_value) |
                Q(city__icontains=search_value) |
                Q(state__icontains=search_value) |
                Q(country__icontains=search_value)|
                Q(pin_code__icontains=search_value)
            )

        # Total and filtered counts
        total_billing_address = Billing_Address.objects().count()
        filtered_billing_address = billing_address_query.count()

        # Apply sorting and pagination
        if order_column:
            billing_address_query = billing_address_query.order_by(order_by)
        billing_address_query = billing_address_query.skip(start).limit(length)

        # Prepare response data
        billing_address_data = [{
            "id": str(bill_add.id),
            "address_one": bill_add.address_one,
            "address_two": bill_add.address_two,
            "city": bill_add.city,
            "state": bill_add.state,
            "country":bill_add.country,
            "pin_code":bill_add.pin_code,
            "added_time": bill_add.added_time.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_time": bill_add.updated_time.strftime('%Y-%m-%d %H:%M:%S') if bill_add.updated_time else None,
        } for bill_add in billing_address_query]

        # Return data in DataTables format
        return jsonify({
            "draw": int(request.args.get('draw', 1)),
            "recordsTotal": total_billing_address,
            "recordsFiltered": filtered_billing_address,
            "data": billing_address_data
        }), 200        
    except Exception as e:
         return jsonify({"status":"error","message": f"Error occured while retrieving a Billing Address : {str(e)}"}),404
    
    

@billing_address_bp.put('/my_bill')
def update_billing_address():
    data = request.get_json()
    id = request.args.get('id')
    try:
        if data['address_one'] == "" or data['address_two'] == "" or data['city'] == "" or data['state'] == "" or data['country'] == "" or data['pin_code'] == "":
            return jsonify({"status": "error", "message": "Please fill all the required fields."}), 400
        
        billing_address = Billing_Address.objects(id=id).first()
        if not billing_address:
            return jsonify({"status": "error", "message": "Billing Address not found"}), 404
        
        billing_address.address_one = data['address_one']
        billing_address.address_two = data['address_two']
        billing_address.city = data['city']
        billing_address.state = data['state']
        billing_address.country = data['country']
        billing_address.pin_code = data['pin_code']
        
        billing_address.save()
        return jsonify({"status": "success", "message": "Billing Address Updated successfully."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error occurred while updating a Billing Address: {str(e)}"}), 500

    

@billing_address_bp.delete('/my_bill')
def delete_billing_address(): 
    id=request.args.get('id')
    try:
        billing_address=Billing_Address.objects(id=id).first()
        if not billing_address:
            return jsonify({"status":"error","message":"Billing Address  not found"}), 404
        
        billing_address.delete()
        return jsonify({"status":"success","message":"Billing Address Sucessfully deleted"}), 200
    
    except Exception as e:
         return jsonify({"status": "error", "message": f"Error Occured while deleting Tag: {e}"}), 500