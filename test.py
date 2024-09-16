from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as dt
import ee
import numpy as np
from google.auth import credentials
from google.auth import compute_engine
from google.cloud import storage 
import calendar
import copy as cp
import cv2
import csv
import requests
import pyrebase
# import pandas as pd
import pandas as pd
import seaborn as sns
from staticmap import StaticMap, Polygon
import shutil

from math import sqrt
import time as t
import json
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)

Config = {
 "apiKey": "AIzaSyBAkNeWEsfpp52N2v946f6k-ftQbbJc8lk",
  "authDomain": "flask-crop2x.firebaseapp.com",
  "projectId": "flask-crop2x",
  "storageBucket": "flask-crop2x.appspot.com",
  "messagingSenderId": "122929339968",
  "appId": "1:122929339968:web:728b1e53e1102695ee89a5",
  "measurementId": "G-8347B8TW3E",
  "databaseURL": "https://flask-crop2x-default-rtdb.firebaseio.com",
}

app.config['SECRET_KEY'] = 'your_secret_key'

# Update your SQLAlchemy configuration to use mysql-connector-python
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:@localhost/crop"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False

db=SQLAlchemy(app)
firebase = pyrebase.initialize_app(Config)
auth = firebase.auth()
db = firebase.database()
login_manager = LoginManager(app)
login_manager.login_view = 'login'



class User(UserMixin):
    pass


# Homepage ***************************************************************************************************
@app.route('/')
def home():
    return render_template('home.html')
