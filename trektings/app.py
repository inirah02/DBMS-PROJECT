from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy as alc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Password@127.0.0.1:3306/trek'
db = alc(app)

class Customer(db.Model):
    __tablename__ = 'customer'
    customer_id = db.Column(db.Integer, primary_key=True) 
    contact = db.Column(db.String(length=10))
    firstname = db.Column(db.String(length=100)) 
    lastname = db.Column(db.String(length=100)) 
    address = db.Column(db.String(length=200)) 
    email = db.Column(db.String(length=50)) 
    booking = db.relationship('Booking',backref='customer', uselist=False)
    def __repr__(self):
            return f"customer('{self.customer_id}', '{self.firstname}', '{self.lastname}', '{self.contact}', '{self.address}', '{self.email}')"

class Booking(db.Model):
    __tablename__ = 'booking'
    booking_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
    journey_id = db.Column(db.Integer, db.ForeignKey('journey.journey_id'))
    travel = db.Column(db.Boolean)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    total_cost = db.Column(db.Float)
    def __repr__(self):
            return f"booking('{self.booking_id}', '{self.customer_id}', '{self.journey_id}', '{self.travel}', '{self.start_date}', '{self.end_date}', '{self.total_cost}')"

class Journey(db.Model):
    __tablename__ = 'journey'
    journey_id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer,db.ForeignKey('trek_location.location_id'))
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.vehicle_id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.driver_id'))
    lead_id = db.Column(db.Integer, db.ForeignKey('trek_leads.lead_id'))
    booking = db.relationship('Booking',backref='journey',uselist=False)
    def __repr__(self):
            return f"journey('{self.journey_id}', '{self.location_id}', '{self.vehicle_id}', '{self.driver_id}', '{self.lead_id}')"

class Trek_location(db.Model):
    __tablename__ = 'trek_location'
    location_id = db.Column(db.Integer, primary_key=True)
    homestay_id = db.Column(db.Integer,db.ForeignKey('homestay.homestay_id'))
    duration = db.Column(db.Integer)
    description = db.Column(db.String(length=500))
    trek_cost = db.Column(db.Float)
    travel_cost = db.Column(db.Float)
    available = db.Column(db.Boolean)
    address = db.Column(db.String(length=300))
    def __repr__(self):
            return f"trek_location('{self.location_id}', '{self.homestay_id}', '{self.duration}', '{self.description}', '{self.trek_cost}', '{self.travel_cost}', '{self.available}', '{self.address}')"
    
class Homestay(db.Model):
    __tablename__ = 'homestay'
    homestay_id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(length=50)) 
    capacity = db.Column(db.Integer)
    address = db.Column(db.String(length=300))
    cost_per_day = db.Column(db.Float)
    contact = db.Column(db.String(length=10))
    trek_location = db.relationship('Trek_location',backref='homestay',uselist=False)
    def __repr__(self):
            return f"homestay('{self.homestay_id}', '{self.email}', '{self.capacity}', '{self.address}', '{self.cost_per_day}', '{self.contact}', '{self.trek_location}')"

class Driver(db.Model):
    __tablename__ = 'driver'
    driver_id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(length=300))
    firstname = db.Column(db.String(length=100))
    lastname = db.Column(db.String(length=100))
    hourly_rate = db.Column(db.Float)
    driver_contact = db.Column(db.String(length=10))
    status = db.Column(db.Boolean)
    journey = db.relationship('Journey',backref='driver',uselist=False)
    def __repr__(self):
            return f"driver('{self.driver_id}', '{self.firstname}', '{self.lastname}', '{self.address}', '{self.hourly_rate}', '{self.driver_contact}', '{self.status}')"

class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    vehicle_id = db.Column(db.Integer, primary_key=True)
    capacity = db.Column(db.Integer)
    vehicle_number = db.Column(db.String(length=10))
    status = db.Column(db.Boolean)
    journey = db.relationship('Journey',backref='vehicle',uselist=False)
    def __repr__(self):
            return f"vehicle('{self.vehicle_id}', '{self.capacity}', '{self.vehicle_number}', '{self.status}')"

class Trek_leads(db.Model):
    __tablename__ = 'trek_leads'
    lead_id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(length=100))
    lastname = db.Column(db.String(length=100))
    lead_contact = db.Column(db.String(length=10))
    daily_rate = db.Column(db.Float)
    status = db.Column(db.Boolean)
    journey = db.relationship('Journey',backref='trek_leads',uselist=False)
    def __repr__(self):
            return f"trek_leads('{self.lead_id}', '{self.firstname}', '{self.lastname}', '{self.lead_contact}', '{self.lead_contact}', '{self.daily_rate}', '{self.status}')"

with app.app_context():
    db.create_all();

@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Customer(firstname=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except:
            return "There was an issue adding your task"
    else:
        tasks = Trek_location.query.all()
        return render_template('index.html',tasks=tasks) 

@app.route('/admin')
def admin():
    return render_template('admin.html') 

@app.route('/location', methods=['POST','GET'])
def location():
    if request.method == "POST":
        pass
    else:
        columns = Trek_location.__table__.columns
        column_names = [column.name for column in columns]
        tasks = Trek_location.query.all()
        return render_template('manage.html', tasks=tasks, column_names = column_names) 

@app.route('/vehicle', methods=['POST','GET'])
def vehicle():
    if request.method == "POST":
        pass
    else:
        columns = Vehicle.__table__.columns
        column_names = [column.name for column in columns]
        tasks = Vehicle.query.all()
        return render_template('manage.html', tasks=tasks, column_names = column_names) 

@app.route('/driver', methods=['POST','GET'])
def driver():
    if request.method == "POST":
        pass
    else:
        columns = Driver.__table__.columns
        column_names = [column.name for column in columns]
        tasks = Driver.query.all()
        return render_template('manage.html', tasks=tasks, column_names = column_names) 

@app.route('/leads', methods=['POST','GET'])
def leads():
    if request.method == "POST":
        pass
    else:
        columns = Trek_leads.__table__.columns
        column_names = [column.name for column in columns]
        tasks = Trek_leads.query.all()
        return render_template('manage.html', tasks=tasks, column_names = column_names) 

@app.route('/homestay', methods=['POST','GET'])
def homestay():
    if request.method == "POST":
        pass
    else:
        columns = Homestay.__table__.columns
        column_names = [column.name for column in columns]
        tasks = Homestay.query.all()
        return render_template('manage.html', tasks=tasks, column_names = column_names) 

@app.route('/customer', methods=['POST','GET'])
def customer():
    if request.method == "POST":
        pass
    else:
        columns = Customer.__table__.columns
        column_names = [column.name for column in columns]
        tasks = Customer.query.all()
        return render_template('manage.html', tasks=tasks, column_names = column_names) 

@app.route('/journey', methods=['POST','GET'])
def journey():
    if request.method == "POST":
        pass
    else:
        columns = Journey.__table__.columns
        column_names = [column.name for column in columns]
        tasks = Journey.query.all()
        return render_template('manage.html', tasks=tasks, column_names = column_names) 

@app.route('/booking', methods=['POST','GET'])
def booking():
    if request.method == "POST":
        pass
    else:
        columns = Booking.__table__.columns
        column_names = [column.name for column in columns]
        tasks = Booking.query.all()
        return render_template('manage.html', tasks=tasks, column_names = column_names) 

if __name__ == "__main__":
    app.run(debug=True)
