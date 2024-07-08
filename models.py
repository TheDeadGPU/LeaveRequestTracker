from app import db
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_bcrypt import Bcrypt,generate_password_hash, check_password_hash
from app import create_app,db,login_manager,bcrypt

class User(UserMixin, db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pwd = db.Column(db.String(300), nullable=False, unique=True)

    def __repr__(self):
        return '<User %r>' % self.username
    def generate_reset_password_token(self,app):
        serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

        return serializer.dumps(self.email, salt=self.pwd)

    @staticmethod
    def validate_reset_password_token(token: str, user_id: int, app):
        user = db.session.get(User, user_id)

        if user is None:
            return None

        serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        try:
            token_user_email = serializer.loads(
                token,
                max_age=app.config["RESET_PASS_TOKEN_MAX_AGE"],
                salt=user.pwd,
            )
        except (BadSignature, SignatureExpired):
            return None

        if token_user_email != user.email:
            return None

        return user
    
    def set_password(self,password):
        self.pwd = bcrypt.generate_password_hash(password)
    
class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    znumber = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    hours = db.Column(db.String(100), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)
    leave_approved = db.Column(db.String(50), nullable=False)
    comments = db.Column(db.String(100), nullable=True)