from app import db, ma

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64))
    token = db.Column(db.String(256))
    click_count = db.Column(db.Integer)

    def __init__(self, email, token, click_count):
        self.email = email
        self.token = token
        self.click_count = click_count


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Users

    id = ma.auto_field()
    email = ma.auto_field()
    token = ma.auto_field()
    click_count = ma.auto_field()
