from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String

engine = None
appointments = None

def initialize_database():
    global engine
    engine = sqlalchemy.create_engine('postgresql://localhost/anvilappointments')

    meta = sqlalchemy.MetaData(bind=engine, reflect=True)

    global appointments
    appointments = Table('appointments', meta,
        Column('name', String),
        Column('email', String),
        Column('appointmentdate', String)               
    )

    meta.create_all(engine)

def insert(appointee, appointee_email, appointee_appointment_date):
    clause = appointments.insert().values(name=appointee, email=appointee_email, appointmentdate=appointee_appointment_date)
    
    engine.execute(clause)

    print 'insert() executed'

def print_table():
    results = meta.tables['appointments']

    for row in engine.execute(results.select()):
        print row

