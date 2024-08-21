from flask import Blueprint
from flask_swagger_ui import get_swaggerui_blueprint

swagger_blueprint = Blueprint('swagger', __name__)

SWAGGER_URL = '/api/docs'  
API_URL = '/static/swagger.json'  

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "elevorin-prima-test"
    }
)

swagger_blueprint.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
