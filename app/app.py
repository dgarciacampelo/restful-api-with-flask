from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "planets.db")
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI

# JSON Web Token setup.
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
# ! print(f"Using JWT_SECRET_KEY: {app.config['JWT_SECRET_KEY']}")

# Mail setup. # TODO: Check mailtrap.io
app.config["MAIL_USERNAME"] = os.environ["MAIL_USERNAME"]
app.config["MAIL_PASSWORD"] = os.environ["MAIL_PASSWORD"]
app.config["MAIL_SERVER"] = os.environ["MAIL_SERVER"]

# Database setup and model definitions.
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
mail = Mail(app)


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


@app.route("/planets", methods=["GET"])
def planets():
    planets_list = Planet.query.all()
    planets = planets_schema.dump(planets_list)
    return jsonify(planets)


@app.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message="That email already exists."), 409
    else:
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        password = request.form["password"]
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User created successfully."), 201


@app.route("/login", methods=["POST"])
def login():
    if request.is_json:
        email = request.json["email"]
        password = request.json["password"]
    else:
        email = request.form["email"]
        password = request.form["password"]

    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login succeeded!", access_token=access_token), 200
    else:
        return jsonify(message="Bad email or password"), 401


@app.route("/retrieve-password/<string:email>", methods=["GET"])
def retrieve_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message(
            "your planetary API password is " + user.password,
            sender="admin@planetary-api.com",
            recipients=[email],
        )
        mail.send(msg)
        return jsonify(message="Password sent to " + email)
    else:
        return jsonify(message="That email doesn't exist"), 401


# Database models definitions.
class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "first_name", "last_name", "email", "password")


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class Planet(db.Model):
    __tablename__ = "planets"
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)


class PlanetSchema(ma.Schema):
    class Meta:
        fields = (
            "planet_id",
            "planet_name",
            "planet_type",
            "home_star",
            "mass",
            "radius",
            "distance",
        )


planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)


# Commands for the terminal, to manage the database.
@app.cli.command("db_create")
def db_create():
    db.create_all()
    print("Database created!")


@app.cli.command("db_drop")
def db_drop():
    db.drop_all()
    print("Database dropped!")


@app.cli.command("db_seed")
def db_seed():
    db_seed_planets()
    db_seed_user()
    db.session.commit()
    print("Database seeded!")


def db_seed_planets():
    mercury = Planet(
        planet_name="Mercury",
        planet_type="Class D",
        home_star="Sol",
        mass=2.258e23,
        radius=1516,
        distance=35.98e6,
    )

    venus = Planet(
        planet_name="Venus",
        planet_type="Class K",
        home_star="Sol",
        mass=4.867e24,
        radius=3760,
        distance=67.24e6,
    )

    earth = Planet(
        planet_name="Earth",
        planet_type="Class M",
        home_star="Sol",
        mass=5.972e24,
        radius=3959,
        distance=92.96e6,
    )

    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)


def db_seed_user():
    # TODO: Hash the password.
    test_user = User(
        first_name="William",
        last_name="Herschel",
        email="test@test.com",
        password="P@ssw0rd",
    )

    db.session.add(test_user)


if __name__ == "__main__":
    # * Runs a a development server on http://127.0.0.1:5000 by default.
    # * With debug=True, the server reloads itself each time the code changes.
    app.run(debug=True)
