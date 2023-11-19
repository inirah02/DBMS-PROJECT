from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import Table, MetaData, text
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Password@127.0.0.1:3306/trek'
db = SQLAlchemy(app)

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

    drop_trigger_sql = "DROP TRIGGER IF EXISTS delete_related_journeys;"
    db.session.execute(db.text(drop_trigger_sql))

    trigger_sql = """
    CREATE TRIGGER delete_related_journeys
    BEFORE DELETE ON trek_location
    FOR EACH ROW
    BEGIN
        DELETE FROM journey WHERE journey.location_id = OLD.location_id;
    END;
    """
    db.session.execute(db.text(trigger_sql))

@app.route('/')
def index():
    tasks = Trek_location.query.all()
    return render_template('index.html',tasks=tasks) 

@app.route('/admin')
def admin():
    return render_template('admin.html') 

@app.route('/admin/add/<dbtable>', methods=['POST','GET'])
def create(dbtable):

    table_name = dbtable.capitalize()
    try:
        model_class=getattr(sys.modules[__name__],table_name)
    except:
        return 'There was an error deleting that task'

    if request.method == "POST":
        columns = model_class.__table__.columns
        column_names = [column.name for column in columns]
        task_values=[]
        form_data_types = {
            int: int,
            str: str,
            bool: bool,
            float: float
        }

        for i in range(len(column_names)):
            column = columns[i]
            column_name = column_names[i]
            form_value = request.form[column_name]

            if column.type.python_type in form_data_types:
                converted_value = form_data_types[column.type.python_type](form_value)
            else:
                converted_value = form_value  

            task_values.append(converted_value)

        kwargs = dict(zip(column_names, task_values))
        new_task = model_class(**kwargs)

        try:
            db.session.add(new_task)
            db.session.commit()
            redirect_uri = '/admin/' + dbtable
            return redirect(redirect_uri)
        except Exception as e:
            print(f"Error: {e}")
            return "There was an error adding your entry. Try again"
    else:
        columns = model_class.__table__.columns
        return render_template('add.html', columns = columns, table_uri=dbtable) 

@app.route('/admin/<dbtable>')
def read(dbtable):

    table_name = dbtable.capitalize()
    try:
        model_class=getattr(sys.modules[__name__],table_name)
    except:
        return 'There was an error'

    columns = model_class.__table__.columns
    id_column = columns[0].name.strip()
    tasks = model_class.query.all()
    return render_template('manage.html', table_name=dbtable, tasks=tasks, columns = columns, id_column=id_column) 

@app.route('/admin/update/<dbtable>/<int:id>', methods=['POST','GET'])
def update(id,dbtable):
    table_name = dbtable.capitalize()
    try:
        model_class=getattr(sys.modules[__name__],table_name)
    except:
        return 'There was an error deleting that task'
    
    task_to_update = model_class.query.get_or_404(id)
    
    if request.method == "POST":
        columns = model_class.__table__.columns
        column_names = [column.name for column in columns]
        for column_name in column_names:
            if column_name == 'status':
                setattr(task_to_update, column_name, 1)
            else:
                setattr(task_to_update, column_name, request.form[column_name])
        try:
            db.session.commit()
            redirect_uri = '/admin/' + dbtable
            return redirect(redirect_uri)
        except Exception as e:
            print(f"Error: {e}")
            return "There was an error adding your entry. Try again"
    else:
        columns = model_class.__table__.columns
        return render_template('update.html',task_to_update=task_to_update, columns = columns, table_uri=dbtable) 

@app.route('/admin/delete/<dbtable>/<int:id>')
def delete(id,dbtable):

    table_name = dbtable.capitalize()
    try:
        model_class=getattr(sys.modules[__name__],table_name)
    except:
        return 'There was an error deleting that task'

    task_to_delete = model_class.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete) 
        db.session.commit()
        redirect_uri = '/admin/' + dbtable
        return redirect(redirect_uri)
    except Exception as e:
        print(f"Error: {e}")
        return "There was an error adding your entry. Try again"


if __name__ == "__main__":
    app.run(debug=True)
