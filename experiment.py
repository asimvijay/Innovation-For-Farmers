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

    coll = ee.ImageCollection("COPERNICUS/S2_SR")

    image_area = coll.filterBounds(area)
    img = image_area.median()


    bands = ["B4", "B3", "B2"]
    band_outputs = {}
    #red
    for band in bands:

        image = img.select(band).rename(["temp"])

        latlon = ee.Image.pixelLonLat().addBands(image)

        latlon = latlon.reduceRegion(
            reducer=ee.Reducer.toList(),
            geometry=area,
            maxPixels=1e8,
            scale=10)

        data = np.array((ee.Array(latlon.get("temp")).getInfo()))
        lats = np.array((ee.Array(latlon.get("latitude")).getInfo()))
        lons = np.array((ee.Array(latlon.get("longitude")).getInfo()))

        #get the unique coordinates
        uniqueLats = np.unique(lats)
        uniqueLons = np.unique(lons)

        #get number of columns and rows from coordinates
        ncols = len(uniqueLons)
        nrows = len(uniqueLats)

        #determine pixelsizes
        ys = uniqueLats[1] - uniqueLats[0]
        xs = uniqueLons[1] - uniqueLons[0]

        #create an array with dimensions of image
        arr = np.zeros([nrows, ncols], np.float32)  # -9999

        # fill the array with values
        counter = 0
        for y in range(0, len(arr), 1):
            for x in range(0, len(arr[0]), 1):
                if lats[counter] == uniqueLats[y] and lons[counter] == uniqueLons[x] and counter < len(lats) - 1:
                    counter += 1
                    arr[len(uniqueLats) - 1 - y, x] = data[counter]  # we start from lower left corner
        band_outputs[band] = arr

    r = np.expand_dims(band_outputs["B4"], -1).astype("float32")
    g = np.expand_dims(band_outputs["B3"], -1).astype("float32")
    b = np.expand_dims(band_outputs["B2"], -1).astype("float32")
    rgb = np.concatenate((r, g, b), axis=2) / 3000

    coll = ee.ImageCollection("COPERNICUS/S2_SR")

    image_area = coll.filterBounds(area)
    img = image_area.median()

    RED = img.select("B4")
    NIR = img.select("B8")
    NDVI = ee.Image(img.subtract(RED).divide(NIR.add(RED)))

    #get the lat lon and add the ndvi
    latlon = ee.Image.pixelLonLat().addBands(NDVI)

    #apply reducer to list
    latlon = latlon.reduceRegion(
        reducer=ee.Reducer.toList(),
        geometry=area,
        maxPixels=1e8,
        scale=10)

    data = np.array((ee.Array(latlon.get("B8")).getInfo()))
    lats = np.array((ee.Array(latlon.get("latitude")).getInfo()))
    lons = np.array((ee.Array(latlon.get("longitude")).getInfo()))
    print(data.shape)
    #get the unique coordinates
    uniqueLats = np.unique(lats)
    uniqueLons = np.unique(lons)

    #get number of columns and rows from coordinates
    ncols = len(uniqueLons)
    nrows = len(uniqueLats)

    #determine pixelsizes
    ys = uniqueLats[1] - uniqueLats[0]
    xs = uniqueLons[1] - uniqueLons[0]

    #create an array with dimensions of image
    arr = np.zeros([nrows, ncols], np.float32)  # -9999

    #fill the array with values
    counter = 0
    for y in range(0, len(arr), 1):
        for x in range(0, len(arr[0]), 1):
            if lats[counter] == uniqueLats[y] and lons[counter] == uniqueLons[x] and counter < len(lats) - 1:
                counter += 1
                arr[len(uniqueLats) - 1 - y, x] = data[counter]  # we start from lower left corner

    #MASKING
    ndvi = (arr ** 2).copy()
    ndvi[ndvi < 0.05] = 0
    ndvi[ndvi > 0.05] = 1
    blue = rgb[:, :, 0]
    red = rgb[:, :, 2]
    blue[ndvi == 1] -= 0.5
    red[ndvi == 1] -= 0.5
    output = rgb.copy()
    output[:, :, 0] = blue
    output[:, :, 2] = red
    output *= 255
    output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)

    cv2.imwrite("D:/MY_WORK/THESIS/Faraz_Work/work/greenarea main/static/l.jpg", output)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # CALCULATIONS
    total_img = np.sum(rgb, axis=-1)
    total_pixels = len(total_img[total_img != 0])
    green_pixels = len(ndvi[ndvi != 0])
    build_pixels = total_pixels - green_pixels
    percent = (green_pixels / total_pixels) * 100
    total = total_sqkm
    green = (percent / 100) * total
    build = total_sqkm - green
    print(total)

    if percent < 30:
        p1 = "Plantation less than 30% is not considered as optimal so kindly plant more trees."
    else:
        p1 = "Plantation is above 30%, you can plant more if you need or help others to plant trees."


    return render_template("resultnew.html", b=total, c=green, d=build, e=percent, f=p1)


if __name__ == '__main__':
    app.debug = True
    app.run()