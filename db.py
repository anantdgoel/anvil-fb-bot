from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/anvilappointments'
db = SQLAlchemy(app)

class AnvilAppointment(db.Model):
    name = db.Column(db.String)
    email = db.Column(db.String)
    appointment_date = db.Column(db.String)

    def __init__(self, name, email, appointment_date):
        self.name = name
        self.email = email
        self.appointment_date = appointment_date
