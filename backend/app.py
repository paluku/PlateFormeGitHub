from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Autorise React à communiquer avec Flask
CORS(app)


def message():
    return "Bonjour depuis Python !"


@app.route("/api/message")
def get_message():
    return jsonify({
        "message": message()
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )