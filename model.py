from app import db

class AnvilAppointment(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    appointment_date = db.Column(db.String)

    def __init__(self):
        #self.name = name
        #self.email = email
        #self.appointment_date = appointment_date

    def set_name(self, name):
        self.name = name

    def set_email(self, email):
        self.email = email

    def set_date(self, date):
        self.appointment_date = date
