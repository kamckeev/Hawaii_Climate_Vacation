import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
###
engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread': False})
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

###
from flask import request

def calc_temps(start_date, end_date):
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
def calc_temp_start(start_date):
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

###
app=Flask(__name__)
@app.route("/")
def home():
    print('Welcome to the home page')
    return (
    f"<h3>Welcome to the Hawaii Historical Weather data API!</h3>"
    f"<strong>Available Routes:</strong><br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"<br/>"
    f"<strong>Date Routes:</strong><br/>"
    f"Use the following format for start_date and end_date: 'YYYY-MM-DD'<br/>"
    f"/api/v1.0/start_date<br/>"    
    f"/api/v1.0/start_date/end_date<br/>"
    )
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
last_date_obj = dt.datetime.strptime(last_date[0], '%Y-%m-%d').date()
year_ago = last_date_obj - dt.timedelta(days=365)



@app.route("/api/v1.0/precipitation")
def precip():
    print("Precipitation data")    
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    prcp = dict(prcp_data)
    return jsonify(prcp)

@app.route("/api/v1.0/stations")
def stations():
    _station = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    return jsonify(_station)

@app.route("/api/v1.0/tobs")
def tobs(): 
    last_year_temp=session.query(Measurement.date,Measurement.tobs).filter(Measurement.date>=year_ago).all()
    table_last_temp=list(np.ravel(last_year_temp))
#     return(f"Table of dates and observed temperatures:<br/>") 
    return(jsonify(table_last_temp))

@app.route("/api/v1.0/start_date") 
def temperatures_start(start_date):
        return (jsonify(calc_temp_start(start_date)))
""" Given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than 
        and equal to the start date. 
"""


 
@app.route("/api/v1.0/start_date/end_date")
def start_end(start_date, end_date):
        return (jsonify(calc_temps(start_date, end_date)))

if __name__ == "__main__":
    app.run(debug=True)