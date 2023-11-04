from flask import Flask, jsonify


app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello World!"


@app.route("/super-simple")
def super_simple():
    return jsonify(message="Hello from the Planetary API, nice."), 200


if __name__ == "__main__":
    # * Runs a a development server on http://127.0.0.1:5000 by default.
    # * With debug=True, the server reloads itself each time the code changes.
    app.run(debug=True)
