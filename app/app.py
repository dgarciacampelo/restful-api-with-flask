from flask import Flask, jsonify, request


app = Flask(__name__)


@app.route("/")
def hello_world():
    return jsonify(message="Hello World!"), 200


@app.route("/super-simple")
def super_simple():
    return jsonify(message="Hello from the Planetary API."), 200


@app.route("/not-found")
def not_found():
    return jsonify(message="That resource was not found"), 404


@app.route("/parameters")
def parameters():
    try:
        name = request.args.get("name")
        age = int(request.args.get("age"))
        if age < 18:
            return jsonify(message="Sorry " + name + ", you are not old enough."), 401
        else:
            return jsonify(message="Welcome " + name + ", you are old enough!"), 200
    # If any of the parameters are missing, return a internal server error.
    except:
        return jsonify(message="Some error occurred"), 500


@app.route("/url-variables/<string:name>/<int:age>")
def url_variables(name: str, age: int):
    # Because the route takes age as int, no need of try-except block.
    if age < 18:
        return jsonify(message="Sorry " + name + ", you are not old enough."), 401
    else:
        return jsonify(message="Welcome " + name + ", you are old enough!"), 200


if __name__ == "__main__":
    # * Runs a a development server on http://127.0.0.1:5000 by default.
    # * With debug=True, the server reloads itself each time the code changes.
    app.run(debug=True)
