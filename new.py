from flask import Flask, render_template, make_response, url_for, request, jsonify
import ee
import numpy as np
import cv2
from datetime import date
from dateutil.rrule import rrule,MONTHLY
import datetime
import cgi


app = Flask(__name__, static_url_path='/static')

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


polygon = None
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")


@app.route('/map')
def map():
    return render_template("test.html")


@app.route('/result', methods=['GET', 'POST'])
def result():

    if request.method == 'POST':
        print('Incoming..')
        req = request.get_json(force=True)
        #a = json.loads(req)
        global polygon
        polygon = req["geojson"]["geometry"]["coordinates"][0] # parse as JSON
        print(polygon)

    return render_template("resultnew.html")



@app.route('/code', methods=['GET', 'POST'])
def code():
    global polygon
    ee.Initialize()
    area = ee.Geometry.Polygon(polygon)
    total_sqkm = area.area().divide(1000 * 1000).getInfo()

    coll = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR").filterDate('2014-01-01', '2014-01-30')
    print(coll)
    image_area = coll.filterBounds(area)
    img = image_area.median()


@app.route('/code', methods=['GET', 'POST'])
def code():
    global polygon
    ee.Initialize()
    area = ee.Geometry.Polygon(polygon)
    total_sqkm = area.area().divide(1000 * 1000).getInfo()

    dt = datetime.date(2017, 3, 28)  # add the starting date according to your satellite, year, month, day
    q = dt.strftime("%Y-%m-%d")

    coll = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR").filterDate('2014-01-01', '2014-01-30')
    # print(coll)
    image_area = coll.filterBounds(area)
    img = image_area.median()











































