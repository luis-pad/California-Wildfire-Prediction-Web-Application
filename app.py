from flask import Flask, render_template, redirect, url_for, request, send_file, flash
from pymongo.mongo_client import MongoClient
from io import BytesIO
from datetime import date

# LIST OF STRINGS FILLED WITH CALIFORNA COUNTY NAMES
# Format: <BLANK>,<COUNTY NAME>,...
CountyList = ["","Alameda",
              "","Alpine",
              "","Amador",
              "","Butte",
              "","Calaveras",
              "","Colusa",
              "","Contra Costa",
              "","Del Norte",
              "","El Dorado",
              "","Fersno",
              "","Glenn",
              "","Humboldt",
              "","Imperial",
              "","Inyo",
              "","Kern",
              "","Kings",
              "","Lake",
              "","Lassen",
              "","Los Angeles",
              "","Madera",
              "","Marin",
              "","Mariposa",
              "","Mendocino",
              "","Merced",
              "","Modoc",
              "","Mono",
              "","Monterey",
              "","Napa",
              "","Nevada",
              "","Orange",
              "","Placer",
              "","Plumas",
              "","Riverside",
              "","Sacramento",
              "","San Benito",
              "","San Bernardino",
              "","San Diego",
              "","San Francisco",
              "","San Joaquin",
              "","San Luis Obispo",
              "","San Mateo",
              "","Santa Barbara",
              "","Santa Clara",
              "","Santa Cruz",
              "","Shasta",
              "","Sierra",
              "","Siskiyou",
              "","Solano",
              "","Sonama",
              "","Stanislaus",
              "","Sutter",
              "","Tehama",
              "","Trinity",
              "","Tulare",
              "","Tuolume",
              "","Ventura",
              "","Yolo",
              "","Yuba"
              ]


## PLACEHOLDERS (Check with the dataset to find the actual values)
MIN_LON = "0"
MIN_LAT = "0"
MAX_LON = "200"
MAX_LAT = "200"

## Generates the file to download ##
def createFile(data):
    file_data = bytearray('\n'.join(data) , "utf-8")
    return send_file(BytesIO(file_data), download_name = "dataset.txt", as_attachment = True)

def generateHeader(data_type):
    header = ""

    if "EVI" in data_type:
        header += "Enhanced Vegetation Index | "
    if "TA" in data_type:
        header += "Themal Anomalies | "
    if "LST" in data_type:
        header += "Land Surface Temperature | "
    if "Wind" in data_type:
        header += "Wind | "
    if "Fire" in data_type:
        header += "Fire? | "
    if "Elevation" in data_type:
        header += "Elevation | "

    return header[:-3]

## Finds and returns a value from file 'filePath' from day 'date' and county 'county' ##
## Returns an empty array if it can't find a value ##
def findValue(start_date, end_date, county, filePath):
    file = open(filePath, 'r')
    line = file.readline()
    line = file.readline() # Skip Header
    matches = []

    if (end_date == ""): # Only Start Date
        end_date = start_date

    while (line != ''):
        line_check = [str(x) for x in line.split(",")]
        if ((start_date <= date.fromisoformat(toISO(line_check[0])) <= end_date)
        and (county in line)):
            matches.append(line_check)
        line = file.readline()

    file.close()

    if matches == []:
        return []

    for i in matches:
        i[0] = date.fromisoformat(toISO(i[0]))
        
    ret_list = []
    for i in matches:
        # <County>  |  <Date>  |  <Value>
        ap_str = i[3][:-1] + "  |  " + str(i[0]) + "  |  " + i[1]
        ret_list.append(ap_str)

    ret_list.sort()
    ret_list.append("")
    
    return ret_list

## Converts the county id into a string ##
def formatCounty(county):
    try:
        return "," + f"{county:03d}"+ "," + CountyList[county] + "\n"
    except:         # Out of range index
        return ""
        
## Converts the date from mm/dd/yyyy to yyyy-mm-dd ##
def toISO(date):
    m, d, y = [str(x) for x in date.split('/')]
    return y + "-" + m + "-" + d

app = Flask(__name__)
app.secret_key = b'z19D]p3Q4]rjhx[qcBHSf-Rx@K@9W*' # Needed for flash()

client = MongoClient('localhost', 27017)
db = client["cwp_prod"]
coll = db.main

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

