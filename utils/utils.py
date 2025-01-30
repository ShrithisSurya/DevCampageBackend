from flask import request , json
from models import *


def identify_client(user_agent):
    """Identify the client based on the User-Agent string."""
    if 'Postman' in user_agent:
        return 'Postman'
    elif 'curl' in user_agent:
        return 'cURL'
    elif 'Chrome' in user_agent:
        return 'Google Chrome'
    elif 'Firefox' in user_agent:
        return 'Mozilla Firefox'
    elif 'Safari' in user_agent and 'Chrome' not in user_agent:
        return 'Apple Safari'
    elif 'Edge' in user_agent:
        return 'Microsoft Edge'
    else:
        return 'Unknown Client'
    
def log_api_request(endpoint, user_id, response_data, status, method):
    """Helper function to log API request."""
    domain = request.headers.get('Origin', 'unknown domain')
    user_agent = request.headers.get('User-Agent', 'Unknown')
    platform_info = identify_client(user_agent)
    
    user = User.objects(id=user_id).first()

    log_entry = Api_Log(
        endpoint=endpoint,
        user=user if user else None,  
        domain=domain,
        method=request.method,  # Save the HTTP method here
        platform=platform_info,
        response=json.dumps(response_data) if isinstance(response_data, dict) else str(response_data),
        status=status
    )
    log_entry.save()