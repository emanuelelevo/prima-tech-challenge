from flask import Blueprint, jsonify, current_app as app

health_check_blueprint = Blueprint('health_check', __name__)

@health_check_blueprint.route('/livez', methods=['GET'])
def livez():
    return jsonify(status='alive'), 200

@health_check_blueprint.route('/readyz', methods=['GET'])
def readyz():
    try:
        # Internal request to the /users endpoint
        with app.test_client() as client:
            response = client.get('/users')
            if response.status_code == 200:
                return jsonify(status='ready'), 200
            else:
                app.logger.error('Users endpoint check failed')
                return jsonify(status='error', error='Users endpoint check failed'), 500
    except Exception as e:
        app.logger.error('Readiness check failed', exc_info=True)
        return jsonify(status='error', error=str(e)), 500
