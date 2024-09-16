from flask import Flask, render_template, make_response, url_for, request, jsonify
import ee
import numpy as np
import cv2
import geemap
import os
from datetime import date
from dateutil.rrule import rrule,MONTHLY
import datetime
import cgi
import csv
import sys
import numpy as np
import tifffile as tiff


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


@app.route('/map')                                              #this and the function def map1() renders the test.html file in templates folder
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

def maskS2clouds(image):
  qa = image.select('QA60')

  # Bits 10 and 11 are clouds and cirrus, respectively.
  cloudBitMask = 1 << 10
  cirrusBitMask = 1 << 11

  # Both flags should be set to zero, indicating clear conditions.
  mask = (qa.bitwiseAnd(cloudBitMask).eq(0))and(qa.bitwiseAnd(cirrusBitMask).eq(0))

  return image.updateMask(mask).divide(10000)

def NDVI(image):
  return image.expression('float(b("B8") - b("B4")) / (b("B8") + b("B4"))')  # for COPERNICUS/S2
  # return image.expression('float(b("B5") - b("B4")) / (b("B5") + b("B4"))')     # for LANDSAT/LC08/C01/T1_SR

def NDVI2(image):
  # return image.expression('float(b("B8") - b("B4")) / (b("B8") + b("B4"))')  # for COPERNICUS/S2
  return image.expression('float(b("B5") - b("B4")) / (b("B5") + b("B4"))')     # for LANDSAT/LC08/C01/T1_SR


def green_percentage(filename, mask_im):
    dis_area = tiff.imread(filename)
    mask_area = tiff.imread(mask_im)
    pixels_dis = np.sum((dis_area * 255) >= 1)
    pixels_mask = np.sum((mask_area * 255) >= 1)
    percentage = (pixels_mask / pixels_dis) * 100
    return percentage