## STILL NEED THIS FOR REFERENCE, WILL REMOVE WHEN FILE DOWNLOADER IS DONE.
"""
@app.route('/data')
def data():
    sd = request.args.get('start_date', default = "", type = str)
    ed = request.args.get('end_date', default = "", type = str)
    county = request.args.getlist('county', type = int)
    print(sd)       # DEBUG
    print(ed)       # DEBUG
    print(county)   # DEBUG

    if (len(county) == 0 or sd == ""): # NO DATA ENTERED
        return render_template('data.html')
    
    try:
        start_date = date.fromisoformat(sd)
        end_date = date.fromisoformat(ed) if (not ed == "") else ""
    except: ## INVALID DATE ENTRY
        print("Invalid date entry!")
        flash("ERROR: Invalid date entry!")
        return redirect(url_for('data'))

    if (start_date > end_date):
        print("End date is larger than start date")
        flash("ERROR: End date is larger than start date")
        return redirect(url_for('data'))

    print(start_date)     # DEBUG date : <year>-<month>-<day>
    print(end_date)
    
    value_NDVI = []
    value_NDVI.append(["<County>  |  <Date>  |  <NDVI>", ""])
        
    for i in county:
        find_county = formatCounty(i)
        print(find_county)                  # DEBUG

        value_NDVI.append(
            findValue(start_date, end_date, find_county, "Data Processing/output/NDVI_result.csv")
        )

    value_NDVI = sum(value_NDVI, []) # Flatens the list
    
    for i in value_NDVI: # DEBUG, OUTPUT
        print(i)
    
    return createFile(value_NDVI)"""

@app.route('/models')
def models():
    return render_template('models.html')

@app.route('/data_sources')
def data_sources():

    # Gets parameters from the url from the form entry (if avalible)    
    sd = request.args.get('start_date', default = "", type = str)
    ed = request.args.get('end_date', default = "", type = str)
    method = request.args.get('m_type', default = "", type = str)

    # TODO: Replace the defaults with whatever the min and max values are from the dataset
    min_Lat = request.args.get('minLat', default = "", type = str)
    max_Lat = request.args.get('maxLat', default = "", type = str)
    min_Lon = request.args.get('minLon', default = "", type = str)
    max_Lon = request.args.get('maxLon', default = "", type = str)

    county = request.args.get('county', default = -1, type = int)

    data_type = request.args.getlist('type', type = str)

    ## IF ANY OF THE REQUIRED FIELDS ARE THE DEFAULT VALUES, JUST LOAD THE PAGE ##
    ## (Unless you clicked on the "Download Dataset" button, this should always be true) ##
    if (sd == "" or ed == "" or method == "" or len(data_type) == 0):
        return render_template('data_sources.html')

    ## START DATA VALIDATION ##
    start_date = date.fromisoformat(sd)
    end_date = date.fromisoformat(ed)

    if (start_date > end_date):
        start_date, end_date = end_date, start_date

    #DEBUG <year-month-date>
##    print(start_date)
##    print(end_date)
##    print("\n")

    temp = (str)(end_date - start_date)
##    print((int)(temp[:(temp.find(" "))]) > 20)
##    print("\n")

    # Date range checker (to prevent a large file from being generated)
    ## The limit is less then 3 weeks (less then 21 days) because if it is any higher,
    ## then the worst case senario is that a file could be over 0.5 GB in size, making
    ## it unopenable by the user, which is the whole point of the downloader. ##
    if ((int)(temp[:(temp.find(" "))]) > 20):
        flash("Date range is too large: must be less than 3 weeks (< 21 days)")
        print("Date range = " + temp[:(temp.find(" "))])
        return redirect(url_for('data_sources'))
    
    if (method == "LL"):
        min_Lat = MIN_LAT if (min_Lat == "") else min_Lat
        max_Lat = MAX_LAT if (max_Lat == "") else max_Lat
        min_Lon = MIN_LON if (min_Lon == "") else min_Lon
        max_Lon = MAX_LON if (max_Lon == "") else max_Lon
    else: # method == "county"
        min_Lat = MIN_LAT if (county == -1) else min_Lat #lat[county]
        max_Lat = MAX_LAT if (county == -1) else max_Lat #lat[county+1]
        min_Lon = MIN_LON if (county == -1) else min_Lon #lon[county]
        max_Lon = MAX_LON if (county == -1) else max_Lon #lon[county+1]

    if (min_Lat > max_Lat):
        min_Lat, max_Lat = max_Lat, min_Lat
    if (min_Lon > max_Lon):
        min_Lon, max_Lon = max_Lon, min_Lon

    #DEBUG
##    print(min_Lat)
##    print(max_Lat)
##    print("\n")
##    print(min_Lon)
##    print(max_Lon)

    ## END DATA VALIDATION, START FILE GENERATION ##

    # Generate header
    print(generateHeader(data_type))
    # Generate date
    # Find values in lat and log and get the data type the user requested
    # Flaten the array at the end of the

    # PLACEHOLDER FOR FILE DOWNLOADER
    flash("WIP")
    return redirect(url_for('data_sources')) # Removes parameters from URL

@app.route('/dbtest')
def db_test():

    year_param = request.args.get('year')

    # 1
    _1 = coll.find({"year": int(year_param)}, {"_id": 0})
    return(list(_1))

if __name__ == "__main__":
    app.run()
