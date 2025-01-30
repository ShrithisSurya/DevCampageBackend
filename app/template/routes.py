from flask import request,session,jsonify
from models import *
from.import templates_bp
from datetime import datetime,timedelta
import base64


@templates_bp.post('/my_template')
def create_template():
    try:
        user_id=session.get('user_id')
        user=User.objects(id=user_id).first()

        if not user:
            return jsonify({"status":"error","message":"User not found"}), 404
        

        template_name=request.form.get('template_name')
        description=request.form.get('description')
        if template_name =="" or description=="":
            return jsonify({"status": "error", "message": "Please fill all the required fields."}), 400

        templates=Templates(
            user=user,
            template_name=template_name,
            description=description,
        )
        templates.save()
        return jsonify({"status": "success", "message": "Templates Created successfully."}), 200
    
    
    except Exception as e:
         return jsonify({"status": "error", "message": f"Error Occured while adding a Templates: {e}"}), 500

@templates_bp.get('/my_template')
def get_template():
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
            2: 'user',
            3: 'template_name',
            4: 'description',
            5: 'added_time',
            6: 'updated_time'
        }

        # Determine the column to sort by
        order_column = columns_map.get(order_column_index)
        order_by = f"-{order_column}" if order_column and order_direction == 'desc' else order_column

        # Initialize query for user-specific plans
        templates = Templates.objects()

        # Date range filtering
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        today = request.args.get('today', 'false').lower() == 'true'

        if today:
            templates = templates.filter(
                added_time__gte=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            )
        elif start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                templates = templates.filter(added_time__gte=start_date, added_time__lt=end_date)
            except ValueError:
                return jsonify({"status": "error", "message": "Invalid date format. Use YYYY-MM-DD."}), 400

        # Apply search filter (case-insensitive)
        if search_value:
            templates = templates.filter(
                Q(template_name__icontains=search_value) |
                Q(description__icontains=search_value) |
                Q(id__icontains=search_value)
            )

        # Total and filtered counts
        total_templates = Templates.objects().count()
        filtered_templates = templates.count()

        # Apply sorting and pagination
        if order_column:
            templates = templates.order_by(order_by)
        templates = templates.skip(start).limit(length)

        templates_data = [{
           "id": str(template.id),
           "username":template.user.username,
           "template_name": template.template_name,
           "description": template.description,
           "added_time": template.added_time.strftime('%Y-%m-%d %H:%M:%S'),
           "updated_time": template.updated_time.strftime('%Y-%m-%d %H:%M:%S') if template.updated_time else None,
           }for template in templates]


        # Return data in DataTables format
        return jsonify({
            "draw": int(request.args.get('draw', 1)),
            "recordsTotal": total_templates,
            "recordsFiltered": filtered_templates,
            "data": templates_data
        }), 200

     except Exception as e:
        return jsonify({"status": "error", "message": f"Error occurred while retrieving Templates: {str(e)}"}), 500

    

@templates_bp.put('/my_template')
def update_template():
    id=request.args.get("id")
    try:                  
        template_name=request.form.get('template_name')
        description=request.form.get('description')
        if template_name =="" or description=="":
            return jsonify({"status": "error", "message": "Please fill all the required fields."}), 400
                
        templates = Templates.objects(id=id).first()
        if not templates:
            return jsonify({"status": "error", "message": "Templates not found."}), 404
        
        templates.template_name=template_name
        templates.description=description
        templates.save()
        return jsonify({"status": "success", "message": "Templates updated successfully."}), 200
        
    except Exception as e:
         return jsonify({"status": "error", "message": f"Error Occured while updating a Templates: {e}"}), 500
    

@templates_bp.delete('/my_template')
def delete_template():
    id=request.args.get("id")
    try:
        templates=Templates.objects(id=id).first()

        if not templates:
            return jsonify({"status":"error","message":"Template not found."}), 404
        
        templates.delete()
        return jsonify({"status":"success","message":"Template Sucessfully deleted."}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error Occured while deleting Templates: {e}"}), 500
     
     
     
@templates_bp.put('/save_template')
def save_template():
    id=request.args.get("id")
    try:
        data = request.get_json()
        
        template = Templates.objects(id=id).first()
        
        if not template:
            return jsonify({"status":"error","message":"Template not found."}), 404
        
        template.content = data["content"]
        template.save()
        return jsonify({"status":"success","message":"Template Saved Successfully."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error Occured while saving Template: {e}"}), 500
    

@templates_bp.put('/save_image')
def save_image():
    id=request.args.get("id")
    try:        
        template = Templates.objects(id=id).first()
        
        if not template:
            return jsonify({"status":"error","message":"Template not found."}), 404
        
        image = request.files.get('image')
        if not image:
          return jsonify({"status":"error","message": "No image provided"}), 400
        
        template.image = image
        template.save()
        return jsonify({"status":"success","message":"Image Saved Successfully."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error Occured while saving Template: {e}"}), 500