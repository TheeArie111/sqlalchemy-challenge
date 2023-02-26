
#  Import Flask and other dependencies
from flask import Flask
import numpy as np
import pandas as pd
import datetime as dt
from datetime import date
import os.path

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import inspect
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify


### DataBase Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
connection = engine.connect()

# Reflect an existing database into new model
Base = automap_base()
#reflect tables
Base.prepare(engine, reflect=True)

#Save references to each table in a variable
Measurement = Base.classes.measurement
Station = Base.classes.station


### Setup Flask App
app = Flask(__name__)


##### Define static routes/ Homepage-------------------------------------------------------- 
@app.route("/")
def index():
    return (
          f"This is the Homepage.<br/>"
          f"All the available routes: <br/>"
          f"/api/v1.0/precipitation <br/>"
          f"/api/v1.0/stations <br/>"
          f"/api/v1.0/tobs <br/>"
          f"/api/v1.0/start <br/>"
          f"/api/v1.0/startend <br/>"
    )

##### Precipitation-------------------------------------------------------- 
@app.route("/api/v1.0/precipitation")
def precipitation():
        session = Session(engine)
        most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
        # The most resent date as string
        most_recent_date_str = most_recent_date.date

# convert that string to datatime
        most_recentdt = date.fromisoformat(most_recent_date_str)

# Calculate the date one year from the last date in data set.
        one_year_ago = date((most_recentdt.year - 1), most_recentdt.month, most_recentdt.day).isoformat()

# Perform a query to retrieve the data and precipitation scores
        data = session.query(Measurement.date, Measurement.prcp).\
                filter (Measurement.date > one_year_ago).all()

# Save the query results as a Pandas DataFrame and set the index to the date column
        df = pd.DataFrame(data, columns =['Date', 'Prcp'])
        PrecipData = df.set_index('Date')

# Sort the dataframe by date
        PrecipData.sort_index(inplace = True, ascending=True)
        PrecipData = PrecipData.dropna(how='any')
        prcp_dic = PrecipData.to_dict()
        prcp_dic
        return jsonify(prcp_dic)

        


##### Stations-------------------------------------------------------- 
@app.route("/api/v1.0/stations")
def stations():
        session = Session(engine)
        results = session.query(Measurement.station).distinct().all()
        session.close()

         # Convert list of tuples into normal list
        all_stations = list(np.ravel(results))


        return jsonify(all_stations)




##### Temperature-------------------------------------------------------- 
# Query the dates and temperature observations of the most active station for the previous year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
        session = Session(engine)
        most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
        # The most resent date as string
        most_recent_date_str = most_recent_date.date

# convert that string to datatime
        most_recentdt = date.fromisoformat(most_recent_date_str)

# Calculate the date one year from the last date in data set.
        one_year_ago = date((most_recentdt.year - 1), most_recentdt.month, most_recentdt.day).isoformat()

        results = session.query(Measurement.date, Measurement.station, Measurement.prcp).\
                filter (Measurement.date > one_year_ago).all()
        session.close()

        df = pd.DataFrame(results, columns =['Date', 'Station', 'Prcp'])
        PrecipData = df.set_index('Date')
        activity = PrecipData.groupby(['Station']).size().sort_values(ascending=False)
        most_active = activity.index[0]

        tempresults = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date > one_year_ago).\
                filter(Measurement.station== most_active).all()
        session.close()

        df_temps = pd.DataFrame(tempresults, columns =['Date', 'Temperature from station USC00519397'])
        dfi_temps = df_temps.set_index('Date')
        dfi_temps = dfi_temps.dropna(how='any')
        dfi_temps.sort_index(inplace = True, ascending=True)

        temp_dic = dfi_temps.to_dict()
        #temp_dic
        return jsonify(temp_dic)



##### Start Page-------------------------------------------------------- 
@app.route("/api/v1.0/start")
def start():
        return f"the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range."




##### Start and End Page-------------------------------------------------------- 
@app.route("/api/v1.0/startend")
def startend():
        return f"the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range."


# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)

