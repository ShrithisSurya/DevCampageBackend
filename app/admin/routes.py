from flask import request,session,jsonify
from models import *
from.import admin_bp
from utils.utils import *
from datetime import datetime,timedelta
import base64


@admin_bp.get('/users')
def get_user():
     try:
        # Fetch the current user ID from the session
        user_id = session.get('user_id')
        current_user = User.objects(id=user_id).first()

        if not current_user:
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
            1: 'name',
            2: 'email',
            3: 'phone',
            4: 'billing_address',
            5: 'city',
            6: 'state',
            7: 'country',
            8: 'zip_code',
            9: 'subscription_plan',
            10: 'usage'
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
        
        # Get all user IDs
        user_ids = [user.id for user in users_query]

        # Fetch billing addresses for those users
        billing_addresses = Billing_Address.objects(user__in=user_ids)
        billing_map = {billing.user.id: billing for billing in billing_addresses}
        
        
        # Prepare response data using list comprehension
        users_data = [ {
        "name": user.username,
        "email": user.email,
        "phone": user.phone,
        "billing_address": billing_map[user.id].address_one if user.id in billing_map else None,
        "city": billing_map[user.id].city if user.id in billing_map else None,
        "state": billing_map[user.id].state if user.id in billing_map else None,
        "country": billing_map[user.id].country if user.id in billing_map else None,
        "zip_code": billing_map[user.id].pin_code if user.id in billing_map else None,
        "subscription_plan":user.subscription_plan.name if user.subscription_plan else None,
        }for user in users_query
        ]
        
        # Return data in DataTables format
        return jsonify({
            "draw": int(request.args.get('draw', 1)),
            "recordsTotal": total_users,
            "recordsFiltered": filtered_users,
            "data": users_data
        }), 200
     
     except Exception as e:
        return jsonify({"status": "error", "message": f"Error Occurred while retrieving User Details: {e}"}), 500

@admin_bp.get('/templates')
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
            2: 'username',
            3: 'template_name',
            4: 'description',
            5: 'image',
            6: 'added_time',
            7: 'updated_time'
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
           "image_id": str(template.image.grid_id) if template.image and template.image.grid_id else None, #Image id 
           "image": base64.b64encode(template.image.read()).decode('utf-8') if template.image and template.image.grid_id else None, #image bas364 cde
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

@admin_bp.get('/logs')
def get_logs():
    try:
        # Pagination parameters
        start = int(request.args.get('start', 0))
        length = int(request.args.get('length', 10))
        
        # Sorting parameters
        order_column_index = int(request.args.get('order[0][column]', 0))
        order_direction = request.args.get('order[0][dir]', 'asc')
        
        # Mapping columns to fields
        columns_map = {0: None, 1: 'log_time', 2: 'endpoint', 3: 'response', 4: 'user', 5: 'domain'}
        order_column = columns_map.get(order_column_index, '-log_time')
        order_by = f"-{order_column}" if order_direction == 'desc' else order_column

        # Get current user
        user = User.objects(id=session.get('user_id')).first()
        if not user:
            return jsonify({"status": "error", "message": "User Not Found"}), 404
        
        # Base query for logs
        logs_query = Api_Log.objects(user=str(user.id))
        
        # Date range for Today, Yesterday, Last Month
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        yesterday_start = today_start - timedelta(days=1)
        yesterday_end = today_end - timedelta(days=1)
        last_month_start = (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1)
        last_month_end = last_month_start.replace(day=28) + timedelta(days=4)
        
        # Log count type filter
        log_count_type = request.args.get('log_count_type', '').lower()
        
        # Count logs for today, yesterday, last month
        today_count = logs_query.filter(log_time__gte=today_start, log_time__lt=today_end).count()
        yesterday_count = logs_query.filter(log_time__gte=yesterday_start, log_time__lt=yesterday_end).count()
        last_month_count = logs_query.filter(log_time__gte=last_month_start, log_time__lt=last_month_end).count()
        user_count = User.objects.count()
        
        # Apply log count type filter (Today, Yesterday, Last Month, etc.)
        if log_count_type == 'today':
            logs_query = logs_query.filter(log_time__gte=today_start, log_time__lt=today_end)
        elif log_count_type == 'yesterday':
            logs_query = logs_query.filter(log_time__gte=yesterday_start, log_time__lt=yesterday_end)
        elif log_count_type == 'lastmonth':
            logs_query = logs_query.filter(log_time__gte=last_month_start, log_time__lt=last_month_end)
        elif log_count_type == '':
            
            
            # Date filter range (from request params)
            if request.args.get('today', 'false').lower() == 'true':
                logs_query = logs_query.filter(log_time__gte=today_start)
            else:
                start_date = request.args.get('start_date')
                end_date = request.args.get('end_date')
                if start_date and end_date:
                    logs_query = logs_query.filter(log_time__gte=datetime.strptime(start_date, '%Y-%m-%d'),log_time__lt=datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
        
        # Search filter (case-insensitive)
        search_value = request.args.get('search[value]', '')
        if search_value:
            logs_query = logs_query.filter(
                Q(endpoint__icontains=search_value) | Q(response__icontains=search_value) |
                Q(domain__icontains=search_value) | Q(platform__icontains=search_value) |
                Q(user__icontains=search_value)
            )
        
        # Pagination and sorting
        total_logs = Api_Log.objects(user=str(user.id)).count()
        filtered_logs = logs_query.count()
        logs_query = logs_query.order_by(order_by).skip(start).limit(length)

        # Prepare log data
        log_data = [{
            "id": str(log.id),
            "time": log.log_time.strftime('%Y-%m-%d %H:%M:%S'),
            "endpoint": log.endpoint,
            "user": User.objects(id=log.user.id).first().username if log.user else "Unknown",
            "domain": log.domain,
            "method":log.method,
            "platform": log.platform,
            "response": log.response
        } for log in logs_query]
        
        # Return the response
        return jsonify({
            "status": "success",
            "log_counts": {
                "today_count": today_count,
                "yesterday_count": yesterday_count,
                "last_month_count": last_month_count,
                "user_count": user_count
            },
            "draw": int(request.args.get('draw', 1)),
            "recordsTotal": total_logs,
            "recordsFiltered": filtered_logs,
            "data": log_data
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error occurred while retrieving logs: {e}"}), 500



@admin_bp.get('/plans')
def get_subscription_plans():
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




@admin_bp.get('/tickets')
def get_tickets():
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
        return jsonify({"status": "error", "message": f"Error Occured while retrieving SubscriptionPlans: {e}"}), 500
    
    
    
  
@admin_bp.get('/contact_us')
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
    
    
    
@admin_bp.get('/my_subscriber')
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

    
    