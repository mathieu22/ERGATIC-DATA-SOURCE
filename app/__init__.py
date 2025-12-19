from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'postgresql://pappers:pappers_secure_2024@localhost:5432/sirene'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

    # Initialisation extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Enregistrement des blueprints
    from app.routes.main import main_bp
    from app.routes.search import search_bp
    from app.routes.entreprise import entreprise_bp
    from app.routes.export import export_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(entreprise_bp, url_prefix='/entreprise')
    app.register_blueprint(export_bp, url_prefix='/export')

    return app
