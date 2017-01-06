from app import db

class AnvilAppointment(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    appointment_date = db.Column(db.String)

    def __init__(self, name, email, appointment_date):
        self.name = name
        self.email = email
        self.appointment_date = appointment_date