# *****************************************************************************************************
# SIGN UP*********************************************************************************************
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']

        # Check if the username already exists
        if db.child('users').child(username).get().val() is not None:
            flash(f"Error adding user: Username '{username}' already exists", 'error')
            return redirect(url_for('signup'))

        try:
            user = auth.create_user_with_email_and_password(email, password)

            # Store user data in Realtime Database with the username as the key
            user_info = {
                'uid': user['localId'],
                'email': email,
                'username': username,
                'created_at': dt.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Use the username as the key in the database for user_info
            db.child('users').child(username).child('user_info').set(user_info)

            # Store additional user data in user_data subdirectory
            user_data = {
                
            }

            
            db.child('users').child(username).child('user_data').set(user_data)

            flash(f"User {email} signup successful!", 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error adding user: {str(e)}", 'error')
            return redirect(url_for('signup'))
    return render_template('signup.html')

# ...********************************************************************************END
@login_manager.user_loader
def load_user(user_id):
    user = User()
    user.id = user_id
    return user

# Login Admin ************************************************************************
@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            user_token = user['idToken']

            if email in approved_admin_emails:
                flash('Login successful', 'success')
                return redirect(url_for('admin', user=user['idToken']))
            else:
                abort(403)
        except Exception as e:
            flash('Error: Authorized Access only', 'error')
            return redirect(url_for('login_admin'))

    return render_template('login_admin.html')
# END**************************************************************
# USER LOGIN***********************************************************************
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            print("Attempting login with email:", email)  # Debug print
            user = auth.sign_in_with_email_and_password(email, password)
            session['user_token'] = user['idToken']  # Store user token with 'user_token' key
            
            # Fetch user information from the Realtime Database using the user's UID
            user_info_ref = db.child('users').child(user['localId']).child('user_info')
            user_info_snapshot = user_info_ref.get()

            # Check if user_info_snapshot exists
            if user_info_snapshot is not None and user_info_snapshot.val() is not None:
                user_info = user_info_snapshot.val()
                username = user_info.get('username', 'N/A')  # Get the username or use 'N/A' if not found
                created_at = user_info.get('created_at', 'N/A')  # Get the created_at date or use 'N/A' if not found
                print("User info from database:", user_info)  # Debug print
            else:
                print("User info not found in the database.")
                username = 'N/A'
                created_at = 'N/A'
                # Handle the case when user info is not found
                
            # Print user information to the console
            print("User logged in - Email:", email, "Username:", username, "Created at:", created_at, "UID:", user['localId'])
            
            return render_template('dashboard.html')  # or redirect to another page
        except Exception as e:
            print("Error:", e)  # Debug print
            return render_template('login.html', error="Login failed. Please check your credentials and try again.")

    return render_template('login.html')


# END********************************************************************************************
# FOR LOGOUT***********************************************************************
@app.route('/logout')
def logout():
    logout_user()
    flash('Logout successful ', 'success')
    return redirect(url_for('login'))
# ADMIN PAGE************************************************************************************************8
approved_admin_emails = ['ewe111.vijay@gmail.com', 'hashimhasan444@gmail.com', 'yet_another_admin@gmail.com']
# ...
@app.route('/admin')
def admin():
    try:
        user_info = get_user_info()
        if get_user_info is not None:
            user_count = len(user_info)
            return render_template('dashboard_admin.html', users=user_info, user_count=user_count)
        else:
            flash('Error: Failed to fetch user info.', 'error')
            return redirect(url_for('login_admin'))
    except Exception as e:
        flash('Error: ' + str(e), 'error')
        return redirect(url_for('login_admin'))
# ...
def get_user_info():
    user_info_list = []
    try:
        # Fetch user info data from Realtime Database
        users = db.child('users').get()
        for user in users.each():
            user_info = user.val().get('user_info')
            if user_info:
                user_data = {
                    'username': user_info.get('username', ''),
                    'uid': user_info.get('uid', ''),
                    'email': user_info.get('email', ''),
                    'created_on': user_info.get('created_at', '')
                }
                user_info_list.append(user_data)
        return user_info_list
    except Exception as e:
        print("Error in get_user_info:", str(e))
        return None  # Return None in case of an error

@app.route('/edit_user/<user_id>', methods=['POST'])
def edit_user(user_id):
    if request.method == 'POST':
        # Get the new data from the request
        new_email = request.form.get('email')  # Use request.form.get() to avoid KeyError
        new_password = request.form.get('password')  # Use request.form.get() to avoid KeyError
        
        if new_email is None:
            flash("Email is required.", 'error')
            return redirect(url_for('admin'))  # Redirect to wherever appropriate

        try:
            # Update the user's email and password in Firebase Authentication
            auth.update_user(
                user_id,
                email=new_email,
                password=new_password
            )
            
            flash(f"User {user_id} updated successfully!", 'success')
            return redirect(url_for('admin'))  # Redirect to wherever appropriate
        except Exception as e:
            flash(f"Error updating user: {str(e)}", 'error')
            return redirect(url_for('admin'))  # Redirect to wherever appropriate

@app.route('/delete_user/<user_id>', methods=['POST'])
def delete_user(user_id):
    if request.method == 'POST':
        try:
            # Delete the user from Firebase Authentication
            auth.delete_user(user_id)

            # Delete the user's data from Realtime Database
            db.child('users').child(user_id).remove()

            flash(f"User {user_id} deleted successfully!", 'success')
            return redirect(url_for('admin'))  # Redirect to wherever appropriate
        except Exception as e:
            flash(f"Error deleting user: {str(e)}", 'error')
            return redirect(url_for('admin'))  # Redirect to wherever appropriate       

# ********************************************************************ADMIN PAGE END
# DASHBOARD PAGE /MAP PAGE *********************************************************
@app.route('/dashboard')
@login_required
def dashboard():
    if 'user_token' in session:  # Use 'user_token' key to retrieve the user token
        user_token = session['user_token']  # Retrieve the user token from the session
        print("User Token:", user_token)  # Print user token for debugging
        
        try:
            # Verify the user token to get the user's ID
            user_id_token = auth.verify_id_token(user_token)
            print("User ID:", user_id_token['user_id'])  # Print user ID for debugging
            
            # Fetch username from the Realtime Database using the user's ID
            user_info = db.child('users').child(user_id_token['user_id']).child('user_info').get().val()
            print("User Info:", user_info)  # Print user info for debugging
            
            if user_info:
                username = user_info.get('username')
                print("Username:", username)  # Print username for debugging
                return render_template('dashboard.html', username=username)
            else:
                # Handle the case where user data is not found
                print("User data not found")
                return "User data not found", 404
        except Exception as e:
            # Handle any exceptions
            print("Error:", e)
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/check_username', methods=['POST'])
def check_username():
    try:
        data = request.json
        username = data.get('username')

        # Check if username exists in the database (implement this logic according to your database structure)
        exists = db.child('users').child(username).get().val() is not None

        # Return JSON response indicating whether the username exists
        return jsonify({'exists': exists}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 

@app.route('/get_saved_fields', methods=['POST'])
def fetch_saved_fields():
    try:
        data = request.json
        username = data.get('username')

        if username:
            # Query the database to retrieve saved fields associated with the username
            user_data = db.child('users').child(username).child('user_data').get().val()

            if user_data:
                saved_fields = []
                # Extract field data from the user_data dictionary
                for field_name, field_info in user_data.items():
                    saved_fields.append({
                        'id': field_name,  # Make sure to include the unique identifier for each field
                        'name': field_info['name'],
                        'coordinates': field_info['coordinates']
                    })

                # Return the saved fields data as JSON response
                return jsonify({'status': 'success', 'saved_fields': saved_fields}), 200
            else:
                return jsonify({'status': 'error', 'message': 'No saved fields found for the user'}), 404
        else:
            return jsonify({'status': 'error', 'message': 'Username not provided'}), 400

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# key_path = 'geekey.json'

# Initialize Earth Engine with the service account key 
# MAP AND DASHBOARD DATA END*************************************************************************** 


# Define a global variable to store the polygon data



# @app.route('/result', methods=['GET', 'POST'])
# def result():
#     if request.method == 'POST':
#         print('Incoming..')
#         req = request.get_json(force=True)
#         geojson = req.get("geojson")
        
#         if geojson:
#             polygon = geojson["geometry"]["coordinates"][0]  # Extracting coordinates from GeoJSON
            
#             # Now you have the coordinates of the polygon, you can process or save them as needed
#             # For example, you can save them to a database or perform any other required operation
            
#             print("Polygon coordinates:", polygon)
            
#             return jsonify({'status': 'success'})
#         else:
#             return jsonify({'status': 'error', 'message': 'No GeoJSON data received'})

#     return render_template("results.html")
@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        print('Incoming..')
        req = request.get_json(force=True)
        geojson = req.get("geojson")
        global polygon
        
        if geojson:
            polygon = geojson["geometry"]["coordinates"][0]  # Extracting coordinates from GeoJSON
            field_name = req.get("fieldName")  # Extracting field name from the request
            username = req.get("username")  # Extracting username from the request
            
            try:
                # Print the coordinates before saving them to the database
                print("Polygon coordinates:", polygon)
                print("fieldName:", field_name)
                
                if username:
                    # Construct the data to be saved
                    field_data = {
                        'coordinates': polygon,
                        'name': field_name
                    }
                    
                    # Save the field data to Firebase Realtime Database under the provided username
                    db.child('users').child(username).child('user_data').child(field_name).set(field_data)
                    
                    return jsonify({'status': 'success'})
                else:
                    return jsonify({'status': 'error', 'message': 'Username not provided'}), 400
                
            except Exception as e:
                # Log the error message
                print("Error:", e)
                # Return the error message in the response
                return jsonify({'status': 'error', 'message': str(e)}), 500
        else:
            return jsonify({'status': 'error', 'message': 'No GeoJSON data received'}), 400

    return render_template("results.html")


@app.route('/code', methods=['GET', 'POST'])
def code():
    pathvi=[]
    pathmi=[]
    pathre=[]
    pathms=[]
    arrayvi=[]
    arraymi=[]
    arrayre=[]
    arrayms=[]
    with open('ndvi.csv', mode='a+') as csvfile:
            csvfile.truncate(0)
    with open('ndmi.csv', mode='a+') as csvfile:
            csvfile.truncate(0)
    with open('ndre.csv', mode='a+') as csvfile:
            csvfile.truncate(0)
    with open('msavi.csv', mode='a+') as csvfile:
            csvfile.truncate(0)
    global polygon
    ee.Initialize(project='ee-hashimhasan444')

    area = ee.Geometry.Polygon(polygon)
    total_sqkm = area.area().divide(1000 * 1000).getInfo()

 
    import datetime

    startdate= request.form.get('startdate')
    enddate= request.form.get('enddate')
    startdate=startdate.split("/")
    enddate=enddate.split("/")
    year1=int(startdate[2])
    month1=int(startdate[0])
    day1=int(startdate[1])
    year2=int(enddate[2])
    month2=int(enddate[0])
    day2=int(enddate[1])
    x= {1: 'Jan',2: 'Feb',3: 'Mar',4: 'Apr',5: 'May',6: 'Jun',7: 'Jul' ,8: 'Aug',9: 'Sep',10: 'Oct',11: 'Nov',12: 'Dec'}
    for h in x:
        if  h == int(month1):
            z= x[h]
            mon1= z
    for k in x:
        if  k == int(month2):
            z= x[k]
            mon2= z
    stdate= str(mon1) + " "+ str(day1) + ", "+ str(year1)
    endate= str(mon2) + " "+ str(day2) + ", "+ str(year2)

    start_date = datetime.date(year1,month1,day1)
    end_date = datetime.date(year2,month2,day2)

    dt = datetime.date(year1,month1,day1)  # add the starting date according to your satellite, year, month, day
    q = dt.strftime("%Y-%m-%d")
    # dt = datetime.date(2021, 5,17)  # add the starting date according to your satellite, year, month, day
    w = q
    delta = datetime.timedelta(days=5)
    a = 1
    # while a < 10:
    # start timer
    start = t.time()
    while (start_date < end_date): 
     
        df = dt + datetime.timedelta(days=a * 5)  # set number of days or weeks you want to extract
        q = w
        w = df.strftime("%Y-%m-%d")
        #print(w)
     
        start_date += delta
    # Define the area

    # define the image
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
            try:
                image = img.select(band).rename(["temp"])
            except ee.ee_exception.EEException:
                
                continue
        
        #end timer
            total_time = t.time() - start
            print("total time", total_time)



            latlon = ee.Image.pixelLonLat().addBands(image)     #Creates an image with two bands named 'longitude' and 'latitude', containing the longitude and latitude at each pixel, in degrees.

            latlon = latlon.reduceRegion(                       #Apply a reducer to all the pixels in a specific region.
                reducer=ee.Reducer.toList(),
                geometry=area,
                maxPixels=1e8,
                scale=2)

            data = np.array((ee.Array(latlon.get("temp")).getInfo()))       #getting an array of pixel data
            lats = np.array((ee.Array(latlon.get("latitude")).getInfo()))   #getting an array of lat data
            lons = np.array((ee.Array(latlon.get("longitude")).getInfo())) 
            # print( data)
            # print(lats) #getting an array of lon data
            # print(lons)

            #get the unique coordinates
            uniqueLats = np.unique(lats)
            # print(uniqueLats)
            uniqueLons = np.unique(lons)
            # print(uniqueLons)

            #get number of columns and rows from coordinates
            ncols = len(uniqueLons)
            # print( ncols)
            nrows = len(uniqueLats)
            # print(nrows)

            #determine pixelsizes
            ys = uniqueLats[1] - uniqueLats[0]
            # print(  ys)
            xs = uniqueLons[1] - uniqueLons[0]
            # print(xs)

            #create an array with dimensions of image
            arr = np.zeros([nrows, ncols], np.float32)  # -9999
            
            # fill the array with values
            counter = 0
            for y in range(0, len(arr), 1):
                for x in range(0, len(arr[0]), 1):
                    if lats[counter] == uniqueLats[y] and lons[counter] == uniqueLons[x] and counter < len(lats) - 1:
                        arr[len(uniqueLats) - 1 - y, x] = data[counter]  # we start from lower left corner
                        counter += 1
            band_outputs[band] = arr
            # print(arr)
        if not band_outputs:
             print("No valid bands found for this image date")
    # do something else or skip this image date

        else: 
            r = np.expand_dims(band_outputs["B4"], -1).astype("float32")            #expanding the array
        g = np.expand_dims(band_outputs["B3"], -1).astype("float32")
        b = np.expand_dims(band_outputs["B2"], -1).astype("float32")
        rgb = np.concatenate((r, g, b), axis=2) / 3000                          #joining r,g,b arrays into one array called rgb

        coll = ee.ImageCollection("COPERNICUS/S2_SR").filterDate("" + q + "", "" + w + "")
        image_area = coll.filterBounds(area)
        # print("image_area", image_area)
        img = image_area.median()
        # print("img", img)



      
        RED = img.select("B4")                                                  #taking the red band
        NIR = img.select("B8")   
        SWIR = img.select("B11")  
        Rededge = img.select("B5") 
        

        
        NDVI = ee.Image(NIR.subtract(RED).divide(NIR.add(RED)))   #taking the near infrared band
        # NDVI = ee.Image((NIR-RED)/(NIR+RED))
        NDMI = ee.Image(NIR.subtract(SWIR).divide(NIR.add(SWIR)))  
        # NDMI = ee.Image((NIR-SWIR)/(NIR+SWIR))
        NDRE = ee.Image(NIR.subtract(Rededge).divide(NIR.add(Rededge)))  
        # NDRE = ee.Image((NIR-Rededge)/(NIR+Rededge))
        # MSAVI = ee.Image((2 * NIR + 1 - sqrt(pow((2 * NIR + 1), 2) - 8 * (NIR - RED)) ) / 2)
        MSAVI =ee.Image(NIR.multiply(2).add(1).subtract(NIR.multiply(2).add(1).pow(2).subtract(NIR.subtract(RED).multiply(8)).sqrt()).divide(2))
        # MSAVI = ee.Image((NIR * 2 + 1 - np.sqrt(np.power((NIR * 2 + 1), 2) - (NIR - RED) * 8) ) / 2)
        # print("NDVI", NDVI)           #making NVDI image
        #get the lat lon and add the ndvi
        latlonvi = ee.Image.pixelLonLat().addBands(NDVI)
        latlonmi = ee.Image.pixelLonLat().addBands(NDMI)
        latlonre = ee.Image.pixelLonLat().addBands(NDRE)
        latlonms= ee.Image.pixelLonLat().addBands(MSAVI)
        # print(" latlon", latlon)
        #apply reducer to list
        latlonvi = latlonvi.reduceRegion(
            reducer=ee.Reducer.toList(),
            geometry=area,
            maxPixels=1e8,
            scale=2)
        latlonmi = latlonmi.reduceRegion(
            reducer=ee.Reducer.toList(),
            geometry=area,
            maxPixels=1e8,
            scale=2)
        latlonre = latlonre.reduceRegion(
            reducer=ee.Reducer.toList(),
            geometry=area,
            maxPixels=1e8,
            scale=2)
        latlonms = latlonms.reduceRegion(
            reducer=ee.Reducer.toList(),
            geometry=area,
            maxPixels=1e8,
            scale=2)
        datavi = np.array((ee.Array(latlonvi.get("B8")).getInfo()))                 #getting an array of pixel data from near infrared band
        latsvi = np.array((ee.Array(latlonvi.get("latitude")).getInfo()))           #getting an array of lat data
        lonsvi = np.array((ee.Array(latlonvi.get("longitude")).getInfo()))     
        print("NDVI")
        # print( "data", datavi)
        # print("lats",latsvi) 
        # print("lons",lonsvi)    
        # print("data.shape",datavi.shape)
        #get the unique coordinates
        uniqueLatsvi = np.unique(latsvi)
        uniqueLonsvi = np.unique(lonsvi)
        # print(uniqueLatsvi)
        # print(uniqueLonsvi)
        #get number of columns and rows from coordinates
        ncolsvi = len(uniqueLonsvi)
        print(ncolsvi)
        nrowsvi = len(uniqueLatsvi)
        print(nrowsvi)
        #determine pixelsizes
        ysvi = uniqueLatsvi[1] - uniqueLatsvi[0]
        xsvi = uniqueLonsvi[1] - uniqueLonsvi[0]

        #create an array with dimensions of image
        arrvi = np.zeros([nrowsvi, ncolsvi], np.float32)  # -9999
        # print(len(arr))
        #fill the array with values
        counter = 0
        for y in range(0, len(arrvi), 1):
            for x in range(0, len(arrvi[0]), 1):
                # print("len(arr[0])",len(arr[0]))
                if latsvi[counter] == uniqueLatsvi[y] and lonsvi[counter] == uniqueLonsvi[x] and counter < len(latsvi) - 1:
                    # print(len(uniqueLats) - 1 - y, x)
                    arrvi[len(uniqueLatsvi) - 1 - y, x] = datavi[counter]  #we start from lower left corner
                    counter += 1
        #MASKING
        # import json
        ndvi = arrvi.copy()
        arrayvin=ndvi.tolist()
        # ndvis = arr.copy()
        # print('arr =',arr)
        import json
        # arrayvin = json.dumps(ndvi.tolist())  
        arrayvi.append(arrayvin)
        # print(arrayvi)
       

 ################# NDMI ###############################
        datami = np.array((ee.Array(latlonmi.get("B8")).getInfo()))                 #getting an array of pixel data from near infrared band
        latsmi = np.array((ee.Array(latlonmi.get("latitude")).getInfo()))           #getting an array of lat data
        lonsmi = np.array((ee.Array(latlonmi.get("longitude")).getInfo()))     
        print("NDMI")
        # print( "data", datami)
        # print("lats",latsmi) 
        # print("lons",lonsmi)    
        # print("data.shape",datami.shape)
        #get the unique coordinates
        uniqueLatsmi = np.unique(latsmi)
        uniqueLonsmi = np.unique(lonsmi)
        # print(uniqueLatsmi)
        # print(uniqueLonsmi)
        

        #get number of columns and rows from coordinates
        ncolsmi = len(uniqueLonsmi)
        print(ncolsmi)
        
        nrowsmi = len(uniqueLatsmi)
        print(nrowsmi)
        

        #determine pixelsizes
        ysmi = uniqueLatsmi[1] - uniqueLatsmi[0]
        xsmi = uniqueLonsmi[1] - uniqueLonsmi[0]

        #create an array with dimensions of image
        arrmi = np.zeros([nrowsmi, ncolsmi], np.float32)  # -9999
        # print(len(arr))
        #fill the array with values
        counter = 0
        for y in range(0, len(arrmi), 1):
            for x in range(0, len(arrmi[0]), 1):
                # print("len(arr[0])",len(arr[0]))
                if latsmi[counter] == uniqueLatsmi[y] and lonsmi[counter] == uniqueLonsmi[x] and counter < len(latsmi) - 1:
                    # print(len(uniqueLats) - 1 - y, x)
                    arrmi[len(uniqueLatsmi) - 1 - y, x] = datami[counter]  #we start from lower left corner
                    counter += 1

        #MASKING
        # import json

      
    
        # print('arr =',arr)

        ndmi = ((np.around(arrmi.copy(),decimals=1))+0.02)
        ndmis = np.around(arrmi.copy(),decimals=1)
        # ndvis = arr.copy()
        # print('arr =',arr)
        # arraymi = json.dumps(ndmis.tolist())  
     
        arraymin=ndmis.tolist() 
        arraymi.append(arraymin)
   ################################  NDRE  ######################################    

        datare = np.array((ee.Array(latlonre.get("B8")).getInfo()))                 #getting an array of pixel data from near infrared band
        latsre = np.array((ee.Array(latlonre.get("latitude")).getInfo()))           #getting an array of lat data
        lonsre = np.array((ee.Array(latlonre.get("longitude")).getInfo()))     
        print("NDRE")
        # print( "data", datavi)
        # print("lats",latsvi) 
        # print("lons",lonsvi)    
        # print("data.shape",datavi.shape)
        #get the unique coordinates
        uniqueLatsre = np.unique(latsre)
        uniqueLonsre = np.unique(lonsre)
        # print(uniqueLatsvi)
        # print(uniqueLonsvi)
        

        #get number of columns and rows from coordinates
        ncolsre = len(uniqueLonsre)
        print(ncolsre)
        
        nrowsre = len(uniqueLatsre)
        print(nrowsre)
        

        #determine pixelsizes
        ysvi = uniqueLatsre[1] - uniqueLatsre[0]
        xsvi = uniqueLonsre[1] - uniqueLonsre[0]

        #create an array with dimensions of image
        arrre = np.zeros([nrowsre, ncolsre], np.float32)  # -9999
        # print(len(arr))
        #fill the array with values
        counter = 0
        for y in range(0, len(arrre), 1):
            for x in range(0, len(arrre[0]), 1):
                # print("len(arr[0])",len(arr[0]))
                if latsre[counter] == uniqueLatsre[y] and lonsre[counter] == uniqueLonsre[x] and counter < len(latsre) - 1:
                    # print(len(uniqueLats) - 1 - y, x)
                    arrre[len(uniqueLatsre) - 1 - y, x] = datare[counter]  #we start from lower left corner
                    counter += 1

        #MASKING
        # import json
        ndre = arrre.copy()
        # ndvis = arr.copy()
        # print('arr =',arr)
        import json
        # arrayre = json.dumps(ndre.tolist())  
        arrayren=ndre.tolist() 
        arrayre.append(arrayren)

    ################################  MSAVI ######################################    

        datams = np.array((ee.Array(latlonms.get("B8")).getInfo()))                 #getting an array of pixel data from near infrared band
        latsms = np.array((ee.Array(latlonms.get("latitude")).getInfo()))           #getting an array of lat data
        lonsms = np.array((ee.Array(latlonms.get("longitude")).getInfo()))     
        print("MSAVI")
        # print( "data", datavi)
        # print("lats",latsvi) 
        # print("lons",lonsvi)    
        # print("data.shape",datavi.shape)
        #get the unique coordinates
        uniqueLatsms = np.unique(latsms)
        uniqueLonsms = np.unique(lonsms)
        # print(uniqueLatsvi)
        # print(uniqueLonsvi)
        

        #get number of columns and rows from coordinates
        ncolsms = len(uniqueLonsms)
        print(ncolsms)
        
        nrowsms = len(uniqueLatsms)
        print(nrowsms)
        

        #determine pixelsizes
        ysms = uniqueLatsms[1] - uniqueLatsms[0]
        xsms = uniqueLonsms[1] - uniqueLonsms[0]

        #create an array with dimensions of image
        arrms = np.zeros([nrowsms, ncolsms], np.float32)  # -9999
        # print(len(arr))
        #fill the array with values
        counter = 0
        for y in range(0, len(arrms), 1):
            for x in range(0, len(arrms[0]), 1):
                # print("len(arr[0])",len(arr[0]))
                if latsms[counter] == uniqueLatsms[y] and lonsms[counter] == uniqueLonsms[x] and counter < len(latsms) - 1:
                    # print(len(uniqueLats) - 1 - y, x)
                    arrms[len(uniqueLatsms) - 1 - y, x] = datams[counter]  #we start from lower left corner
                    counter += 1

        #MASKING
        # import json
        msavi= arrms.copy()
        # ndvis = arr.copy()
        # print('arr =',arr)
        import json
        # arrayms = json.dumps(msavi.tolist())    
        arraymsn=msavi.tolist() 
        arrayms.append(arraymsn)
   ###############################################################
        np.savetxt("ndvi-arr.csv", ndvi, delimiter=",")
        np.savetxt("ndmi-arr.csv", ndmi, delimiter=",")
        np.savetxt("ndre-arr.csv", ndre, delimiter=",")
        np.savetxt("msavi-arr.csv", msavi, delimiter=",")
       
        print("ndvi")
        print("ndvi.shape", ndvi.shape)
        # print("max", np.max(ndvi))
        maxvi =np.max(ndvi)
        minvi = np.min(ndvi)
        avgvi= np.average(ndvi)
        print("max", np.max(ndvi))
        print("min", np.min(ndvi))
        print("average", np.average(ndvi))

        print("ndmi")
        print("ndmi.shape", ndmi.shape)
        # print("max", np.max(ndvi))
        maxmi =np.max(ndmi)
        minmi = np.min(ndmi)
        avgmi= np.average(ndmi)
        print("max", np.max(ndmi))
        print("min", np.min(ndmi))
        print("average", np.average(ndmi))

        print("ndre")
        print("ndre.shape", ndre.shape)
        # print("max", np.max(ndvi))
        maxre =np.max(ndre)
        minre = np.min(ndre)
        avgre= np.average(ndre)
        print("max", np.max(ndre))
        print("min", np.min(ndre))
        print("average", np.average(ndre))

        print("msavi")
        print("msavi.shape", msavi.shape)
        # print("max", np.max(ndvi))
        maxms =np.max(msavi)
        minms = np.min(msavi)
        avgms= np.average(msavi)
        print("max", np.max(msavi))
        print("min", np.min(msavi))
        print("average", np.average(msavi))
        # print("mean", np.mean(ndvi))
        # print ("min value element : ", my_data.min(axis=0)[1])
        # print ("max value element : ", my_data.max(axis=0)[2])
        # minVal, maxVal = [], []
        # for i in data:
        #     minVal.append(i[1])
        #     maxVal.append(i[2])

        # print min(minVal)
        # print max(maxVal)
        outputmi = rgb.copy()
        # output[:, :, 0] = blue
        # output[:, :, 2] = red
        outputmi *= 255
        outputmi = cv2.cvtColor(outputmi, cv2.COLOR_BGR2RGB)
        cv2.imwrite("./static/ndmi/{}.jpg".format(a), outputmi)


        outputre = rgb.copy()
        # output[:, :, 0] = blue
        # output[:, :, 2] = red
        outputre *= 255
        outputre = cv2.cvtColor(outputre, cv2.COLOR_BGR2RGB)
        cv2.imwrite("./static/ndre/{}.jpg".format(a), outputre)

        outputms = rgb.copy()
        # output[:, :, 0] = blue
        # output[:, :, 2] = red
        outputms *= 255
        outputms = cv2.cvtColor(outputms, cv2.COLOR_BGR2RGB)
        cv2.imwrite("./static/msavi/{}.jpg".format(a), outputms)

        ndvi[ndvi < 0.4] = 0
        ndvi[ndvi > 0.4] = 1
        # with np.printoptions(threshold=np.inf):
      
        #     print("ndvi array =", ndvi)
            
        np.savetxt("final-ndvi.csv", ndvi, delimiter=",")
        # file = "final-ndvi.csv"
        ndvi[ndvi >= 0.5] = 0
        blue = rgb[:, :, 0]
        red = rgb[:, :, 2]
        blue[ndvi == 1] -= 0.5
        red[ndvi == 1] -= 0.5
        outputvi = rgb.copy()
        outputvi[:, :, 0] = blue
        outputvi[:, :, 2] = red
        outputvi *= 255
        outputvi = cv2.cvtColor(outputvi, cv2.COLOR_BGR2RGB)

     
      

        #cv2.imwrite("/Users/admin/PycharmProjects/greenarea/static/l.jpg", output)
        #cv2.imwrite("E:/greenarea/static/l.jpg", output)
        cv2.imwrite("./static/ndvi/{}.jpg".format(a), outputvi)
  
       
        
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # a = request.args.get('X', 0, type=int)
        # b = request.args.get('Y', 0, type=int)

        # print(a,b)
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
        print("percentage", percent)
        


        

        with open('main.csv', 'a', newline="") as f:
            thewriter = csv.writer(f)
            if a == 1:
                thewriter.writerow(['Date', 'TotalArea', 'GreenArea', 'NongreenArea', 'Percentage', 'Coordinates'])
            thewriter.writerow([w, total, green, nongreen, percent, polygon])
        
        with open('ndvi.csv', 'a', newline="") as f:
            thewriter = csv.writer(f)
            if a == 1:
                thewriter.writerow(['date', 'min','avg','max'])
            thewriter.writerow([q,minvi,avgvi,maxvi ])
        with open('ndmi.csv', 'a', newline="") as f:
            thewriter = csv.writer(f)
            if a == 1:
                thewriter.writerow(['date', 'min','avg','max'])
            thewriter.writerow([q,minmi,avgmi,maxmi ])
        with open('ndre.csv', 'a', newline="") as f:
            thewriter = csv.writer(f)
            if a == 1:
                thewriter.writerow(['date', 'min','avg','max'])
            thewriter.writerow([q,minre,avgre,maxre ])
        with open('msavi.csv', 'a', newline="") as f:
            thewriter = csv.writer(f)
            if a == 1:
                thewriter.writerow(['date', 'min','avg','max'])
            thewriter.writerow([q,minms,avgms,maxms ])


        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        colorvi = pd.read_csv('ndvi-arr.csv')
        color_palettevi = sns.color_palette("RdYlGn",as_cmap=True)

        # Pass palette to plot and set axis ranges
        sns.heatmap(colorvi,
                    cmap=color_palettevi,
                    center=0.5,
                    vmin=0,
                    vmax=1,
                    yticklabels=False,
                    xticklabels=False,
                    cbar=False
                )
        plt.savefig("./static/viplot/{}.jpg".format(a),bbox_inches='tight',pad_inches=0)
        # plotvi= "./static/viplot/{}.jpg".format(a)
        pathvi.append("./static/viplot/{}.jpg".format(a))

        colormi = pd.read_csv('ndmi-arr.csv')
        for i in np.arange(0,1,0.1):
            colormi[colormi == i] = i + 0.01
        colors=["#AF998C",'#B49E95','#BAA49E','#BFAAA8','#C5B0B2','#CBB6BC','#D0BBC5', '#D6C1CF', '#CBB9D2', '#BAADD3', '#A8A0D5','#9894D6','#8788D7','#767BD8','#646ED9','#5362DA','#4356DB','#3249DC','#213DDD','#0F30DE']
        color_palettemi = sns.color_palette(colors,as_cmap=True)


        # Pass palette to plot and set axis ranges
        sns.heatmap(colormi,
                    cmap=color_palettemi,
                    center=0,
                    vmin=-1,
                    vmax=1,
                    yticklabels=False,
                    xticklabels=False,
                    cbar=False
                )
        plt.savefig("./static/miplot/{}.jpg".format(a),bbox_inches='tight',pad_inches=0)
        # plotmi= "./static/miplot/{}.jpg".format(a)
        
        pathmi.append("./static/miplot/{}.jpg".format(a))

        colorre = pd.read_csv('ndre-arr.csv')
        color_palettere = sns.color_palette("RdYlGn",as_cmap=True)

        # Pass palette to plot and set axis ranges
        sns.heatmap(colorre,
                    cmap=color_palettere,
                    center=0.5,
                    vmin=0,
                    vmax=1,
                    yticklabels=False,
                    xticklabels=False,
                    cbar=False
                )
        plt.savefig("./static/replot/{}.jpg".format(a),bbox_inches='tight',pad_inches=0)
        # plotvi= "./static/viplot/{}.jpg".format(a)
        pathre.append("./static/replot/{}.jpg".format(a))

        colorms = pd.read_csv('msavi-arr.csv')
        color_palettems = sns.color_palette("RdYlGn",as_cmap=True)

        # Pass palette to plot and set axis ranges
        sns.heatmap(colorms,
                    cmap=color_palettems,
                    center=0.5,
                    vmin=0,
                    vmax=1,
                    yticklabels=False,
                    xticklabels=False,
                    cbar=False
                )
        plt.savefig("./static/msplot/{}.jpg".format(a),bbox_inches='tight',pad_inches=0)
        # plotvi= "./static/viplot/{}.jpg".format(a)
        pathms.append("./static/msplot/{}.jpg".format(a))
        a = a + 1
    if percent < 30:
        p1 = "Plantation less than 30% is not considered as optimal so kindly plant more trees."
    else:
        p1 = "Plantation is above 30%, you can plant more if you need or help others to plant trees."
    

    
   
   
    datavi = pd.read_csv('ndvi.csv', on_bad_lines='skip')
    datami = pd.read_csv('ndmi.csv', on_bad_lines='skip')
    datare = pd.read_csv('ndre.csv', on_bad_lines='skip')
    datams = pd.read_csv('msavi.csv', on_bad_lines='skip')
    

    datearray= datavi['date'].tolist()
    dates_arr = []
    for date in datearray:
     dates_arr.append(datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%d %B, %Y"))
    # import json
    # dates_arr= json.dumps(dates_arr)
    # x= {1 + (i - 1) % 12:calendar.month_name[i] for i in range(1, 13)}
    x= {1: 'Jan',2: 'Feb',3: 'Mar',4: 'Apr',5: 'May',6: 'Jun',7: 'Jul',8: 'Aug',9: 'Sep',10: 'Oct',11: 'Nov',12: 'Dec'}

    # monvi = datavi['date'].str[-5:-3]
    # dayvi=datavi['date'].astype(str).str[-2:]
    # monmi = datami['date'].str[-5:-3]
    # daymi=datami['date'].astype(str).str[-2:]
    # k=0

    # for g in monvi:
    #     for h in x:
    #         if  h == int(float(g)):
    #             z=  x[h]
    #             datavi['date'][k] = dayvi[k] + " "+ z
    #             k=k+1
    # print(datavi)
    # k=0
    # for g in monmi:
    #     for h in x:
    #         if  h == int(float(g)):
    #             z=  x[h]
    #             datami['date'][k] = daymi[k] + " "+ z
    #             k=k+1
    # print(datami)
    # firstrow= ['date','min', 'avg','max']
    # print(data.columns.values)
    lvi=list(datavi.values.tolist())
    # lvi.insert(0, firstrow)
    import json
    dicvi= json.dumps(lvi)
    
    lmi=list(datami.values.tolist())
    # lmi.insert(0, firstrow)
    import json
    dicmi= json.dumps(lmi)
    # print(lmi)
    lre=list(datare.values.tolist())
    # lmi.insert(0, firstrow)
    import json
    dicre= json.dumps(lre)

    lms=list(datams.values.tolist())
    # lmi.insert(0, firstrow)
    import json
    dicms= json.dumps(lms)
    # print('lre',lre)
######################################        weather data        ###############################
    from datetime import datetime
    from meteostat import Point, Daily,Hourly
    # Set time period
    start = datetime(year1,month1,day1)
    end = datetime(year2,month2,day2)
    x= {1: 'Jan',2: 'Feb',3: 'Mar',4: 'Apr',5: 'May',6: 'Jun',7: 'Jul',8: 'Aug',9: 'Sep',10: 'Oct',11: 'Nov',12: 'Dec'}
    # vancouver = Point(25.14780973,67.21414)
    vancouver = Point(lats[0],lons[0])
    # print(vancouver)  
    data1 = Daily(vancouver, start, end)
    data1 = data1.fetch()
    # print(data1)
    data1.to_csv('weather-daily.csv')
    weather1= pd.read_csv('weather-daily.csv', on_bad_lines='skip')
    k=0
    # monthwthr1 = weather1['time'].str[-5:-3]
    # daywthr1=weather1['time']
    # for g in monthwthr1:
    #     for h in x:
    #         if  h == int(float(g)):
    #             z=  x[h]
    #             weather1['time'][k] = "new Date"+ "("+ '"'+daywthr1[k]+'"'+ ")"
    #             k=k+1

    wthr1=weather1[weather1.columns[:4]]
    ltmp=list(wthr1.values.tolist())
    # translation = {39: None}
    # ltmp=str(ltmp).translate(translation)
    # print(ltmp)
    import json
    dictmp= json.dumps(ltmp)

    # Get hourly data
    data2 = Hourly(vancouver, start, end)
    data2 = data2.fetch()
    data2.to_csv('weather-hourly.csv')
    weather2= pd.read_csv('weather-hourly.csv', on_bad_lines='skip')
    k=0
    # monthwthr2 = weather2['time'].str[5:7]
    # daywthr2= weather2['time']
    # for g in monthwthr2:
    #     for h in x:
    #         if  h == int(float(g)):
    #             z=  x[h]
    #             weather2['time'][k] =  "new Date"+ "("+ '"'+daywthr2[k]+'"'+ ")"
    #             k=k+1

    wthr2=weather2[weather2.columns[:-8:3]]
    # print(wthr2)
    # translation = {39: None}
    lhum=list(wthr2.values.tolist())
    # lhum=str(lhum).translate(translation)
    # print(lhum)
    import json
    dichum= json.dumps(lhum)

    


 
    # print(pathvi)

    # print(pathmi)
    # print(pathre) 
    # print(arrayvi)
    # print(type(arrayvi))
    # print(type(pathvi))
    polygonss = polygon
    for i in range(len(polygonss)):
    #     print(i)
            for j in range(len(polygonss[i])):
        #             print('j',j)
                    x=1
                    polygonss[i][j],polygonss[i][x]= polygonss[i][x], polygonss[i][j]
    print(polygonss)

    return render_template("finalnew.html",polygonss=polygonss,dates_arr=dates_arr,b=total, c=green, d=build, e=percent, f=p1,nrowsvi=nrowsvi,nrowsmi=nrowsmi,nrowsre=nrowsre,nrowsms=nrowsms,ncolsvi=ncolsvi, ncolsmi=ncolsmi,ncolsre=ncolsre, ncolsms=ncolsms,ndvi=arrayvi ,ndmi=arraymi,ndre=arrayre,msavi=arrayms, pathvi=pathvi,pathmi=pathmi,pathre=pathre,pathms=pathms,dicvi=dicvi,dicmi=dicmi,dicre=dicre,dicms=dicms,dictmp=dictmp,dichum=dichum,startdate=stdate,enddate=endate)

# @app.route('/my', methods=['GET', 'POST'])
# def my():

#     import pandas as pd
#     datavi = pd.read_csv('ndvi.csv', on_bad_lines='skip')
#     datami = pd.read_csv('ndmi.csv', on_bad_lines='skip')
#     x= {1: 'Jan',2: 'Feb',3: 'Mar',4: 'Apr',5: 'May',6: 'Jun',7: 'Jul',8: 'Aug',9: 'Sep',10: 'Oct',11: 'Nov',12: 'Dec'}

#     monvi = datavi['date'].str[-5:-3]
#     dayvi=datavi['date'].astype(str).str[-2:]
#     monmi = datami['date'].str[-5:-3]
#     daymi=datami['date'].astype(str).str[-2:]
#     k=0

#     for g in monvi:
#         for h in x:
#             if  h == int(float(g)):
#                 z=  x[h]
#                 datavi['date'][k] =  dayvi[k] + " "+ z
#                 k=k+1
#     print(datavi)
#     k=0
#     for g in monmi:
#         for h in x:
#             if  h == int(float(g)):
#                 z=  x[h]
#                 datami['date'][k] =  daymi[k] + " "+ z
#                 k=k+1
#     print(datami)
#     # firstrow= ['date','min', 'avg','max']
#     # print(data.columns.values)
#     lvi=list(datavi.values.tolist())
#     # lvi.insert(0, firstrow)
#     import json
#     dicvi= json.dumps(lvi)
    
#     lmi=list(datami.values.tolist())
#     print(lmi)
#     # lmi.insert(0, firstrow)
#     import json
#     dicmi= json.dumps(lmi)
#     plotvi="./static/viplot/12.jpg"
#     plotmi= "./static/miplot/12.jpg"
#     from datetime import datetime
#     from meteostat import Point, Daily,Hourly
#     # Set time period
#     start = datetime(2022, 5, 17)
#     end = datetime(2022, 6, 9)
#     x= {1: 'Jan',2: 'Feb',3: 'Mar',4: 'Apr',5: 'May',6: 'Jun',7: 'Jul',8: 'Aug',9: 'Sep',10: 'Oct',11: 'Nov',12: 'Dec'}
#     vancouver = Point(25.14780973,67.21414)
#     # vancouver = Point(lats[0],lons[0])
#     print(vancouver)
#     data1 = Daily(vancouver, start, end)
#     data1 = data1.fetch()
#     print(data1)
#     data1.to_csv('weather-daily.csv')
#     weather1= pd.read_csv('weather-daily.csv', on_bad_lines='skip')

#     k=0
#     monthwthr1 = weather1['time'].str[-5:-3]
#     daywthr1=weather1['time']
#     for g in monthwthr1:
#         for h in x:
#             if  h == int(float(g)):
#                 z=  x[h]
#                 weather1['time'][k] = "new Date"+ "("+ '"'+daywthr1[k]+'"'+ ")"
#                 k=k+1

#     wthr1=weather1[weather1.columns[:4]]
#     ltmp=list(wthr1.values.tolist())
#     translation = {39: None}
#     ltmp=str(ltmp).translate(translation)
#     print(ltmp)
#     import json
#     dictmp= json.dumps(ltmp)

#     # Get hourly data
#     data2 = Hourly(vancouver, start, end)
#     data2 = data2.fetch()
#     data2.to_csv('weather-hourly.csv')
#     weather2= pd.read_csv('weather-hourly.csv', on_bad_lines='skip')
#     k=0
#     monthwthr2 = weather2['time'].str[5:7]
#     daywthr2= weather2['time']
#     for g in monthwthr2:
#         for h in x:
#             if  h == int(float(g)):
#                 z=  x[h]
#                 weather2['time'][k] =  "new Date"+ "("+ '"'+daywthr2[k]+'"'+ ")"
#                 k=k+1

#     wthr2=weather2[weather2.columns[:-8:3]]
#     print(wthr2)
#     translation = {39: None}
#     lhum=list(wthr2.values.tolist())
#     lhum=str(lhum).translate(translation)
#     print(lhum)
#     import json
#     dichum= json.dumps(lhum)

    
 
#     return render_template('final.html',dicvi=dicvi,dicmi=dicmi,plotvi=plotvi,plotmi=plotmi,dichum=dichum,dictmp=dictmp)
# @app.route('/dec', methods=['GET', 'POST'])
# def dec():
#     return render_template("dec.html")
if __name__ == '__main__':
    app.debug = True
    app.run(port= 152)