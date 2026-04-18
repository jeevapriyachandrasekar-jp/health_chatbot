from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'public' or 'officer'

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disease = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(300))
    created_by = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
