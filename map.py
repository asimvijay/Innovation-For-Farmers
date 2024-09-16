# Import necessary modules
import ee
import folium
from flask import Flask, render_template, request, jsonify

# Initialize Earth Engine with the service account key
key_path = 'D:\\flask-login\\geekey.json'
credentials = ee.ServiceAccountCredentials('', key_path)
ee.Initialize(project='ee-ewe111vijay')
# Function to calculate NDVI
def calculate_ndvi(image):
    # Compute NDVI
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return ndvi

# Function to fetch satellite imagery for the selected area
def fetch_satellite_imagery(geometry, start_date, end_date):
    # Define the image collection (e.g., Sentinel-2)
    collection = ee.ImageCollection('COPERNICUS/S2') \
        .filterBounds(geometry) \
        .filterDate(start_date, end_date) \
        .select(['B4', 'B8'])  # Select the desired bands (red and NIR)
    
    # Get the median image from the collection
    image = collection.median()
    
    return image

# Flask app
app = Flask(__name__)

# Route to display NDVI map
@app.route('/ndvi_map')
def ndvi_map():
    # Get parameters from the request
    geometry_json = request.args.get('geometry')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Convert geometry JSON to ee.Geometry
    geometry_dict = eval(geometry_json)
    geometry = ee.Geometry.Polygon(geometry_dict['coordinates'])

    # Fetch satellite imagery for the selected area
    image = fetch_satellite_imagery(geometry, start_date, end_date)

    # Calculate NDVI
    ndvi = calculate_ndvi(image)

    # Create a map centered at the centroid of the selected area
    centroid = geometry.centroid().coordinates().getInfo()[::-1]  # Reverse coordinates for folium
    map_obj = folium.Map(location=centroid, zoom_start=10)

    # Add NDVI layer to the map
    folium.TileLayer(
        tiles=ndvi.getMapId({'min': -1, 'max': 1, 'palette': ['blue', 'white', 'green']}),
        attr='NDVI',
        overlay=True,
        name='NDVI',
    ).add_to(map_obj)

    # Save the map as an HTML file
    map_file = 'templates/ndvi_map.html'
    map_obj.save(map_file)

    # Return the HTML file to display the map
    return render_template('ndvi_map.html')


if __name__ == '__main__':
    app.run(debug=True)
