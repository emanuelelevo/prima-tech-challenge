from flask import Blueprint, request, jsonify
from services.aws_service import get_users_from_dynamodb, save_user_to_dynamodb, upload_file_to_s3
import logging

logger = logging.getLogger(__name__)

user_blueprint = Blueprint('user_routes', __name__)

@user_blueprint.route('/users', methods=['GET'])
def get_users():
    try:
        users = get_users_from_dynamodb()
        logger.info("GET /users request successful")
        return jsonify(users), 200
    except Exception as e:
        logger.error("GET /users request failed", exc_info=True)
        return jsonify({"error": str(e)}), 500

@user_blueprint.route('/user', methods=['POST'])
def create_user():
    try:
        name = request.form['name']
        email = request.form['email']
        file = request.files['avatar']
        
        avatar_url = upload_file_to_s3(file)
        
        save_user_to_dynamodb(name, email, avatar_url)
        
        logger.info("POST /user request successful")
        return jsonify({"message": "User created successfully!"}), 201
    except Exception as e:
        logger.error("POST /user request failed", exc_info=True)
        return jsonify({"error": str(e)}), 500
