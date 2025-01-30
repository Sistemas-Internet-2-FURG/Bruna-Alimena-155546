from flask import Flask
from .config import Config
from .routes.auth import register_auth_routes, auth_routes
from .routes.products import register_product_routes
from .routes.aisles import register_aisle_routes
from app.db import create_tables
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    create_tables()
    app.register_blueprint(auth_routes)
    register_auth_routes(app)
    register_product_routes(app)
    register_aisle_routes(app)
    
    return app
