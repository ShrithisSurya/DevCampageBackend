from . import tag_bp
from flask import request ,jsonify,session
from models import *
from datetime import datetime,timedelta


@tag_bp.post('/my_tag')
def create_tag():
    data=request.get_json()
    try:
        user_id = session.get('user_id')
        user = User.objects(id=user_id).first()  
        if not user:
            return jsonify({"status":"error","message": "User not found"}), 404
        
        if data['tag_name']=="":
            return jsonify({"status": "error", "message": "Please fill out these required fields"}), 400
        
        tags=Tag(
            user=user,
            tag_name=data['tag_name']
        )
        tags.save()
        return jsonify({"status": "success", "message": "Tag Created successfully."}), 200
    
    except Exception as e:
         return jsonify({"status": "error", "message": f"Error Occured while adding a Tag: {e}"}), 500
    
@tag_bp.get('/my_tag')
def get_tag():
    try:
        user_id = session.get('user_id')
        user = User.objects(id=user_id).first()

        if not user:
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
            2: 'tag_name',
            3: 'added_time',
            4: 'updated_time'
        }

        # Get sorting column
        order_column = columns_map.get(order_column_index)
        if order_column:
            order_by = f"-{order_column}" if order_direction == 'desc' else order_column
        else:
            order_by = '-added_time'  # Default sorting by time

        
       
        tags = Tag.objects(user=user)

        # Date range filter
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        today = request.args.get('today', 'false').lower() == 'true'
        if today:
           tags = tags.filter(
                added_time__gte=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            )
        elif start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            tags = tags.filter(added_time__gte=start_date, added_time__lt=end_date)


        # Apply search filter (case-insensitive)
        if search_value:
            tags= tags.filter(
                Q(email__icontains=search_value) |
                Q(tags__icontains=search_value) |
                Q(id__icontains=search_value)
            )

        # Total logs (before filtering)
        total_tags = Tag.objects(user=str(user.id)).count()
        
        # Filtered logs count
        filtered_tags = tags.count()

        # Apply sorting, pagination
        tags = tags.order_by(order_by).skip(start).limit(length)
    
        # Prepare subscriber data
        tags_data = [{
            "id": str(tag.id),
            "tag_name": tag.tag_name,
            "added_time": tag.added_time.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_time": tag.updated_time.strftime('%Y-%m-%d %H:%M:%S') if tag.updated_time else None,
        } for tag in tags]
        
        # Return data in DataTables format
        return jsonify({
            "draw": int(request.args.get('draw', 1)),
            "recordsTotal": total_tags,  # Total records in the database
            "recordsFiltered": filtered_tags,  # Total records after filtering
            "data": tags_data # Actual data for the current page
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error Occured while retrieving Tags: {e}"}), 500
  
    
@tag_bp.put('/my_tag')
def update_tag():
    data=request.get_json()
    id = request.args.get("id")
    try:
        if data['tag_name']=="":
            return jsonify({"status": "error", "message": "Please fill all the required fields."}), 400
    
        tags = Tag.objects(id=id).first()
        if not tags:
            return jsonify({"status": "error", "message": "Tag not found."}), 404
         
        tags.tag_name = data['tag_name']
        tags.updated_time=datetime.now()
        tags.save()
        return jsonify({"status": "success", "message": "Tag Updated successfully."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error Occured while retrieving Tag: {e}"}), 500



@tag_bp.delete('/my_tag')
def delete_tag():
    id=request.args.get('id')
    try:
        tags=Tag.objects(id=id).first()
        if not tags:
            return jsonify({"status":"error","message":"Tag not found"}), 404
        
        tags.delete()
        return jsonify({"status":"success","message":"Tag Sucessfully deleted"}), 200
    
    except Exception as e:
         return jsonify({"status": "error", "message": f"Error Occured while deleting Tag: {e}"}), 500


         