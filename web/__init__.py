from flask import Flask
from web.routes import main_routes


def create_app():
    app = Flask(__name__)
    # Registrar blueprints
    from web.routes.main_routes import main_bp
    #from web.views.admin_routes import admin_bp

    app.register_blueprint(main_bp)
    #app.register_blueprint(admin_blueprint)


    return app