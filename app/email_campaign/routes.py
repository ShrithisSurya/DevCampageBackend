from . import email_campaign_bp
from flask import request,session,jsonify
from models import *
from datetime import datetime,timedelta


@email_campaign_bp.post('/my_campaign')
def create_email_campaign():
    data=request.get_json()
    try:
        user_id = session.get('user_id')
        user = User.objects(id=user_id).first()

        if not user:
            return jsonify({"status":"error","message": "User not found"}), 404
        
        if data['campaign_name']=="" or data['subject']=="" or data['content']=="":
            return jsonify({"status": "error", "message": "Please fill out these required fields"}), 400

        if 'audience_tag' in data:
            tags=Tag.objects(user=user, tag_name__in=data['audience_tag'])
            if not tags:
                return jsonify({"status":"error","message":"Tags not found"}), 404

        email_campaign=Email_Campaign(
            user=user,
            campaign_name=data['campaign_name'],
            subject=data['subject'],
            content=data['content'],
            audience_tag=list(tags),
            scheduled_at=datetime.fromisoformat(data['scheduled_at']) if data['scheduled_at'] else None
        )
        email_campaign.save()
 
    
        # Campaign -Analytics
        if  data['campaign_name']=="":
            return jsonify({"status":"error","message":"please fill out this fields"}), 400
        
        campaign_analytics=Campaign_Analytics(
            user=user,
            campaign=data['campaign_name']
        )
        campaign_analytics.save()

        return jsonify({"status":"success","message":"Email Campaign Successfully Created"}), 200

    except Exception as e:
         return jsonify({"status": "error", "message": f"Error Occured while creating  a Email Campaign : {e}"}), 500
    

@email_campaign_bp.get('/my_campaign')
def get_email_campaign():
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
            2: 'campaign_name',
            3: 'audience_tag',
            4: 'subject',
            5: 'status',
            6: 'added_time',
            7: 'updated_time'
        }

        # Get sorting column
        order_column = columns_map.get(order_column_index)
        if order_column:
            order_by = f"-{order_column}" if order_direction == 'desc' else order_column
        else:
            order_by = '-added_time'  # Default sorting by time

        
       
        email_campaign = Email_Campaign.objects(user=user)

        # Date range filter
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        today = request.args.get('today', 'false').lower() == 'true'
        if today:
            email_campaign = email_campaign.filter(
                added_time__gte=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            )
        elif start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            email_campaign = email_campaign.filter(added_time__gte=start_date, added_time__lt=end_date)


        # Apply search filter (case-insensitive)
        if search_value:
            email_campaign = email_campaign.filter(
                Q(email__icontains=search_value) |
                Q(tags__icontains=search_value) |
                Q(id__icontains=search_value)
            )

        # Total logs (before filtering)
        total_campaign = Email_Campaign.objects(user=str(user.id)).count()
        
        # Filtered logs count
        filtered_campaign = email_campaign.count()

        # Apply sorting, pagination
        email_campaign = email_campaign.order_by(order_by).skip(start).limit(length)
    
        # Prepare subscriber data
        email_campaign_data = [{
            "id": str(emc.id),
            "campaign_name": emc.campaign_name,
            "audience_tag": emc.audience_tag,
            "subject":emc.subject,
            "status":emc.status,
            "content":emc.content,
            "added_time": emc.added_time.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_time": emc.updated_time.strftime('%Y-%m-%d %H:%M:%S') if emc.updated_time else None,
        } for emc in email_campaign]
        
        # Return data in DataTables format
        return jsonify({
            "draw": int(request.args.get('draw', 1)),
            "recordsTotal": total_campaign,  # Total records in the database
            "recordsFiltered": filtered_campaign,  # Total records after filtering
            "data": email_campaign_data  # Actual data for the current page
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error Occured while retrieving Email Campaign: {e}"}), 500
    

@email_campaign_bp.put('/my_campaign')
def update_email_campaign():
    data=request.get_json()
    id=request.args.get('id')
    try:
        if data['campaign_name']=="" or data['subject']=="" or data['content']=="":
            return jsonify({"status":"error","message": "please fill out these required fields"}), 400
        
        email_campaign=Email_Campaign.objects(id=id).first()

        if not email_campaign:
            return jsonify({"status":"error","message":"Email Campaign not found"}), 404
        
        email_campaign.campaign_name=data['campaign_name']
        email_campaign.subject=data['subject']
        email_campaign.content=data['content']
        email_campaign.updated_time=datetime.now()
        email_campaign.save()
        return jsonify({"status":"sucesss","message":"Email Campaign Updated Sucessfully"}), 200

      
    except Exception as e:
        return jsonify({"status":"error","message":f"Error Occured While retrieving Campaign : {e}"}), 500
    


@email_campaign_bp.delete('/my_campaign')
def delete_email_campaign():
    id=request.args.get('id')
    try:        
        email_campaign=Email_Campaign.objects(id=id).first()

        if not email_campaign:
            return jsonify({"status":"error","message":"Email Campaign not found"}), 404
        
        email_campaign.delete()
        return jsonify({"status":"success","message":"Email Campaign Sucessfully deleted"}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error Occured while deleting Campaign: {e}"}), 500

