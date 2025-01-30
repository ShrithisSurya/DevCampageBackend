from flask import render_template, jsonify, request, session
from . import auth_bp
from models import *

@auth_bp.get('/')
def default():
    return render_template('index.html')

@auth_bp.post('/register')
def register():
    data = request.get_json()

    try:
        if data['email'] == "" or data['username'] == "" or data['password'] == "":
            return jsonify({"status": "error", "message": "Please fill all the required fields."}), 400

        if User.objects(email=data['email']).first():
            return jsonify({"status": "error", "message": "Account already exists. Please try with another email."}), 404

        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_hashed_password(data['password'])
        user.save()

        return jsonify({"status": "success", "message": "Account registered successfully."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error Occured while registering an account: {e}"}), 500
    


@auth_bp.post('/login')
def login():
    data = request.get_json()

    try:
        if data['email'] == "" or data['password'] == "":
            return jsonify({"status": "error", "message": "Please fill all the required fields."}), 400

        user = User.objects(email=data['email']).first()

        if not user:
            return jsonify({"status": "error", "message": "Account not exists. Please try with registered email."}), 404
        
        if not user.check_password(data['password']):
            return jsonify({"status": "error", "message": "Password is not matched with your email."}), 404

        session['user_id'] = str(user.id)

        return jsonify({"status": "success", "message": "Account login successfully.", "redirect": "/dashboard"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error Occured while login an account: {e}"}), 500


@auth_bp.get('/logout')
def logout():
    if session['user_id']:
        session.clear()
        return render_template('index.html')
    else:
        return jsonify({"status": "error", "message": "You are not logged in. Please login and logout again."}), 400