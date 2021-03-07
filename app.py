#################################################
# Dependencies
#################################################

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    # List all available api routes
    return (
        f"Welcome to the Hawaii Weather API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Available Routes with Variable Input:<br/>"
        f"/api/v1.0/2016-04-01<br/>"
        f"/api/v1.0/2016-04-01/2017-04-01<br/><br/>"
        f"NOTICE:<br/>"
        f"Please input the query date in ISO date format(YYYY-MM-DD),<br/>"
        f"and the start date should not be later than 2017-08-23."
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all the precipitation measurements
    result = session.query(Measurement.date, Measurement.prcp).all()
    
    # Close Session
    session.close()
    # Create a dictionary from the row data and append to a list of all_passengers
        
    # Create a list of dictionaries with all the precipitation measurements
    all_prcp = []
    for date, prcp in result:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)



@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find out all the station
    stations = session.query(Station.station).distinct().all()
    
    # Close Session
    session.close()

    # Create a list of dictionaries with all the stations
    station_list = []
    for i in range(len(stations)):
        station_dict = {}
        name = f'Station {i + 1}'
        station_dict[name] = stations[i]
        station_list.append(station_dict)

    return jsonify(station_list)



@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find out the most recent date in the data set and convert it to date format
    recent_date = session.query(Measurement).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(recent_date.date, '%Y-%m-%d').date()

    # Retrieve the last 12 months of temperature data
    query_date = last_date - dt.timedelta(days=364)

    # Set up the list for query and find out the most active station
    active_station_lst = [Measurement.station, func.count(Measurement.station)]
    active_station = session.query(*active_station_lst).group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).first().station

    # Pick out last 12 months of temperature measurements of the most active station throughout 
    active_station_temp = session.query(Measurement.date, Measurement.tobs).\
                        filter(func.strftime('%Y-%m-%d', Measurement.date) > query_date).\
                        filter(Measurement.station == active_station).all()
    
    # Close Session
    session.close()

    # Create a list of dictionaries with the date and temperature with for loop
    all_temp = []
    for date, temp in active_station_temp:
        temp_dict = {}
        temp_dict['Date'] = date
        temp_dict['Temperature'] = temp
        all_temp.append(temp_dict)

    return jsonify(all_temp)



@app.route("/api/v1.0/<start>")
def date_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Change the date in string format to datatime.date
    query_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    
    # Set up the list for query
    temp_list = [func.min(Measurement.tobs), 
             func.max(Measurement.tobs), 
             func.avg(Measurement.tobs)]

    # Filter out the measurements between the query date
    date_temp = session.query(*temp_list).\
                filter(func.strftime('%Y-%m-%d', Measurement.date) >= query_date).all()
    
    # Close Session
    session.close()
    # Create a dictionary from the row data and append to a list of all_passengers

    return (
        f"Analysis of temperature from {start} to 2017-08-23 (the latest measurement in database):<br/>"
        f"Minimum temperature: {round(date_temp[0][0], 1)} °F<br/>"
        f"Maximum temperature: {round(date_temp[0][1], 1)} °F<br/>"
        f"Average temperature: {round(date_temp[0][2], 1)} °F"
    )



@app.route("/api/v1.0/<start>/<end>")
def date_start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Change the date in string format to datatime.date
    query_date_start = dt.datetime.strptime(start, '%Y-%m-%d').date()
    query_date_end = dt.datetime.strptime(end, '%Y-%m-%d').date()
    
    # Set up the list for query
    temp_list = [func.min(Measurement.tobs), 
             func.max(Measurement.tobs), 
             func.avg(Measurement.tobs)]

    # Pick out the measurements between the query date
    date_temp = session.query(*temp_list).\
                filter(func.strftime('%Y-%m-%d', Measurement.date) >= query_date_start).\
                filter(func.strftime('%Y-%m-%d', Measurement.date) <= query_date_end).all()
    
    # Close Session
    session.close()

    return (
        f"Analysis of temperature from {start} to {end}:<br/>"
        f"Minimum temperature: {round(date_temp[0][0], 1)} °F<br/>"
        f"Maximum temperature: {round(date_temp[0][1], 1)} °F<br/>"
        f"Average temperature: {round(date_temp[0][2], 1)} °F"
    )



if __name__ == '__main__':
    app.run(debug=True)
