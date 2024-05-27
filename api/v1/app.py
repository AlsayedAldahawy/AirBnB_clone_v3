#!/usr/bin/python3
"""Flask app"""


from flask import Flask, jsonify
from api.v1.views import app_views
from models import storage
from werkzeug.exceptions import NotFound
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "0.0.0.0"}})

app.register_blueprint(app_views)


@app.teardown_appcontext
def teardown_db(exception):
    """Remove the current SQLAlchemy Session"""
    storage.close()


@app.errorhandler(NotFound)
def not_found(error):
    """Return a JSON-formatted 404 status code response"""
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    """Main function"""
    import os
    host = os.getenv("HBNB_API_HOST", "0.0.0.0")
    port = int(os.getenv("HBNB_API_PORT", 5000))
    app.run(host=host, port=port, threaded=True)
