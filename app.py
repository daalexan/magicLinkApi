from flask import Flask, request
from flask import json
from flask.json import jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_mail import Mail, Message
import hashlib
import os


frontend_host_url = "http://localhost:4200/"
project_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

app.config['SECRET_KEY'] = "ca1e0daa0f36cab0a18639537a23c8e48db2ce92ca6e49d728b001fa4dc72ce8"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///{}".format(os.path.join(project_dir, "test.db"))

db = SQLAlchemy(app)
ma = Marshmallow(app)

app.config.update(dict(
    DEBUG = False,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'flaskdaniel316@gmail.com',
    MAIL_PASSWORD = 'flask.test_2130Daniel',
))

mail = Mail(app)
cors = CORS(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64))
    token = db.Column(db.String(256))
    click_count = db.Column(db.Integer)


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    id = ma.auto_field()
    email = ma.auto_field()
    token = ma.auto_field()
    click_count = ma.auto_field()


@app.route('/users', methods=['GET'])
def users():
    users = User.query.all()
    user_schema = UserSchema(many=True)
    return jsonify(user_schema.dump(users))


@app.route('/auth', methods=['POST', 'GET'])
def auth():
    if request.method == 'POST':
        user_mail = request.get_json()
        user = User.query.filter_by(email=user_mail.get('user_email')).first()
        if user is None:
            email = user_mail.get('user_email')
            token = hashlib.sha256(email.encode())
            user = User(email=user_mail.get('user_email'), token=token.hexdigest(), click_count=0)
            db.session.add(user)
            db.session.commit()
            magic_link = frontend_host_url + "auth?user_token=" + user.token
            with mail.connect() as conn:
                message = "click the link to go in your account, don't share this link with anybody " + magic_link
                subject = "magic link to your account"
                msg = Message(sender=app.config.get("MAIL_USERNAME"),
                    recipients=[user.email],
                    body=message,
                    subject=subject)
                conn.send(msg)
            user_schema = UserSchema()
            return jsonify({'status': 'success', 'user': user_schema.dump(user)})
        else:
            return jsonify("user already exist {}".format(user_mail.get('user_email')))
    elif request.method == 'GET':
        user_token = request.args.get('user_token')
        if user_token != "":
            user = User.query.filter_by(token=user_token).first()
            if user is not None:
                user.click_count += 1
                db.session.commit()
                user_schema = UserSchema()
                return jsonify(user_schema.dump(user))
            else:
                return jsonify("token not binded to user")
        return jsonify("token field empty")
    return jsonify("success"), 200


if __name__ == "__main__":
    db.create_all()
    app.run()
