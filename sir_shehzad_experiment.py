from flask import Flask, render_template, make_response, url_for, request, jsonify
import ee
import numpy as np
import cv2
from datetime import date
from dateutil.rrule import rrule,MONTHLY
import datetime
import cgi
import csv


app = Flask(__name__, static_url_path='/static')                #telling flask our script file name and static folder for use

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


polygon = None                                                  #methods=['GET', 'POST'] enables the script to retrieve and send data
@app.route('/', methods=['GET', 'POST'])                        #this and the function def index() renders the index.html file in templates folder
def index():
    return render_template("index.html")


@app.route('/map')                                              #this and the function def map() renders the test.html file in templates folder
def map():
    return render_template("test.html")


@app.route('/result', methods=['GET', 'POST'])                  #this and the function def result() renders the resultnew.html file in templates folder
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
    polygon = [[66.97677612304688, 24.8727322360673], [66.99394226074219, 24.881453301317965], [67.00424194335938, 24.882699117531892], [67.0111083984375, 24.879584553440623], [67.0166015625, 24.879584553440623], [67.02484130859375, 24.886436490787712], [67.03170776367188, 24.890796616653954], [67.03479766845703, 24.87740431185819], [67.03857421875, 24.87242075806748], [67.05024719238281, 24.860272503836693], [67.05642700195312, 24.849369208160923], [67.06707000732422, 24.841580551445354], [67.07462310791016, 24.835660844499756], [67.08457946777344, 24.828494504716478], [67.0931625366211, 24.824132181788887], [67.09178924560547, 24.819146481739068], [67.0876693725586, 24.818523255124294], [67.08732604980469, 24.81353732934949], [67.08148956298828, 24.812914074521444], [67.07977294921875, 24.806992997329047], [67.07839965820312, 24.800136659859948], [67.07977294921875, 24.793591620418344], [67.0883560180664, 24.788293002185807], [67.09281921386719, 24.783305860651126], [67.09762573242188, 24.777695086846297], [67.10174560546875, 24.773019248261697], [67.10277557373047, 24.76740800950013], [67.1048355102539, 24.762420028851665], [67.10037231445312, 24.75930243922547], [67.09590911865234, 24.757743615072602], [67.09178924560547, 24.754002357308305], [67.0880126953125, 24.75119634006102], [67.08423614501953, 24.749325626697196], [67.08011627197266, 24.748390259456198], [67.0773696899414, 24.747454885176023], [67.07496643066406, 24.747143092185084], [67.07084655761719, 24.749013838399], [67.06947326660156, 24.75431413309125], [67.05745697021484, 24.770837129986052], [67.05196380615234, 24.778941947389757], [67.0440673828125, 24.78673454198888], [67.03788757324219, 24.792968265314457], [67.02827453613281, 24.799824999147894], [67.01316833496092, 24.805434772108956], [67.00492858886719, 24.806681353851964], [67.00149536132812, 24.817900025374463], [67.01042175292969, 24.81976970521875], [67.02140808105467, 24.821016142772585], [67.02346801757812, 24.827248142416146], [67.01591491699219, 24.83223351635245], [67.01042175292969, 24.83908807776389], [67.00218200683594, 24.84469607296012], [66.99050903320312, 24.84656534821976], [66.98707580566406, 24.852173004559464], [66.98638916015625, 24.86089552027181], [66.98020935058594, 24.86712551196965]]
    area = ee.Geometry.Polygon(polygon)
    total_sqkm = area.area().divide(1000 * 1000).getInfo()

    dt = datetime.date(2018, 4, 1)  # add the starting date according to your satellite, year, month, day
    q = dt.strftime("%Y-%m-%d")
    w = q
    a = 1
    while a < 102:  # set while condition for number of months
        df = dt + datetime.timedelta(weeks=a * 4)  # set number of days or weeks you want to extract
        q = w
        w = df.strftime("%Y-%m-%d")
        #print(w)
        a = a + 1
        # Define the area
        area = ee.Geometry.Polygon(polygon)
        # define the image
        print(q , w)
        #coll = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR").filterDate("" + q + "", "" + w + "")
        coll = ee.ImageCollection("COPERNICUS/S2_SR").filterDate("" + q + "", "" + w + "")
    #coll = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR")

        image_area = coll.filterBounds(area)
        img = image_area.median()

        '''first three bands map to R, G, B, respectively, and stretched to [0, 1] 
        since the bands are float data type. This means that the 
        coastal aerosol band ('B1') is rendered in red, the blue band ('B2') is rendered in green, 
        and the green band ('B3') is rendered in blue. To render the image as a true-color composite, 
        you need to tell Earth Engine to use the Landsat 8 bands 'B4', 'B3', and 'B2' for R, G, and B, respectively.
        source: https://developers.google.com/earth-engine/tutorials/tutorial_api_04'''

        bands = ["B4", "B3", "B2"]
        band_outputs = {}
        #red
        for band in bands:

            image = img.select(band).rename(["temp"])

            latlon = ee.Image.pixelLonLat().addBands(image)     #Creates an image with two bands named 'longitude' and 'latitude', containing the longitude and latitude at each pixel, in degrees.

            latlon = latlon.reduceRegion(                       #Apply a reducer to all the pixels in a specific region.
                reducer=ee.Reducer.toList(),
                geometry=area,
                maxPixels=1e8,
                scale=6)

            data = np.array((ee.Array(latlon.get("temp")).getInfo()))       #getting an array of pixel data
            lats = np.array((ee.Array(latlon.get("latitude")).getInfo()))   #getting an array of lat data
            lons = np.array((ee.Array(latlon.get("longitude")).getInfo()))  #getting an array of lon data

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

        r = np.expand_dims(band_outputs["B4"], -1).astype("float32")            #expanding the array
        g = np.expand_dims(band_outputs["B3"], -1).astype("float32")
        b = np.expand_dims(band_outputs["B2"], -1).astype("float32")
        rgb = np.concatenate((r, g, b), axis=2) / 3000                          #joining r,g,b arrays into one array called rgb

        coll = ee.ImageCollection("COPERNICUS/S2_SR").filterDate("" + q + "", "" + w + "")
        image_area = coll.filterBounds(area)
        img = image_area.median()

        RED = img.select("B4")                                                  #taking the red band
        NIR = img.select("B8")                                                  #taking the near infrared band
        NDVI = ee.Image(img.subtract(RED).divide(NIR.add(RED)))                 #making NVDI image

        #get the lat lon and add the ndvi
        latlon = ee.Image.pixelLonLat().addBands(NDVI)

        #apply reducer to list
        latlon = latlon.reduceRegion(
            reducer=ee.Reducer.toList(),
            geometry=area,
            maxPixels=1e8,
            scale=6)

        data = np.array((ee.Array(latlon.get("B8")).getInfo()))                 #getting an array of pixel data from near infrared band
        lats = np.array((ee.Array(latlon.get("latitude")).getInfo()))           #getting an array of lat data
        lons = np.array((ee.Array(latlon.get("longitude")).getInfo()))          #getting an array of lat data
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
        ndvi[ndvi < 0.2] = 0
        ndvi[ndvi >= 0.2] = 1
        #ndvi[ndvi >= 0.5] = 0
        blue = rgb[:, :, 0]
        red = rgb[:, :, 2]
        blue[ndvi == 1] -= 0.5
        red[ndvi == 1] -= 0.5
        output = rgb.copy()
        output[:, :, 0] = blue
        output[:, :, 2] = red
        output *= 255
        output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)

        #cv2.imwrite("/Users/admin/PycharmProjects/greenarea/static/l.jpg", output)
        #cv2.imwrite("E:/greenarea/static/l.jpg", output)
        cv2.imwrite("./static/{}.jpg".format(a), output)
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
        nongreen = total - green
        build = total_sqkm - green
        print(percent)

        with open('main.csv', 'a', newline="") as f:
            thewriter = csv.writer(f)
            if a == 2:
                thewriter.writerow(['Date', 'TotalArea', 'GreenArea', 'NongreenArea', 'Percentage', 'Coordinates'])
            thewriter.writerow([w, total, green, nongreen, percent, polygon])

    if percent < 30:
        p1 = "Plantation less than 30% is not considered as optimal so kindly plant more trees."
    else:
        p1 = "Plantation is above 30%, you can plant more if you need or help others to plant trees."


    return render_template("resultnew.html", b=total, c=green, d=build, e=percent, f=p1)


if __name__ == '__main__':
    app.debug = True
    app.run()