@app.route('/code', methods=['GET', 'POST'])
def code():
    global polygon
    ee.Initialize()
    area = ee.Geometry.Polygon(polygon)
    poly_area_karachi = [[66.6650390625, 24.855288259359476], [66.68563842773436, 24.882699117531892], [66.70623779296875, 24.891419479211137], [66.72821044921875, 24.918822320516302], [66.76391601562499, 24.942483512016963], [66.77764892578125, 24.961160190729043], [66.80511474609375, 24.973609735832184], [66.82296752929688, 24.974854621062875], [66.83670043945312, 24.989792261044727], [66.85455322265625, 25.005972656239187], [66.87515258789062, 25.013439812256347], [66.92047119140625, 25.015928763367857], [66.93557739257811, 25.018417664026128], [66.94793701171875, 25.03210571563096], [66.96304321289062, 25.045792240303445], [66.97677612304688, 25.05201288294568], [66.98501586914062, 25.07316070640961], [67.00149536132812, 25.090573819461], [67.0220947265625, 25.104253813095614], [67.02621459960938, 25.121662500982776], [67.02072143554688, 25.132852490910697], [67.0220947265625, 25.145284610685064], [67.02346801757812, 25.16517336866393], [67.03170776367188, 25.1788450086578], [67.03582763671875, 25.197485682706866], [67.04681396484375, 25.21488107113259], [67.060546875, 25.21860833090542], [67.07839965820312, 25.232273973019627], [67.10723876953125, 25.247180194609925], [67.12234497070311, 25.227304826281653], [67.13882446289062, 25.232273973019627], [67.14981079101562, 25.24469595130604], [67.15393066406249, 25.25960064916269], [67.15530395507812, 25.272019833438247], [67.15667724609375, 25.290646227089763], [67.15667724609375, 25.30554528239941], [67.17041015625, 25.315476968424402], [67.1759033203125, 25.327890430844278], [67.17727661132811, 25.345267139880555], [67.18276977539062, 25.35519556738819], [67.17727661132811, 25.371327523300355], [67.18551635742188, 25.3924199082125], [67.18002319335938, 25.40730643193396], [67.17864990234375, 25.42591200329217], [67.18002319335938, 25.443274612305746], [67.20062255859374, 25.473033261279515], [67.22259521484375, 25.45443496795258], [67.25006103515625, 25.427152272626365], [67.26654052734375, 25.389938642388444], [67.28164672851562, 25.36140042062252], [67.37091064453125, 25.227304826281653], [67.41348266601562, 25.201213475204383], [67.47528076171875, 25.158958480083598], [67.52471923828125, 25.141555107671604], [67.56317138671875, 25.13533901613099], [67.60299682617188, 25.131609209315805], [67.62908935546874, 25.12787928859755], [67.59475708007812, 25.05823320992254], [67.58514404296875, 25.035838555635017], [67.57278442382812, 25.003483503351507], [67.57415771484375, 24.93252145867791], [67.53021240234375, 24.93127614538456], [67.50686645507812, 24.883944921181765], [67.49588012695312, 24.844072974931866], [67.48077392578125, 24.81166755546185], [67.46978759765625, 24.78299415764991], [67.44644165039062, 24.77052539567319], [67.42446899414062, 24.77177232822881], [67.40936279296875, 24.77800680315638], [67.38739013671874, 24.78299415764991], [67.36541748046875, 24.77800680315638], [67.34481811523438, 24.776759933219164], [67.32421875, 24.766784522874453], [67.32421875, 24.78673454198888], [67.31048583984375, 24.804188177830667], [67.29812622070312, 24.810421023864638], [67.26791381835938, 24.812914074521444], [67.23495483398438, 24.816653556469955], [67.225341796875, 24.815407075025966], [67.21572875976561, 24.814160581042987], [67.20268249511719, 24.812914074521444], [67.20474243164062, 24.805434772108956], [67.19993591308594, 24.801071637296058], [67.1868896484375, 24.805434772108956], [67.17178344726562, 24.805434772108956], [67.16972351074219, 24.799824999147894], [67.18002319335938, 24.798578348466542], [67.18963623046875, 24.800448319788668], [67.18551635742188, 24.79047481357294], [67.18002319335938, 24.78486436391299], [67.17315673828125, 24.79047481357294], [67.16423034667969, 24.79047481357294], [67.15255737304688, 24.792344907077926], [67.14363098144531, 24.78673454198888], [67.1381378173828, 24.78174733781577], [67.12577819824219, 24.779253660568546], [67.11685180664062, 24.779253660568546], [67.10861206054688, 24.787981311712517], [67.10586547851562, 24.793591620418344], [67.09762573242188, 24.800448319788668], [67.09899902343749, 24.810421023864638], [67.09556579589844, 24.815407075025966], [67.08869934082031, 24.820392925563276], [67.08457946777344, 24.81353732934949], [67.0832061767578, 24.802941571017538], [67.08457946777344, 24.79109818120709], [67.09419250488281, 24.783617562869416], [67.10243225097656, 24.77239578981062], [67.10380554199219, 24.76616103311853], [67.08457946777344, 24.749949200947153], [67.07496643066406, 24.750572772068463], [67.06466674804688, 24.76616103311853], [67.05299377441406, 24.777383369753395], [67.03857421875, 24.792968265314457], [67.02621459960938, 24.801071637296058], [67.01866149902344, 24.80356487599092], [67.00904846191406, 24.80356487599092], [66.99737548828125, 24.809174479730263], [66.98638916015625, 24.809174479730263], [66.99085235595703, 24.79608500950604], [66.98638916015625, 24.794526647200275], [66.9778060913086, 24.808239563402278], [66.97265625, 24.818523255124294], [66.97265625, 24.824132181788887], [66.97711944580078, 24.832545095559098], [66.98123931884766, 24.835660844499756], [66.98604583740234, 24.840645879696808], [66.9891357421875, 24.840645879696808], [66.98707580566406, 24.834414554332977], [66.98810577392578, 24.828494504716478], [66.99256896972656, 24.826936549881115], [67.0004653930664, 24.826936549881115], [67.0114517211914, 24.824755380185703], [67.01385498046875, 24.82195096270788], [67.0114517211914, 24.817276792489675], [67.0224380493164, 24.816965174871672], [67.02449798583984, 24.820392925563276], [67.02449798583984, 24.82506697820823], [67.01728820800781, 24.82569017190159], [67.01179504394531, 24.82911768116273], [67.00733184814453, 24.834102979830956], [67.00561523437499, 24.838153387193202], [66.99325561523438, 24.84282676946321], [66.98844909667969, 24.844072974931866], [66.98192596435545, 24.844072974931866], [66.9784927368164, 24.83939963971898], [66.96956634521484, 24.824443781379227], [66.96887969970703, 24.83129877402803], [66.97368621826172, 24.842203662022907], [66.9781494140625, 24.8531075892375], [66.97608947753906, 24.85715737457844], [66.97059631347656, 24.86619103322823], [66.96819305419922, 24.869305934894843], [66.9620132446289, 24.863699055384146], [66.95240020751953, 24.859960994442023], [66.94038391113281, 24.85840343569803], [66.93592071533203, 24.85746889103534], [66.92939758300781, 24.855911300904335], [66.9228744506836, 24.856845857336882], [66.9180679321289, 24.85715737457844], [66.91532135009766, 24.86151853356795], [66.9070816040039, 24.863076053074888], [66.90570831298828, 24.858714949016232], [66.89952850341797, 24.85840343569803], [66.8954086303711, 24.860584012446605], [66.88819885253906, 24.865256547423], [66.88236236572266, 24.86650252692691], [66.87583923339844, 24.86712551196965], [66.8741226196289, 24.85933797329854], [66.89781188964844, 24.846876891350952], [66.90570831298828, 24.845319167850867], [66.91463470458984, 24.839711200889823], [66.93832397460938, 24.82382058141463], [66.94965362548828, 24.815718696562516], [66.95926666259766, 24.807304640022597], [66.96304321289062, 24.806992997329047], [66.9671630859375, 24.809174479730263], [66.96853637695312, 24.806369709591422], [66.96990966796875, 24.803253223895933], [66.97334289550781, 24.800136659859948], [66.97677612304688, 24.79764335223086], [66.98089599609375, 24.79172154570878], [66.97917938232422, 24.789539756248367], [66.97540283203125, 24.793279943257993], [66.96784973144531, 24.797020017490716], [66.961669921875, 24.801071637296058], [66.95102691650389, 24.810421023864638], [66.93695068359375, 24.82195096270788], [66.92390441894531, 24.83129877402803], [66.90811157226562, 24.840957437730605], [66.9012451171875, 24.844384524338167], [66.89781188964844, 24.84282676946321], [66.88922882080078, 24.84843459524055], [66.87309265136717, 24.856534339310674], [66.85558319091797, 24.86089552027181], [66.84253692626953, 24.861830039038882], [66.83738708496094, 24.859649484262647], [66.83120727539062, 24.85559978052421], [66.82674407958984, 24.85092688067188], [66.82262420654297, 24.842203662022907], [66.81747436523438, 24.839711200889823], [66.80992126464844, 24.84033432087876], [66.79859161376953, 24.84500762079767], [66.79241180419922, 24.845319167850867], [66.78142547607422, 24.843761424741214], [66.77421569824219, 24.843138322006887], [66.76254272460938, 24.8496807442321], [66.75395965576172, 24.852796061796035], [66.74674987792969, 24.849992279518798], [66.73542022705078, 24.84344987376621], [66.72958374023438, 24.83877651502455], [66.72271728515625, 24.83784182210122], [66.71550750732422, 24.83690712211998], [66.70520782470703, 24.832545095559098], [66.70040130615234, 24.832545095559098], [66.69010162353516, 24.831610355586918], [66.68529510498047, 24.83005243995204], [66.67911529541016, 24.828182915317374], [66.67327880859375, 24.826313362459228], [66.6653823852539, 24.826001767572393], [66.65336608886719, 24.83784182210122], [66.6598892211914, 24.84033432087876], [66.6592025756836, 24.845319167850867], [66.65782928466797, 24.850303814020997], [66.65782928466797, 24.854042166854427], [66.6598892211914, 24.856534339310674]]
    area_karachi = ee.Geometry.Polygon(poly_area_karachi)


    total_sqkm = area.area().divide(1000 * 1000).getInfo()
    print("selected area :", total_sqkm)
    total_sqkm_karachi = area_karachi.area().divide(1000 * 1000).getInfo()
    print("karachi area :", total_sqkm_karachi)



    dt = datetime.date(2014, 1, 1)  # add the starting date according to your satellite, year, month, day
    dend = datetime.date.today()    # today"s date. can be changed later

    #coll = ee.ImageCollection("COPERNICUS/S2").filterBounds(area)             # for COPERNICUS/S2
    coll = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR").filterBounds(area)      # for LANDSAT/LC08/C01/T1_SR

    #coll_south = ee.ImageCollection("COPERNICUS/S2").filterBounds(area_south)  # for COPERNICUS/S2
    #coll_south2 = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR").filterBounds(area_south)  # for LANDSAT/LC08/C01/T1_SR
    #coll_malir = ee.ImageCollection("COPERNICUS/S2").filterBounds(area_malir)  # for COPERNICUS/S2
    #coll_korangi = ee.ImageCollection("COPERNICUS/S2").filterBounds(area_korangi)  # for COPERNICUS/S2
    #coll_east = ee.ImageCollection("COPERNICUS/S2").filterBounds(area_east)  # for COPERNICUS/S2
    #coll_central = ee.ImageCollection("COPERNICUS/S2").filterBounds(area_central)  # for COPERNICUS/S2
    #coll_west = ee.ImageCollection("COPERNICUS/S2").filterBounds(area_west)  # for COPERNICUS/S2

    coll_karachi = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR").filterBounds(area_karachi)  # for LANDSAT/LC08/C01/T1_SR


    sc1 = int((total_sqkm/4))+1
    print(sc1)
    scale_karachi = 80


    df = dt
    w = dt.strftime("%Y-%m-%d")
    out_dir = os.path.join(os.path.expanduser('./'), 'Downloads')

    if os.path.exists(out_dir) is False:
        os.mkdir('./Downloads')

    a = 1
    while df < dend:  # set while condition for new date less than today
        df = df + datetime.timedelta(days=30)  # get images of 30 days
        q = w
        w = df.strftime("%Y-%m-%d")
        #collredim = coll.filterDate("" + q + "", "" + w + "").sort('CLOUDY_PIXEL_PERCENTAGE').first().clip(area)      # for COPERNICUS/S2
        collredim = coll.filterDate("" + q + "", "" + w + "").sort('IMAGE_QUALITY', True).first()                     # for LANDSAT/LC08/C01/T1_SR
        # collredim = coll.filterDate("" + q + "", "" + w + "").median()                                                  # for LANDSAT/LC08/C01/T1_SR
        ndviim = coll.filterDate("" + q + "", "" + w + "").map(NDVI2).median()
        ndvimask=ndviim.clip(area).mask()
        ndviim2=ndviim.mask(ndvimask)
        print(q)
        rgbim = collredim.select(['B4', 'B3', 'B2'])

        # #collredim_s = coll_south.filterDate("" + q + "", "" + w + "").sort('CLOUDY_PIXEL_PERCENTAGE').first().clip(area_south)  # for COPERNICUS/S2
        # collredim_s = coll_south.filterDate("" + q + "", "" + w + "").sort('IMAGE_QUALITY', True).first()  # for LANDSAT
        # ndviim_s = coll_south.filterDate("" + q + "", "" + w + "").map(NDVI2).median()
        # ndvimask_s = ndviim_s.clip(area_south).mask()
        # #ndviim2_s_mask = ndviim_s.mask(ndvimask_s).gt(0.2)
        # ndviim2_s = ndviim_s.mask(ndvimask_s)
        # # NDVI_count = ndviim2_s_mask.count()
        # # print("no. of pixels greater than 0.2 = ", NDVI_count)
        # rgbim_s = collredim_s.select(['B4', 'B3', 'B2'])
        # #NDVI_count = col.select('NDVI').map(function(img){return img.updateMask(img.select('NDVI').lt(0.25))}).count()


        #thresholds = ee.Image([-0.2, 0, 0.1, 0.2, 0.3, 0.4, 1])     #Define the thresholds
        #classified = ndviim2_s.gt(thresholds).reduce('sum').toInt()   #Create the classified Image
        #print(classified, 'Classified')
        #Define new visualization parameters for the classification: The values are now ranging from 0 to 7, one for each class
        #classifiedParams = {min: 0, max: 7, palette: ['blue', 'white', 'brown', 'burlywood', 'LimeGreen', 'ForestGreen', 'DarkGreen']}
        # First, we want to count the number of pixels in the entire layer for future reference.
        #allpix = classified.updateMask(classified) # mask the entire layer
        # pixstats = allpix.reduceRegion(
        #                reducer= ee.Reducer.count(),               # count all pixels in a single class
        #                geometry=area_south,
        #                scale=30,
        #                maxPixels=1e10)
        # allpixels = ee.Number(pixstats.get('sum'))                    #extract pixel count as a number
        # print(allpixels)
        # Then, we want to create an empty list to store the area values we will calculate in
        #arealist = []

        #Now, we can create a function to derive the extent of one NDVI class
        #The arguments are class number (cnr) and class name (name)
        # def areacount(cnr, name):
        #     singleMask =  classified.updateMask(classified.eq(cnr))  #mask a single class
        #     stats = singleMask.reduceRegion(
        #         reducer= ee.Reducer.count(),               #count pixels in a single class
        #         geometry= area_south,
        #         scale= 30,
        #         maxPixels= 1e10 )
        #     pix =  ee.Number(stats.get('sum'))
        #     hect = pix.multiply(900).divide(10000)              # Landsat pixel = 30m x 30m --> 900 sqm
        #     perc = pix.divide(allpixels).multiply(10000).round().divide(100)   # get area percent by class and round to 2 decimals
        #     arealist.push(Class= name, Pixels= pix, Hectares= hect, Percentage= perc)

        #Create a list that contains the NDVI class names (7 classes, ranging from [-0.2, 0, 0.1, 0.2, 0.3, 0.4, 1])
        #     names2 = ['Water', 'No Vegetation', 'Very Low Vegetation', 'Low Vegetation', 'Moderate Vegetation','Moderate-high Vegetation', 'High Vegetation']
        #     for i in range (6):
        #       areacount(i, names2[i])
        #
        # #Print the results to the Console and examine it.
        # print('Vegetated Area by NDVI Class', arealist, '--> click list objects for individual classes')


        # collredim_s2 = coll_south2.filterDate("" + q + "", "" + w + "").sort('IMAGE_QUALITY', True).first()   # for LANDSAT
        collredim_s2 = coll_karachi.filterDate("" + q + "", "" + w + "").median()
        ndviim_s2 = coll_karachi.filterDate("" + q + "", "" + w + "").map(NDVI2).median()
        ndvimask_s2 = ndviim_s2.clip(area_karachi).mask()
        ndviim2_s2_mask = ndviim_s2.mask(ndvimask_s2).gt(0.3)     # mask for ndvi values greater than 0.2
        ndviim2_s2o = ndviim_s2.mask(ndvimask_s2)
        ndviim2_s2m = ndviim_s2.mask(ndviim2_s2_mask)
        rgbim_s2 = collredim_s2.select(['B4', 'B3', 'B2'])
        rgbim_s2 = rgbim_s2.mask(ndvimask_s2)

