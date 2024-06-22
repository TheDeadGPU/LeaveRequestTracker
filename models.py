from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pwd = db.Column(db.String(300), nullable=False, unique=True)

    def __repr__(self):
        return '<User %r>' % self.username
    
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