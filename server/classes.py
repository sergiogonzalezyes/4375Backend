from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Numeric, Float
from sqlalchemy.orm import relationship
from .db import Base, engine
from datetime import datetime


class User(Base):
    __tablename__ = 'User'

    User_ID = Column(Integer, primary_key=True, autoincrement=True)
    Username = Column(String(15), unique=True, index=True)
    Password = Column(String(70))
    F_Name = Column(String(15), nullable=False)
    L_Name = Column(String(15), nullable=False)
    User_Type = Column(String(15), default='Guest', nullable=False)  # Can be "admin", "barber", "customer", "guest"
    Email = Column(String(25), unique=True, nullable=False)
    Phone_Number = Column(String(10), unique=True, nullable=False)

    schedules = relationship('Schedule', backref='user')
    appointments_as_requester = relationship('Appointment', foreign_keys='Appointment.Customer_User_ID', backref='requester')
    appointments_as_provider = relationship('Appointment', foreign_keys='Appointment.Barber_User_ID', backref='provider')
    notifications = relationship('Notification', backref='user')
    histories = relationship('Customer_History', backref='user')
    holidays = relationship('Holiday', backref='user')
    blacklist_entries = relationship('Blacklist', backref='user')


class Schedule(Base):
    __tablename__ = 'Schedule'

    Schedule_ID = Column(Integer, primary_key=True, autoincrement=True)
    Barber_User_ID = Column(Integer, ForeignKey('User.User_ID'), nullable=False)
    Day_Of_Week = Column(String(9), nullable=False)
    Start_Time = Column(DateTime, nullable=False)
    End_Time = Column(DateTime, nullable=False)
    Status = Column(String(12), default='Available', nullable=False)


class Appointment(Base):
    __tablename__ = 'Appointment'

    Appointment_ID = Column(Integer, primary_key=True, autoincrement=True)
    F_Name = Column(String(15), nullable=False)
    L_Name = Column(String(15), nullable=False)
    Email = Column(String(25), unique=True, nullable=False)
    Phone_Number = Column(String(10), unique=True, nullable=False)
    Customer_User_ID = Column(Integer, ForeignKey('User.User_ID'), nullable=False)
    Barber_User_ID = Column(Integer, ForeignKey('User.User_ID'), nullable=False)
    Appointment_Date_Time = Column(DateTime, nullable=False)
    Appointment_End_Date_Time = Column(DateTime, nullable=False)
    Status = Column(String(10), nullable=False)
    Payment_ID = Column(Integer, ForeignKey('Payment.Payment_ID'))
    Service_ID = Column(Integer, ForeignKey('Service.Service_ID'))
    Schedule_ID = Column(Integer, ForeignKey('Schedule.Schedule_ID'))

    reviews = relationship('Review', backref='appointment')
    notifications = relationship('Notification', backref='appointment')
    customer_histories = relationship('Customer_History', backref='appointment')
    appointment_schedule = relationship('Schedule', backref='appointment')



class Service(Base):
    __tablename__ = 'Service'

    Service_ID = Column(Integer, primary_key=True, autoincrement=True)
    Service_Name = Column(String(25), unique=True, nullable=False)
    Service_Description = Column(String(200), unique=True, nullable=False)
    Service_Price = Column(Numeric(precision=10, scale=2), nullable=False)
    Service_Duration = Column(String(15), nullable=False)
    

class Notification(Base):
    __tablename__ = 'Notification'

    Notification_ID = Column(Integer, primary_key=True, autoincrement=True)
    User_ID = Column(Integer, ForeignKey('User.User_ID'), nullable=False)
    Appointment_ID = Column(Integer, ForeignKey('Appointment.Appointment_ID'), nullable=False)
    Message = Column(String(255), nullable=False)
    Notification_Type = Column(String(15), nullable=False)
    Notification_Date_Time = Column(DateTime, nullable=False)
    Notification_Status = Column(String(15), nullable=False)


class Payment(Base):
    __tablename__ = 'Payment'

    Payment_ID = Column(Integer, primary_key=True, autoincrement=True)
    Payment_Type_ID = Column(Integer, ForeignKey('Payment_Type.Payment_Type_ID'), nullable=False)
    Payment_Amount = Column(Numeric(scale=2, precision=10), nullable=True)
    Payment_Date = Column(DateTime, nullable=False)

    appointments = relationship('Appointment', backref='payment')


class Payment_Type(Base):
    __tablename__ = 'Payment_Type'

    Payment_Type_ID = Column(Integer, primary_key=True, autoincrement=True)
    Payment_Type_Name = Column(String(20), nullable=False)




class Review(Base):
    __tablename__ = 'Review'

    Review_ID = Column(Integer, primary_key=True, autoincrement=True)
    Rating = Column(Integer, nullable=False)
    Comment = Column(String(255), nullable=True)
    Appointment_ID = Column(Integer, ForeignKey('Appointment.Appointment_ID'), nullable=False)


class Customer_History(Base):
    __tablename__ = 'Customer_History'

    History_ID = Column(Integer, primary_key=True, autoincrement=True)
    User_ID = Column(Integer, ForeignKey('User.User_ID'), nullable=False)
    Services_Done = Column(String(255), nullable=False)
    Appointment_ID = Column(Integer, ForeignKey('Appointment.Appointment_ID'), nullable=False)
    Payment_Made = Column(Float, nullable=False)
    Visit_Date = Column(DateTime, nullable=False)


class Holiday(Base):
    __tablename__ = 'Holiday'

    Holiday_ID = Column(Integer, primary_key=True, autoincrement=True)
    Date_Time = Column(DateTime, nullable=False)
    Description = Column(String(255), nullable=False)
    User_ID = Column(Integer, ForeignKey('User.User_ID'), nullable=False)


class Blacklist(Base):
    __tablename__ = 'Blacklist'

    Blacklist_ID = Column(Integer, primary_key=True, autoincrement=True)
    User_ID = Column(Integer, ForeignKey('User.User_ID'), nullable=False)
    Blacklist_Reason = Column(String(255), nullable=False)
    Blacklist_Date = Column(DateTime, nullable=True)

class Barber_Service(Base):
    __tablename__ = 'Barber_Service'

    Barber_Service_ID = Column(Integer, primary_key=True, autoincrement=True)
    Barber_User_ID = Column(Integer, ForeignKey('User.User_ID'), nullable=False)
    Service_ID = Column(Integer, ForeignKey('Service.Service_ID'), nullable=False)

    # Add relationships
    barber = relationship('User', backref='barber_services')
    service = relationship('Service', backref='barber_services')


# create a function that pulls from the user table
def get_user(username):
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter_by(Username=username).first()
    return user


