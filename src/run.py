from flask import Flask
from controllers.robustness_controller import robustnesstest_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(robustnesstest_bp)
    return app

if __name__ == '__main__':  
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=False)  # Runs the Flask server