#### ndvimask_s2 full area mask
#### ndviim2_s2o grayscale area
#### ndviim2_s2m ndvi mask



        filename = os.path.join(out_dir, '{}.tif'.format(a))
        filename2 = os.path.join(out_dir, 'ndvi{}.tif'.format(a))
        #geemap.ee_export_image(rgbim, filename=filename, scale=sc1, region=area, file_per_band=False)
        # geemap.ee_export_image(rgbim, filename=filename, scale=sc1, region=area, file_per_band=True) # for rgb separate bands
        #geemap.ee_export_image(ndviim2, filename=filename2, scale=sc1, region=area, file_per_band=False)

        # filename = os.path.join(out_dir, 'south{}.tif'.format(a))
        # filename2 = os.path.join(out_dir, 'ndvi_s{}.tif'.format(a))
        # geemap.ee_export_image(rgbim_s, filename=filename, scale=scale_south, region=area_south, file_per_band=False)
        # geemap.ee_export_image(ndviim2_s, filename=filename2, scale=scale_south, region=area_south, file_per_band=False)
        if os.path.exists(os.path.join(out_dir,'karachi')) is False:
            os.mkdir('./Downloads/karachi')

        filename = os.path.join(out_dir, 'karachi/karachi.tif')
        filename2 = os.path.join(out_dir, 'karachi/ndvi_k_ls{}.tif'.format(a))
        filename3 = os.path.join(out_dir, 'karachi/karachirgb{}.tif'.format(a))
        mask_im = os.path.join(out_dir, 'karachi/karachi_mask{}.tif'.format(a))
        geemap.ee_export_image(ndviim2_s2o, filename=filename2, scale=scale_karachi, region=area_karachi, file_per_band=False)
        geemap.ee_export_image(ndviim2_s2m, filename=mask_im, scale=scale_karachi, region=area_karachi, file_per_band=False)
        geemap.ee_export_image(rgbim_s2, filename=filename3, scale=scale_karachi, region=area_karachi, file_per_band=False)

        area_rgb = tiff.imread(filename3)
        min_area = np.amin(area_rgb)
        max_area = np.amax(area_rgb)
        #area1 = (area_rgb/6000)*255
        area1 = ((area_rgb - min_area)/(max_area - min_area))*255
        area1 = area1.astype(np.uint8)
        #print(area1)
        area1 = cv2.cvtColor(area1, cv2.COLOR_BGR2RGB)
        cv2.imwrite(os.path.join(out_dir, 'karachi/karachirgb{}.jpg'.format(a)), area1)
        #cv2.imshow('', area1)
        #cv2.waitKey()

        if a == 1:
            geemap.ee_export_image(ndvimask_s2, filename=filename, scale=scale_karachi, region=area_karachi, file_per_band=False)
        percentage = green_percentage(filename, mask_im)
        #print(percentage)
        greenarea = total_sqkm_karachi * (percentage/100)
        nongreen_area = total_sqkm_karachi - greenarea
        with open('./Downloads/karachi.csv', 'a', newline="") as f:
            thewriter = csv.writer(f)
            if a == 1:
                thewriter.writerow(['Date', 'TotalArea', 'GreenArea', 'NongreenArea', 'Percentage'])
            thewriter.writerow([w, total_sqkm_karachi, greenarea, nongreen_area, percentage])
        a = a + 1




        #MASKING
        # ndvi = (arr ** 2).copy()
        # ndvi[ndvi < 0.15] = 0
        # ndvi[ndvi >= 0.15] = 1
        # blue = rgb[:, :, 0]
        # red = rgb[:, :, 2]
        # blue[ndvi == 1] -= 0.5
        # red[ndvi == 1] -= 0.5
        # output = rgb.copy()
        # output[:, :, 0] = blue
        # output[:, :, 2] = red
        # output *= 255
        # output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
        # rgb1=rgb.copy()
        # rgb1 *=255
        # rgb2=cv2.cvtColor(rgb1,cv2.COLOR_BGR2RGB)
        #cv2.imwrite("/Users/admin/PycharmProjects/greenarea/static/l.jpg", output)
        #cv2.imwrite("E:/greenarea/static/l.jpg", output)
    # cv2.imwrite("D:/Green area project/greenarea main/static1/1.jpg", ndvi)
    #     # cv2.imwrite("D:/Green area project/greenarea main/static1/{}.jpg".format(a), rgb2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

        # CALCULATIONS
        # total_img = np.sum(rgb, axis=-1)
        # total_pixels = len(total_img[total_img != 0])
        # green_pixels = len(ndvi[ndvi != 0])
        # build_pixels = total_pixels - green_pixels
        # percent = (green_pixels / total_pixels) * 100
        # total = total_sqkm
        # green = (percent / 100) * total
        # nongreen = total - green
        # build = total_sqkm - green
        # print(percent)

    #     with open('main.csv', 'a', newline="") as f:
    #         thewriter = csv.writer(f)
    #         if a == 2:
    #             thewriter.writerow(['Date', 'TotalArea', 'GreenArea', 'NongreenArea', 'Percentage', 'Coordinates'])
    #         thewriter.writerow([w, total, green, nongreen, percent, polygon])
    #
    # if percent < 30:
    #     p1 = "Plantation less than 30% is not considered as optimal so kindly plant more trees."
    # else:
    #     p1 = "Plantation is above 30%, you can plant more if you need or help others to plant trees."
    #
    #
    # return render_template("resultnew.html", b=total, c=green, d=build, e=percent, f=p1)


if __name__ == '__main__':
    app.debug = False
    app.run()
