#!/usr/bin/env python3
"""a new Flask view that handles all routes for the Session
authentication"""

from api.v1.views import app_views
from flask import abort, jsonify, request
from models.user import User
from os import getenv


@app_views.route('/auth_session/login', methods=['POST'], strict_slashes=False)
def login():
    """ POST method to return based on email """
    email = request.form.get('email')
    password = request.form.get('password')
    if not email:
        return jsonify({"error": "email missing"}), 400
    if not password:
        return jsonify({"error": "password missing"}), 400
    try:
        users = User.search({'email': email})
    except Exception:
        return jsonify({"error": "no user found for this email"})
    if not users:
        return jsonify({"error": "no user found for this email"})
    for user in users:
        if not user.is_valid_password(password):
            return jsonify({"error": "wrong password"}), 401
        from api.v1.app import auth
        session_id = auth.create_session(user.id)
        output = jsonify(user.to_json())
        output.set_cookie(getenv('SESSION_NAME'), session_id)
        return output
    return jsonify({"error": "no user found for this email"})
