import ee
import numpy as np
import cv2
from datetime import date
from dateutil.rrule import rrule,MONTHLY
import datetime
import cgi
import csv
image = ee.ImageCollection('COPERNICUS/S2').filterDate('2022-01-01','2022-04-16').filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)).filterBounds(geometry).median()
                  
rgbVis = {
  min: -1,
  max: +1,bands:['B8','B4'],
}

Map.addLayer(image.clip(geometry), rgbVis, 'image')



ndvi = image.expression('(nir - red)/(nir + red)' ,{
  'nir': image.select ('B8'),
  'red': image.select('B4'),
}).rename('NDVI')

final_image = image.addBands(ndvi)

Map.addLayer(final_image.clip(geometry),rgbVis, 'newimage')

# Export.image.toDrive({
#   image: ndvi,
#   description: 'NDVI',
#   scale: 10,
#   region: geometry
# })