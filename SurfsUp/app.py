# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, inspect, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base=automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement=Base.classes.measurement
Station=Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

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
        f"Hawaii Weather API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/start/end"
    )
@app.route("/api/v1.0/precipitation")
def precip():
    session=Session(engine)
    
    # Calculate the date one year from the last date in data set.
    previous_year=dt.date(2017,8,23)-dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precip_scores_pastyear=session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >=previous_year).all()
    
    session.close()
    
    precipitation=[]
    for date, prcp in precip_scores_pastyear:
        pastyear_precip_dict={}
        pastyear_precip_dict['Date']=date
        pastyear_precip_dict['Precip']=prcp
        precipitation.append(pastyear_precip_dict)
    
    
    return jsonify(precipitation)

@app.route("/api/v1.0/station")
def station():
    session=Session(engine)
    
    list_of_stations=session.query(Station.station, Station.id, Station.name, Station.elevation).all()
    
    session.close()
    
    station_details=[]
    for station, id, name, elevation in list_of_stations:
        station_dict={}
        station_dict["Station"]=station
        station_dict["Station ID"]=id
        station_dict["Station Name"]=name
        station_dict["Station Elevation"]=elevation
        station_details.append(station_dict)
        
    return jsonify(station_details)

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    
    # Calculate the date one year from the last date in data set.
    most_recent_date_station=session.query(Measurement.date).\
    filter(Measurement.station=='USC00519281').\
    order_by(Measurement.date.desc()).first()

    previous_year_station=dt.date(2017,8,18)-dt.timedelta(days=365)

    temps_pastyear_station=session.query(Measurement.station,Measurement.tobs).filter(Measurement.date >= previous_year_station).\
    order_by(Measurement.tobs.desc()).all()
    
    session.close()
    
    most_active_station=[]
    for date, tobs in temps_pastyear_station:
        top_station_dict={}
        top_station_dict["Date"]=date
        top_station_dict["Temp Obs"]=tobs
        most_active_station.append(top_station_dict)
    
    
    return jsonify(most_active_station)


@app.route("/api/v1.0/temp/start")
def start_temp_obs(start):
    session=Session(engine)
    
    #stats_temp_obs = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    #if not end:
            #start = dt.datetime.strptime(start, "%m%d%Y")
            #results = session.query(*sel).\
            #filter(Measurement.date >= start).all()
    stats_temp_obs=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs).\
                    filter(Measurement.date >= start)).limit(200)
    session.close()
    
    start_date_temps=list(np.ravel(stats_temp_obs))
    start_date_temps
    #start_temps=[]
    #for min, avg, max in stats_temp_obs:
        #start_temp_dict={}
        #start_temp_dict["Minimum"]=min
        #start_temp_dict["Average"]=avg
        #start_temp_dict["Maximum"]=max
        #start_temps.append(start_temp_dict)

    
    return jsonify(start_date_temps)

                                 
@app.route("/api/v1.0/start/end")
def start_end_temp_obs(start, end):
    session=Session(engine)

    tempobs_start_end=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs).filter(Measurement.date >= start).filter(Measurement.date <= end)).all()
    
    start_end_temps=[]
    for min, avg, max in tempobs_start_end:
        start_end_dict={}
        start_end_dict["Minimum"]=min
        start_end_dict["Average"]=avg
        start_end_dict["Maximum"]=max
        start_end_temps.append(start_end_dict)

    return jsonify(start_end_temps)

                                 
if __name__ == "__main__":
    app.run(debug=False)