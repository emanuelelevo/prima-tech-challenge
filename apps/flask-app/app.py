from flask import Flask
from routes.user_routes import user_blueprint
from routes.health_check_routes import health_check_blueprint
from utils.swagger import swaggerui_blueprint
from utils.logging_config import setup_logging
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config['AWS_REGION'] = os.getenv('AWS_REGION', 'eu-north-1')
    app.config['DYNAMODB_TABLE'] = os.getenv('DYNAMODB_TABLE', 'my-table')
    app.config['S3_BUCKET'] = os.getenv('S3_BUCKET', 'my-bucket')
    app.config['LOG_LEVEL'] = os.getenv('LOG_LEVEL', 'INFO')

    setup_logging(app)

    # Log all environment variables at startup
    env_vars_message = ", ".join(f"{key}={value}" for key, value in os.environ.items())
    app.logger.info(f"Environment variables at startup: {env_vars_message}")

    app.register_blueprint(user_blueprint)
    app.register_blueprint(swaggerui_blueprint, url_prefix='/api/docs')
    app.register_blueprint(health_check_blueprint)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
