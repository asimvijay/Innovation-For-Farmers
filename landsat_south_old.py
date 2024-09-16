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

@app.route('/code', methods=['GET', 'POST'])
def code():
    global polygon
    ee.Initialize()
    area = ee.Geometry.Polygon(polygon)
    poly_area_south = [[66.97677612304688, 24.8727322360673], [66.99394226074219, 24.881453301317965], [67.00424194335938, 24.882699117531892], [67.0111083984375, 24.879584553440623], [67.0166015625, 24.879584553440623], [67.02484130859375, 24.886436490787712], [67.03170776367188, 24.890796616653954], [67.03479766845703, 24.87740431185819], [67.03857421875, 24.87242075806748], [67.05024719238281, 24.860272503836693], [67.05642700195312, 24.849369208160923], [67.06707000732422, 24.841580551445354], [67.07462310791016, 24.835660844499756], [67.08457946777344, 24.828494504716478], [67.0931625366211, 24.824132181788887], [67.09178924560547, 24.819146481739068], [67.0876693725586, 24.818523255124294], [67.08732604980469, 24.81353732934949], [67.08148956298828, 24.812914074521444], [67.07977294921875, 24.806992997329047], [67.07839965820312, 24.800136659859948], [67.07977294921875, 24.793591620418344], [67.0883560180664, 24.788293002185807], [67.09281921386719, 24.783305860651126], [67.09762573242188, 24.777695086846297], [67.10174560546875, 24.773019248261697], [67.10277557373047, 24.76740800950013], [67.1048355102539, 24.762420028851665], [67.10037231445312, 24.75930243922547], [67.09590911865234, 24.757743615072602], [67.09178924560547, 24.754002357308305], [67.0880126953125, 24.75119634006102], [67.08423614501953, 24.749325626697196], [67.08011627197266, 24.748390259456198], [67.0773696899414, 24.747454885176023], [67.07496643066406, 24.747143092185084], [67.07084655761719, 24.749013838399], [67.06947326660156, 24.75431413309125], [67.05745697021484, 24.770837129986052], [67.05196380615234, 24.778941947389757], [67.0440673828125, 24.78673454198888], [67.03788757324219, 24.792968265314457], [67.02827453613281, 24.799824999147894], [67.01316833496092, 24.805434772108956], [67.00492858886719, 24.806681353851964], [67.00149536132812, 24.817900025374463], [67.01042175292969, 24.81976970521875], [67.02140808105467, 24.821016142772585], [67.02346801757812, 24.827248142416146], [67.01591491699219, 24.83223351635245], [67.01042175292969, 24.83908807776389], [67.00218200683594, 24.84469607296012], [66.99050903320312, 24.84656534821976], [66.98707580566406, 24.852173004559464], [66.98638916015625, 24.86089552027181], [66.98020935058594, 24.86712551196965]]
    area_south = ee.Geometry.Polygon(poly_area_south)
    poly_area_malir = [[67.08526611328125, 25.23972731233395], [67.115478515625, 25.25711665985981], [67.12921142578125, 25.289404556494823], [67.14569091796874, 25.321683858702098], [67.1649169921875, 25.341543769441667], [67.15393066406249, 25.36140042062252], [67.181396484375, 25.39614171131381], [67.17041015625, 25.428392529196845], [67.18414306640625, 25.46559428893416], [67.203369140625, 25.485430526043555], [67.21435546875, 25.517657429994035], [67.25830078125, 25.54244147012483], [67.2747802734375, 25.572175556682115], [67.2857666015625, 25.58951703179726], [67.33245849609375, 25.631621577258493], [67.37640380859375, 25.634097853244732], [67.401123046875, 25.631621577258493], [67.43133544921875, 25.53252846853444], [67.3846435546875, 25.366364073894893], [67.35992431640625, 25.371327523300355], [67.35443115234375, 25.351472502592568], [67.3736572265625, 25.336579097268118], [67.35443115234375, 25.309269760067775], [67.3297119140625, 25.289404556494823], [67.3077392578125, 25.264568475331583], [67.29949951171875, 25.227304826281653], [67.32696533203125, 25.19500042430748], [67.36541748046875, 25.160201483133374], [67.41485595703125, 25.13533901613099], [67.47802734375, 25.090573819461], [67.5164794921875, 25.05823320992254], [67.5384521484375, 24.97609949369541], [67.5439453125, 24.928785481052262], [67.58514404296875, 24.864010555361574], [67.59063720703125, 24.776759933219164], [67.5164794921875, 24.79670834894575], [67.42584228515625, 24.844072974931866], [67.4285888671875, 24.811044291230406], [67.43064880371094, 24.79733168525243], [67.43820190429688, 24.787357928416778], [67.44369506835938, 24.781123923201235], [67.43476867675781, 24.777383369753395], [67.42515563964844, 24.77239578981062], [67.41691589355469, 24.78486436391299], [67.40867614746094, 24.78985144280632], [67.40180969238281, 24.787981311712517], [67.39768981933594, 24.78174733781577], [67.3798370361328, 24.78174733781577], [67.36679077148438, 24.78174733781577], [67.35580444335938, 24.776136493553793], [67.34344482421875, 24.776759933219164], [67.32902526855469, 24.76803149299553], [67.3249053955078, 24.7630435373877], [67.32009887695312, 24.76553754023245], [67.32215881347656, 24.773642703581935], [67.32353210449219, 24.78050050545515], [67.33108520507812, 24.789228068907338], [67.32215881347656, 24.798578348466542], [67.30705261230469, 24.81166755546185], [67.29812622070312, 24.812914074521444], [67.29057312011719, 24.807927923059236], [67.27134704589844, 24.809797753364574], [67.25486755371092, 24.812914074521444], [67.2418212890625, 24.816653556469955], [67.22396850585936, 24.815407075025966], [67.21160888671875, 24.814160581042987], [67.19993591308594, 24.814160581042987], [67.19924926757812, 24.809174479730263], [67.20474243164062, 24.80605806454742], [67.20199584960938, 24.80169495167004], [67.18826293945312, 24.806681353851964], [67.17727661132811, 24.804811476536706], [67.16766357421875, 24.80356487599092], [67.17658996582031, 24.79483832122786], [67.18208312988281, 24.79172154570878], [67.17109680175781, 24.79047481357294], [67.16354370117188, 24.78860469187607], [67.14912414550781, 24.79172154570878], [67.1429443359375, 24.802941571017538], [67.19718933105469, 24.82974085447296], [67.20680236816406, 24.83908807776389], [67.20542907714844, 24.84656534821976], [67.19993591308594, 24.85092688067188], [67.16423034667969, 24.84282676946321], [67.15667724609375, 24.86712551196965], [67.16285705566406, 24.8689944482603], [67.17384338378906, 24.86774849387282], [67.18757629394531, 24.865256547423], [67.19924926757812, 24.862764550743062], [67.19032287597656, 24.87148631935797], [67.18826293945312, 24.87584697288821], [67.19581604003906, 24.880207472540516], [67.20611572265625, 24.88083038849967], [67.20954895019531, 24.89577942913762], [67.21641540527344, 24.90512166048925], [67.22190856933594, 24.910726659859982], [67.20062255859374, 24.911972180697553], [67.18482971191405, 24.9113494218506], [67.18757629394531, 24.91633140459907], [67.18070983886719, 24.923804001418254], [67.17109680175781, 24.923804001418254], [67.15873718261719, 24.920690474438743], [67.15118408203125, 24.91695413829471], [67.14431762695312, 24.91570866775934], [67.15530395507812, 24.94061568836632], [67.1484375, 24.99414873086723], [67.14981079101562, 25.001616605587664], [67.18620300292969, 25.002861207248976], [67.203369140625, 25.009706290997322], [67.22053527832031, 25.025261880656924], [67.23426818847656, 25.042059703222566], [67.24868774414062, 25.05761119143144], [67.25761413574219, 25.068807041169084], [67.26448059082031, 25.07502651556338], [67.24319458007812, 25.111093236145866], [67.23014831542969, 25.124770934331977], [67.19856262207031, 25.136582259755453], [67.17933654785156, 25.145284610685064], [67.1649169921875, 25.149635553515335], [67.15324401855469, 25.140311914680755], [67.14088439941406, 25.134095759849245], [67.12783813476562, 25.130365915065003], [67.11204528808594, 25.132852490910697], [67.06878662109375, 25.145906183442673], [67.05986022949217, 25.150878651548457], [67.0880126953125, 25.19375777608886], [67.11410522460938, 25.21860833090542], [67.12509155273438, 25.227304826281653]]
    area_malir = ee.Geometry.Polygon(poly_area_malir)
    poly_area_korangi = [[67.15187072753906, 24.79483832122786], [67.1429443359375, 24.79047481357294], [67.14019775390625, 24.78237074929868], [67.13058471679686, 24.78050050545515], [67.12577819824219, 24.77800680315638], [67.11891174316406, 24.777383369753395], [67.11341857910156, 24.78299415764991], [67.10723876953125, 24.79172154570878], [67.09968566894531, 24.798578348466542], [67.09556579589844, 24.80605806454742], [67.09419250488281, 24.812914074521444], [67.08869934082031, 24.817276792489675], [67.08663940429688, 24.82537857544687], [67.08045959472656, 24.82974085447296], [67.08492279052734, 24.843138322006887], [67.08904266357422, 24.848123056031515], [67.09041595458984, 24.852796061796035], [67.09178924560547, 24.861830039038882], [67.09590911865234, 24.86432205455417], [67.1041488647461, 24.86712551196965], [67.11479187011717, 24.868371472636408], [67.12200164794922, 24.869305934894843], [67.12406158447266, 24.875224031804528], [67.12028503417969, 24.879584553440623], [67.11994171142578, 24.884567818295064], [67.12955474853516, 24.886747933454497], [67.14637756347656, 24.887059375335962], [67.16011047363281, 24.887370816432064], [67.16869354248047, 24.8855021580753], [67.1769332885742, 24.884567818295064], [67.17864990234375, 24.892042338626545], [67.18208312988281, 24.90325327078814], [67.18482971191405, 24.912594936400822], [67.203369140625, 24.909481126447975], [67.21435546875, 24.90823558046204], [67.20680236816406, 24.896402266558727], [67.20130920410156, 24.880207472540516], [67.19512939453125, 24.87646991083154], [67.19169616699219, 24.86961742074445], [67.20062255859374, 24.86338755462191], [67.20268249511719, 24.85840343569803], [67.19169616699219, 24.85840343569803], [67.17315673828125, 24.86214154372506], [67.16148376464842, 24.865256547423], [67.15736389160156, 24.862764550743062], [67.159423828125, 24.847188433697745], [67.16045379638672, 24.84500762079767], [67.19856262207031, 24.852173004559464], [67.20199584960938, 24.852173004559464], [67.20611572265625, 24.84781151603803], [67.20611572265625, 24.840957437730605], [67.20405578613281, 24.83223351635245], [67.18551635742188, 24.81976970521875], [67.17247009277344, 24.81229081655887], [67.16011047363281, 24.80605806454742]]
    area_korangi = ee.Geometry.Polygon(poly_area_korangi)
    poly_area_east = [[67.09213256835938, 25.00783948780488], [67.11307525634766, 25.009084026419178], [67.13882446289062, 25.00472808609992], [67.14775085449219, 25.002861207248976], [67.15667724609375, 24.96365020050899], [67.15667724609375, 24.9431061136075], [67.14775085449219, 24.918822320516302], [67.15530395507812, 24.91695413829471], [67.17109680175781, 24.918822320516302], [67.18276977539062, 24.918822320516302], [67.18208312988281, 24.905744450770186], [67.17453002929688, 24.88581360309809], [67.137451171875, 24.887059375335962], [67.12440490722656, 24.887059375335962], [67.12509155273438, 24.87865016890194], [67.12646484375, 24.872109279282647], [67.11685180664062, 24.867437003313704], [67.10552215576172, 24.866814019840735], [67.09693908691406, 24.864010555361574], [67.09075927734375, 24.85933797329854], [67.0883560180664, 24.846876891350952], [67.08457946777344, 24.842515216135208], [67.08045959472656, 24.83129877402803], [67.06466674804688, 24.84189210712628], [67.05951690673828, 24.846876891350952], [67.0547103881836, 24.854042166854427], [67.05024719238281, 24.858714949016232], [67.04235076904297, 24.865879538744686], [67.03617095947266, 24.87242075806748], [67.03033447265625, 24.889550882114328], [67.03754425048828, 24.892042338626545], [67.04338073730469, 24.894222321837816], [67.05368041992188, 24.89733651679859], [67.06020355224608, 24.900139225095582], [67.06295013427734, 24.90449886706521], [67.06535339355469, 24.90885835502671], [67.06844329833984, 24.911972180697553], [67.07565307617186, 24.91415181190483], [67.07839965820312, 24.91726550396347], [67.07908630371094, 24.921624540787306], [67.08114624023438, 24.925983423525253], [67.08457946777344, 24.933144110606197], [67.0835494995117, 24.944040010093424], [67.08251953125, 24.95182220545605], [67.0821762084961, 24.95586875269946], [67.0876693725586, 24.962405201915775], [67.0883560180664, 24.9739209583209], [67.08904266357422, 24.987925155284486], [67.09041595458984, 25.0003719913183]]
    area_east = ee.Geometry.Polygon(poly_area_east)
    poly_area_central = [[67.09144592285155, 25.00783948780488], [67.06466674804688, 25.007217213768804], [67.03582763671875, 25.001616605587664], [67.04132080078125, 24.989792261044727], [67.04063415527344, 24.973609735832184], [67.03720092773438, 24.958670130576788], [67.03170776367188, 24.948709386318527], [67.02346801757812, 24.93376675938881], [67.01728820800781, 24.92754013001425], [67.01042175292969, 24.926294766395593], [67.01385498046875, 24.918199596253377], [67.01454162597656, 24.906990021902633], [67.01591491699219, 24.898893584819813], [67.0166015625, 24.892665194900047], [67.02072143554688, 24.8851907122672], [67.02690124511719, 24.882699117531892], [67.03445434570312, 24.887059375335962], [67.04200744628906, 24.891419479211137], [67.05024719238281, 24.89577942913762], [67.06192016601562, 24.898893584819813], [67.0660400390625, 24.905744450770186], [67.071533203125, 24.910726659859982], [67.08045959472656, 24.914463184647705], [67.08045959472656, 24.924426697379943], [67.08457946777344, 24.93376675938881], [67.08251953125, 24.946219074360084], [67.08183288574219, 24.956802552408], [67.08732604980469, 24.961782697896567], [67.08938598632812, 24.976721925287233], [67.09075927734375, 24.992281691278635]]
    area_central = ee.Geometry.Polygon(poly_area_central)
    poly_area_west = [[66.66641235351562, 24.824132181788887], [66.654052734375, 24.835349273134295], [66.6595458984375, 24.84781151603803], [66.6595458984375, 24.857780406707583], [66.67877197265625, 24.87646991083154], [66.68975830078125, 24.883944921181765], [66.70211791992188, 24.891419479211137], [66.71585083007812, 24.90512166048925], [66.72271728515625, 24.921313186123925], [66.75430297851562, 24.93874783639836], [66.77352905273438, 24.957425081612215], [66.77764892578125, 24.967385120722803], [66.8023681640625, 24.974854621062875], [66.8243408203125, 24.97609949369541], [66.83395385742186, 24.99352638748893], [66.85317993164062, 25.005972656239187], [66.88339233398438, 25.018417664026128], [66.93695068359375, 25.017173220003865], [66.94793701171875, 25.03459428825369], [66.97540283203125, 25.05201288294568], [66.99874877929688, 25.090573819461], [67.01797485351562, 25.105497373014686], [67.02896118164061, 25.120419105501256], [67.01934814453125, 25.132852490910697], [67.02072143554688, 25.150257104114733], [67.02621459960938, 25.16890214979725], [67.0330810546875, 25.18381613394528], [67.03994750976562, 25.203698606796376], [67.04681396484375, 25.216123503743905], [67.06466674804688, 25.22233547648819], [67.07977294921875, 25.236000699800467], [67.10861206054688, 25.249664387120884], [67.115478515625, 25.23972731233395], [67.12921142578125, 25.22606250786859], [67.10586547851562, 25.19251511519153], [67.08938598632812, 25.171387940538974], [67.0770263671875, 25.153986341229828], [67.11959838867188, 25.130365915065003], [67.14569091796874, 25.12663595638182], [67.16354370117188, 25.14652775303499], [67.17521667480469, 25.147149319461974], [67.19856262207031, 25.13533901613099], [67.21504211425781, 25.129744263193796], [67.23014831542969, 25.122284193978963], [67.24319458007812, 25.109849733138773], [67.25761413574219, 25.090573819461], [67.26516723632812, 25.073782645952882], [67.22259521484375, 25.028994928869533], [67.203369140625, 25.010328552422727], [67.18620300292969, 25.00472808609992], [67.11341857910156, 25.010328552422727], [67.07565307617186, 25.006594936580242], [67.05230712890624, 25.005350372745724], [67.03514099121094, 25.000994300028957], [67.03994750976562, 24.99041462332972], [67.03926086425781, 24.97983403599961], [67.03651428222655, 24.965517674784913], [67.02552795410156, 24.948086813049457], [67.01591491699219, 24.933144110606197], [67.00973510742188, 24.93127614538456], [67.01454162597656, 24.921313186123925], [67.01385498046875, 24.910726659859982], [67.01934814453125, 24.88768225674282], [67.01728820800781, 24.881453301317965], [67.00973510742188, 24.8789616312], [66.99806213378905, 24.88083038849967], [66.98844909667969, 24.87584697288821], [66.97746276855469, 24.87148631935797], [66.98432922363281, 24.862764550743062], [66.98638916015625, 24.855911300904335], [66.99119567871094, 24.84843459524055], [67.0001220703125, 24.842203662022907], [67.01385498046875, 24.841580551445354], [67.01866149902344, 24.83597241508107], [67.02278137207031, 24.830364024647107], [67.02140808105467, 24.82537857544687], [67.01728820800781, 24.819146481739068], [67.00767517089844, 24.8147838296018], [66.9891357421875, 24.815407075025966], [66.97471618652344, 24.819146481739068], [66.97471618652344, 24.82537857544687], [66.98020935058594, 24.834102979830956], [66.98844909667969, 24.844072974931866], [66.97952270507812, 24.84033432087876], [66.97402954101562, 24.832856673981677], [66.96784973144531, 24.823508980256506], [66.961669921875, 24.8147838296018], [66.961669921875, 24.824132181788887], [66.96853637695312, 24.82755973416718], [66.97025299072266, 24.83379140454481], [66.97368621826172, 24.842515216135208], [66.9784927368164, 24.849057671305268], [66.97437286376952, 24.84843459524055], [66.97677612304688, 24.854042166854427], [66.97917938232422, 24.85559978052421], [66.97437286376952, 24.859960994442023], [66.97265625, 24.86432205455417], [66.96784973144531, 24.868371472636408], [66.95686340332031, 24.86089552027181], [66.939697265625, 24.856534339310674], [66.92939758300781, 24.85715737457844], [66.92115783691406, 24.85715737457844], [66.91497802734375, 24.860272503836693], [66.90605163574219, 24.862764550743062], [66.90536499023438, 24.859026461549753], [66.89849853515625, 24.859649484262647], [66.89918518066406, 24.863076053074888], [66.90055847167969, 24.866814019840735], [66.89987182617188, 24.869928905809125], [66.8964385986328, 24.868059983647058], [66.89472198486328, 24.861830039038882], [66.88751220703125, 24.864945050584907], [66.88030242919922, 24.86650252692691], [66.87515258789062, 24.86650252692691], [66.8741226196289, 24.85933797329854], [66.88030242919922, 24.85559978052421], [66.88322067260742, 24.85326335266401], [66.89111709594727, 24.849213439831146], [66.8986701965332, 24.845942259604115], [66.90055847167969, 24.847188433697745], [66.9041633605957, 24.85139417860071], [66.90862655639648, 24.85544402003992], [66.91034317016602, 24.857936164249455], [66.9125747680664, 24.858091921595147], [66.9148063659668, 24.856690098421854], [66.9173812866211, 24.854197929104078], [66.91600799560547, 24.852796061796035], [66.91308975219727, 24.85139417860071], [66.91034317016602, 24.85077111430336], [66.90811157226562, 24.848590364550905], [66.90570831298828, 24.845942259604115], [66.90313339233398, 24.846253804304137], [66.90313339233398, 24.84500762079767], [66.90879821777344, 24.84282676946321], [66.9228744506836, 24.833947192285894], [66.93197250366211, 24.828182915317374], [66.94913864135742, 24.815407075025966], [66.95240020751953, 24.813381515936342], [66.95840835571289, 24.807148818773758], [66.95926666259766, 24.808395383279993], [66.9620132446289, 24.80746046107559], [66.96493148803711, 24.809330298432673], [66.96699142456055, 24.811355923737935], [66.9675064086914, 24.808083743328694], [66.96922302246094, 24.804188177830667], [66.9729995727539, 24.801227466183317], [66.97574615478516, 24.79826668383793], [66.97746276855469, 24.79592917415661], [66.98055267333984, 24.791565704877037], [66.98123931884766, 24.78969559962524], [66.98038101196289, 24.78860469187607], [66.9781494140625, 24.790163128581167], [66.97488784790039, 24.793747458704804], [66.9707679748535, 24.797175851469483], [66.96853637695312, 24.797955018426038], [66.96664810180664, 24.79779918542637], [66.9620132446289, 24.801071637296058], [66.95669174194336, 24.805902241731584], [66.95446014404297, 24.807927923059236], [66.95016860961914, 24.811355923737935], [66.94587707519531, 24.814628017755982], [66.93540573120117, 24.823353179383496], [66.92630767822266, 24.830675608558128], [66.91617965698241, 24.83737447299281], [66.90896987915039, 24.841424773310766], [66.90073013305664, 24.84469607296012], [66.89849853515625, 24.84344987376621], [66.89455032348633, 24.845319167850867], [66.88751220703125, 24.849524976294575], [66.88047409057617, 24.852951825614817], [66.87789916992188, 24.854353691157602], [66.87223434448242, 24.856845857336882], [66.86639785766602, 24.858559192455218], [66.86141967773438, 24.859960994442023], [66.8569564819336, 24.860584012446605], [66.84906005859375, 24.861830039038882], [66.84219360351562, 24.86151853356795], [66.83601379394531, 24.860584012446605], [66.83120727539062, 24.855288259359476], [66.82708740234375, 24.8496807442321], [66.8243408203125, 24.845942259604115], [66.82193756103516, 24.842203662022907], [66.82228088378906, 24.83939963971898], [66.81816101074217, 24.83877651502455], [66.8130111694336, 24.83877651502455], [66.80442810058594, 24.844384524338167], [66.79824829101562, 24.845942259604115], [66.7917251586914, 24.845942259604115], [66.7862319946289, 24.844384524338167], [66.78142547607422, 24.84344987376621], [66.77558898925781, 24.84282676946321], [66.77043914794922, 24.84500762079767], [66.7642593383789, 24.84843459524055], [66.75430297851562, 24.852796061796035], [66.74983978271484, 24.85154994418473], [66.741943359375, 24.847499975260114], [66.73439025878906, 24.84282676946321], [66.7306137084961, 24.840957437730605], [66.7306137084961, 24.838153387193202], [66.72649383544922, 24.835349273134295], [66.72374725341797, 24.83784182210122], [66.719970703125, 24.838153387193202], [66.71550750732422, 24.83690712211998], [66.70898437499999, 24.83503770098466], [66.70589447021484, 24.83223351635245], [66.70108795166016, 24.831921936361706], [66.6935348510742, 24.83129877402803], [66.68872833251953, 24.83005243995204], [66.68563842773436, 24.830364024647107], [66.6815185546875, 24.828494504716478], [66.67671203613281, 24.826624956562167], [66.67121887207031, 24.82506697820823]]
    area_west = ee.Geometry.Polygon(poly_area_west)

    total_sqkm = area.area().divide(1000 * 1000).getInfo()
    print("selected area :", total_sqkm)
    total_sqkm_south = area_south.area().divide(1000 * 1000).getInfo()
    print("south area :", total_sqkm_south)
    total_sqkm_malir = area_malir.area().divide(1000 * 1000).getInfo()
    print("malir area :", total_sqkm_malir)
    total_sqkm_korangi = area_korangi.area().divide(1000 * 1000).getInfo()
    print("korangi area :", total_sqkm_korangi)
    total_sqkm_east = area_east.area().divide(1000 * 1000).getInfo()
    print("east area :", total_sqkm_east)
    total_sqkm_central = area_central.area().divide(1000 * 1000).getInfo()
    print("central area :", total_sqkm_central)
    total_sqkm_west = area_west.area().divide(1000 * 1000).getInfo()
    print("west area :", total_sqkm_west)


    dt = datetime.date(2010, 4, 1)  # add the starting date according to your satellite, year, month, day
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

    coll_south = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR").filterBounds(area_south)  # for LANDSAT/LC08/C01/T1_SR
    coll_malir = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR").filterBounds(area_malir)  # for LANDSAT/LC08/C01/T1_SR
    coll_korangi = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR").filterBounds(area_korangi)  # for LANDSAT/LC08/C01/T1_SR
    coll_east = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR").filterBounds(area_east)  # for LANDSAT/LC08/C01/T1_SR
    coll_central = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR").filterBounds(area_central)  # for LANDSAT/LC08/C01/T1_SR
    coll_west = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR").filterBounds(area_west)  # for LANDSAT/LC08/C01/T1_SR


    sc1 = int((total_sqkm/4))+1
    print(sc1)
    scale_south = 14
    #scale_south2 = 6
    scale_malir = 34
    scale_korangi = 16
    scale_east = 18
    scale_central = 10
    scale_west = 25

    df = dt
    w = dt.strftime("%Y-%m-%d")
    out_dir = os.path.join(os.path.expanduser('D:\MY_WORK\THESIS\Faraz_Work\work\greenarea main'), 'Downloads')

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

        #collredim_s = coll_south.filterDate("" + q + "", "" + w + "").sort('CLOUDY_PIXEL_PERCENTAGE').first().clip(area_south)  # for COPERNICUS/S2
        collredim_s = coll_south.filterDate("" + q + "", "" + w + "").sort('IMAGE_QUALITY', True).first()  # for LANDSAT
        ndviim_s = coll_south.filterDate("" + q + "", "" + w + "").map(NDVI2).median()
        ndvimask_s = ndviim_s.clip(area_south).mask()
        #ndviim2_s_mask = ndviim_s.mask(ndvimask_s).gt(0.2)
        ndviim2_s = ndviim_s.mask(ndvimask_s)
        # NDVI_count = ndviim2_s_mask.count()
        # print("no. of pixels greater than 0.2 = ", NDVI_count)
        rgbim_s = collredim_s.select(['B4', 'B3', 'B2'])
        #NDVI_count = col.select('NDVI').map(function(img){return img.updateMask(img.select('NDVI').lt(0.25))}).count()


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
        #collredim_s2 = coll_south2.filterDate("" + q + "", "" + w + "").median()
       # ndviim_s2 = coll_south2.filterDate("" + q + "", "" + w + "").map(NDVI2).median()
        #ndvimask_s2 = ndviim_s2.clip(area_south).mask()
        #ndviim2_s2_mask = ndviim_s2.mask(ndvimask_s2).gt(0.2)     # mask for ndvi values greater than 0.2
        #ndviim2_s2 = ndviim_s2.mask(ndvimask_s2)
        #rgbim_s2 = collredim_s2.select(['B4', 'B3', 'B2'])

        #collredim_m = coll_malir.filterDate("" + q + "", "" + w + "").sort('CLOUDY_PIXEL_PERCENTAGE').first().clip(area_malir)  # for COPERNICUS/S2
        collredim_m = coll_malir.filterDate("" + q + "", "" + w + "").sort('IMAGE_QUALITY', True).first()
        ndviim_m = coll_malir.filterDate("" + q + "", "" + w + "").map(NDVI2).median()
        ndvimask_m = ndviim_m.clip(area_malir).mask()
        ndviim2_m = ndviim_m.mask(ndvimask_m)
        rgbim_m = collredim_m.select(['B4', 'B3', 'B2'])

        #collredim_k = coll_korangi.filterDate("" + q + "", "" + w + "").sort('CLOUDY_PIXEL_PERCENTAGE').first().clip(area_korangi)  # for COPERNICUS/S2
        collredim_k = coll_korangi.filterDate("" + q + "", "" + w + "").sort('IMAGE_QUALITY', True).first()
        ndviim_k = coll_korangi.filterDate("" + q + "", "" + w + "").map(NDVI2).median()
        ndvimask_k = ndviim_k.clip(area_korangi).mask()             # masked image of selected area
        ndviim2_k = ndviim_k.mask(ndvimask_k)                       # apply the mask
        rgbim_k = collredim_k.select(['B4', 'B3', 'B2'])

        #collredim_e = coll_east.filterDate("" + q + "", "" + w + "").sort('CLOUDY_PIXEL_PERCENTAGE').first().clip(area_east)  # for COPERNICUS/S2
        collredim_e = coll_east.filterDate("" + q + "", "" + w + "").sort('IMAGE_QUALITY', True).first()
        ndviim_e = coll_east.filterDate("" + q + "", "" + w + "").map(NDVI2).median()
        ndvimask_e = ndviim_e.clip(area_east).mask()
        ndviim2_e = ndviim_e.mask(ndvimask_e)
        rgbim_e = collredim_e.select(['B4', 'B3', 'B2'])

        #collredim_c = coll_central.filterDate("" + q + "", "" + w + "").sort('CLOUDY_PIXEL_PERCENTAGE').first().clip(area_central)  # for COPERNICUS/S2
        collredim_c = coll_central.filterDate("" + q + "", "" + w + "").sort('IMAGE_QUALITY', True).first()
        ndviim_c = coll_central.filterDate("" + q + "", "" + w + "").map(NDVI2).median()
        ndvimask_c = ndviim_c.clip(area_central).mask()
        ndviim2_c = ndviim_c.mask(ndvimask_c)
        rgbim_c = collredim_c.select(['B4', 'B3', 'B2'])

        #collredim_w = coll_west.filterDate("" + q + "", "" + w + "").sort('CLOUDY_PIXEL_PERCENTAGE').first().clip(area_west)  # for COPERNICUS/S2
        collredim_w = coll_west.filterDate("" + q + "", "" + w + "").sort('IMAGE_QUALITY', True).first()
        ndviim_w = coll_west.filterDate("" + q + "", "" + w + "").map(NDVI2).median()
        ndvimask_w = ndviim_w.clip(area_west).mask()
        ndviim2_w = ndviim_w.mask(ndvimask_w)
        rgbim_w = collredim_w.select(['B4', 'B3', 'B2'])

        filename = os.path.join(out_dir, '{}.tif'.format(a))
        filename2 = os.path.join(out_dir, 'ndvi{}.tif'.format(a))
        geemap.ee_export_image(rgbim, filename=filename, scale=sc1, region=area, file_per_band=False)
        # geemap.ee_export_image(rgbim, filename=filename, scale=sc1, region=area, file_per_band=True) # for rgb separate bands
        geemap.ee_export_image(ndviim2, filename=filename2, scale=sc1, region=area, file_per_band=False)

        filename = os.path.join(out_dir, 'south{}.tif'.format(a))
        filename2 = os.path.join(out_dir, 'ndvi_s{}.tif'.format(a))
        geemap.ee_export_image(rgbim_s, filename=filename, scale=scale_south, region=area_south, file_per_band=False)
        geemap.ee_export_image(ndviim2_s, filename=filename2, scale=scale_south, region=area_south, file_per_band=False)

        #filename = os.path.join(out_dir, 'south_ls{}.tif'.format(a))
        #filename2 = os.path.join(out_dir, 'ndvi_s_ls{}.tif'.format(a))
        #mask_im = os.path.join(out_dir, 'mask.tif')
        #geemap.ee_export_image(rgbim_s2, filename=filename, scale=scale_south2, region=area_south, file_per_band=False)
        #geemap.ee_export_image(ndviim2_s2, filename=filename2, scale=scale_south2, region=area_south, file_per_band=False)
        #geemap.ee_export_image(ndvimask_s2, filename=mask_im, scale=scale_south2, region=area_south, file_per_band=False)

        filename = os.path.join(out_dir, 'malir{}.tif'.format(a))
        filename2 = os.path.join(out_dir, 'ndvi_m{}.tif'.format(a))
        geemap.ee_export_image(rgbim_m, filename=filename, scale=scale_malir, region=area_malir, file_per_band=False)
        geemap.ee_export_image(ndviim2_m, filename=filename2, scale=scale_malir, region=area_malir, file_per_band=False)

        filename = os.path.join(out_dir, 'korangi{}.tif'.format(a))
        filename2 = os.path.join(out_dir, 'ndvi_k{}.tif'.format(a))
        geemap.ee_export_image(rgbim_k, filename=filename, scale=scale_korangi, region=area_korangi, file_per_band=False)
        geemap.ee_export_image(ndviim2_k, filename=filename2, scale=scale_korangi, region=area_korangi, file_per_band=False)

        filename = os.path.join(out_dir, 'east{}.tif'.format(a))
        filename2 = os.path.join(out_dir, 'ndvi_e{}.tif'.format(a))
        geemap.ee_export_image(rgbim_e, filename=filename, scale=scale_east, region=area_east, file_per_band=False)
        geemap.ee_export_image(ndviim2_e, filename=filename2, scale=scale_east, region=area_east, file_per_band=False)

        filename = os.path.join(out_dir, 'central{}.tif'.format(a))
        filename2 = os.path.join(out_dir, 'ndvi_c{}.tif'.format(a))
        geemap.ee_export_image(rgbim_c, filename=filename, scale=scale_central, region=area_central, file_per_band=False)
        geemap.ee_export_image(ndviim2_c, filename=filename2, scale=scale_central, region=area_central, file_per_band=False)

        filename = os.path.join(out_dir, 'west{}.tif'.format(a))
        filename2 = os.path.join(out_dir, 'ndvi_w{}.tif'.format(a))
        geemap.ee_export_image(rgbim_w, filename=filename, scale=scale_west, region=area_west, file_per_band=False)
        geemap.ee_export_image(ndviim2_w, filename=filename2, scale=scale_west, region=area_west, file_per_band=False)

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
    app.debug = True
    app.run()
