# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import flask
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Measurements = Base.classes.measurement
Stations = Base.classes.station

# Create our session (link) from Python to the DB
link = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

  # Find the most recent date in the data set.
  recent_date = link.query(Measurements.date).order_by(Measurements.date.desc()).first().date
  recent_date

  # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
  # Starting from the most recent data point in the database. 
  recent_date = link.query(Measurements.date).order_by(Measurements.date.desc()).first().date

  # Calculate the date one year from the last date in data set.
  one_year = dt.date(2017,8,23) - dt.timedelta(days= 365)
  print(one_year)

  # Perform a query to retrieve the data and precipitation scores

  pre = link.query(Measurements.date, Measurements.prcp).\
    filter(Measurements.date >= one_year, Measurements.prcp != None).\
    order_by(Measurements.date).all()

  return jsonify(dict(pre))

@app.route("/api/v1.0/stations")
def stations():
  
  # Design a query to calculate the total number of stations in the dataset
  link.query(Measurements.station).distinct().count()

  # Design a query to find the most active stations (i.e. which stations have the most rows?)
  # List the stations and their counts in descending order.
  stations = link.query(Measurements.station,func.count(Measurements.station)).\
                               group_by(Measurements.station).\
                               order_by(func.count(Measurements.station).desc()).all()
  stations
  return jsonify(dict(stations))

@app.route("/api/v1.0/tobs")
def tobs():
  
  # Using the most active station id
  # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
  temp_months = link.query(Measurements.tobs).\
      filter(Measurements.date >= one_year, Measurements.station == 'USC00519281').\
      order_by(Measurements.tobs).all()

  da_frame = pd.DataFrame(temp_months, columns=['Tobs'])

  return jsonify(dict(tobs))

@app.route("/api/v1.0/<start>")
def temp():

   # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
  sum_temp = link.query(func.min(Measurements.tobs), func.max(Measurements.tobs),\
                      func.avg(Measurements.tobs)).\
                      filter(Measurements.station == 'USC00519281' ).all()
  sum_temp
  return jsonify(dict(temp))

if __name__ == '__main__':
    app.run(debug=True)
