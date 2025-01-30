from  flask import request,jsonify,session
from .import ticket_bp
from models import *
from datetime import datetime,timedelta

@ticket_bp.post('/my_ticket')
def create_ticket():
    data=request.get_json()
    try:
        user_id=session.get('user_id')
        user=User.objects(id=user_id).first()
        if not user:
            return jsonify({"status":"error","message": "User not found"}), 404
        
        if data['title']== "" or data['description']== "":
            return jsonify({"status": "error", "message": "Please fill out these required fields."}), 400
        
        tickets=Tickets(
            user=user,
            title=data['title'],
            description=data['description']
        )
        tickets.save()
        return jsonify({"status":"success","message":"Ticket created sucessfully."}), 200

    except Exception as e:
          return jsonify({"status": "error", "message": f"Error Occured while creating a Ticket. : {e}"}), 500
    
@ticket_bp.get('my_ticket')
def get_ticket():
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
            2: 'user',
            3: 'title',
            4: 'description',
            5: 'status',
            6: 'date_of_resolved',
            7: 'added_time',
            8: 'updated_time'
        }

        # Get sorting column
        order_column = columns_map.get(order_column_index)
        if order_column:
            order_by = f"-{order_column}" if order_direction == 'desc' else order_column
        else:
            order_by = '-added_time'  # Default sorting by time

        
       
        tickets = Tickets.objects(user=user)

        # Date range filter
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        today = request.args.get('today', 'false').lower() == 'true'
        if today:
            tickets = tickets.filter(
                added_time__gte=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            )
        elif start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            tickets = tickets.filter(added_time__gte=start_date, added_time__lt=end_date)


        # Apply search filter (case-insensitive)
        if search_value:
           tickets=tickets.filter(
                Q(email__icontains=search_value) |
                Q(tags__icontains=search_value) |
                Q(id__icontains=search_value)
            )

        # Total logs (before filtering)
        total_tickets = Tickets.objects(user=str(user.id)).count()
        
        # Filtered logs count
        filtered_tickets = tickets.count()

        # Apply sorting, pagination
        tickets = tickets.order_by(order_by).skip(start).limit(length)
    
        # Prepare subscriber data
        tickets_data = [{
            "id": str(ticket.id),
            "username":ticket.user.username,
            "title": ticket.title,
            "description": ticket.description,
            "status":ticket.status,
            "date of resolved":ticket.date_of_resolved.strftime('%Y-%m-%d %H:%M:%S') if ticket.date_of_resolved else None,
            "added_time": ticket.added_time.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_time": ticket.updated_time.strftime('%Y-%m-%d %H:%M:%S') if ticket.updated_time else None,
        } for ticket in tickets]
        
        # Return data in DataTables format
        return jsonify({
            "draw": int(request.args.get('draw', 1)),
            "recordsTotal": total_tickets,  # Total records in the database
            "recordsFiltered": filtered_tickets,  # Total records after filtering
            "data": tickets_data  # Actual data for the current page
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error Occured while retrieving Tickets: {e}"}), 500
    
    

@ticket_bp.put('my_ticket')
def update_ticket():
    data=request.get_json()
    id=request.args.get('id')
    try:
        if data['title']=="" or data['description']=="":
            return jsonify({"status": "error", "message": "Please fill out these required fields."}), 400
            
        tickets=Tickets.objects(id=id).first()
        if not tickets:
            return jsonify({"status":"error","message":"Ticket not found"}), 404
        
        tickets.title=data['title']
        tickets.description=data['description']
        tickets.updated_time=datetime.now()
        tickets.date_of_resolved=datetime.now()
        tickets.save()
        return jsonify({"status":"sucesss","message":"Ticket updated Sucessfully"}), 200

        

    except Exception as e:
         return jsonify({"status": "error", "message": f"Error Occured while updating a Ticket : {e}"}), 500
    

@ticket_bp.delete('my_ticket')
def delete_ticket():
     id=request.args.get('id')
     try:
         tickets=Tickets.objects(id=id).first()
         if not tickets:
            return jsonify({"status":"error","message":"Tickets not found."}), 404
        
         tickets.delete()
         return jsonify({"status":"success","message":"Ticket Sucessfully deleted."}), 200
     
     except Exception as e:
         return jsonify({"status": "error", "message": f"Error Occured while deleting Ticket: {e}"}), 500


    

