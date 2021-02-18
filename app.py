from flask import Flask, request
from flask import json
from flask.json import jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_mail import Mail, Message
import hashlib
import os


frontend_host_url = "https://magiclinkview.herokuapp.com/"
project_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

from models import UserSchema, Users


@app.route('/users', methods=['GET'])
def users():
    users = Users.query.all()
    user_schema = UserSchema(many=True)
    return jsonify(user_schema.dump(users))


@app.route('/auth', methods=['POST', 'GET'])
def auth():
    if request.method == 'POST':
        user_mail = request.get_json()
        user = Users.query.filter_by(email=user_mail.get('user_email')).first()
        if user is None:
            email = user_mail.get('user_email')
            token = hashlib.sha256(email.encode())
            user = Users(email=user_mail.get('user_email'), token=token.hexdigest(), click_count=0)
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
            user = Users.query.filter_by(token=user_token).first()
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
    app.run()
