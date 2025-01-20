from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.sql import func

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    creation_date = db.Column(db.DateTime, server_default=func.now()) 
    date_of_birth = db.Column(db.Date, nullable=True) 
    goal = db.Column(db.String(100), nullable=True)

    # Relationship to Plan
    plans = db.relationship('Plan', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    

class Lift(db.Model):
    __tablename__ = 'lifts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    targeted_area = db.Column(db.String(30), nullable=False)
    # Relationship to PlanLift 
    plan_lifts = db.relationship('PlanLift', backref='lift', lazy=True, cascade="all, delete-orphan")

class Plan(db.Model):
    __tablename__ = 'plans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    plan_type = db.Column(db.String(50), nullable=True) 
    plan_duration = db.Column(db.String(50), nullable=True)
    creation_date = db.Column(db.DateTime, server_default=func.now()) 

    # Relationship to PlanLift
    plan_lifts = db.relationship('PlanLift', backref='plan', lazy=True, cascade="all, delete-orphan")

class PlanLift(db.Model):
    __tablename__ = 'plan_lifts'
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=False)
    lift_id = db.Column(db.Integer, db.ForeignKey('lifts.id'), nullable=False)
    sets = db.Column(db.Integer, nullable=True, default=3)
    reps = db.Column(db.Integer, nullable=True, default=10)

    # Relationship to LiftPerformance
    performances = db.relationship('LiftPerformance', backref='plan_lift', lazy=True, cascade="all, delete-orphan")

class LiftPerformance(db.Model):
    __tablename__ = 'lift_performances'
    id = db.Column(db.Integer, primary_key=True)
    plan_lift_id = db.Column(db.Integer, db.ForeignKey('plan_lifts.id'), nullable=False)
    lift_id = db.Column(db.Integer, db.ForeignKey('lifts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    reps_performed = db.Column(db.Integer, nullable=False)
    weight_performed = db.Column(db.Float, nullable=False)
    reps_in_reserve = db.Column(db.Integer, nullable=False)
    recommended_weight = db.Column(db.Float, nullable=True)
    additional_notes = db.Column(db.Text, nullable=True)

    user = db.relationship('User', backref='lift_performances', lazy=True)
    lift = db.relationship('Lift', backref='lifts',lazy=True)