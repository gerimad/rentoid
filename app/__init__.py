from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from app.llm.inference import InferenceEngine
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()
infer = InferenceEngine()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .llm import llm as llm_blueprint
    app.register_blueprint(llm_blueprint)

    return app