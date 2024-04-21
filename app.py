from flask import Flask, render_template, redirect, url_for, request, send_file, flash
from pymongo.mongo_client import MongoClient
from io import BytesIO
from datetime import date, timedelta

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

MIN_LON = 32.500
MIN_LAT = -124.200
MAX_LON = 42.000
MAX_LAT = -114.000

## REPLACE THIS WITH THE ACTUAL FILE PATH TO THE PRE-PROCESSED DATA ON THE SERVER
file_path = "data/"

## Generates the file to download ##
def createFile(data, file):
    file_data = bytearray('\n'.join(data) , "utf-8")
    return send_file(BytesIO(file_data), download_name = f"dataset.{file}", as_attachment = True)

## Converts a number sting into one with 3 decimal points ##
def formatValue(value):
    return round(float(value),3)

## Generates the header used for the file ##
def generateHeader(data_type, file_type):

    header = "Latitude | Longitude | "

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

    if (file_type == "txt"):
        return header[:-3]

    header = "Date," + header
    header = header.replace(" | ",",")
    header = header.replace("Enhanced Vegetation Index","EVI")
    header = header.replace("Themal Anomalies","TA")
    header = header.replace("Land Surface Temperature","LST")
    header = header.replace("Fire?","Fire")
    return header[:-1]

## Gets the data from the files based on the following parameters: ##
##
## Start_Date: The starting date
## End_Date: The ending date
## Header: A sting contatining the header of the data set
## Area: An array containing the lat and lon in this format: (Float/Double)
##       [min_Lat, max_Lat, min_Lon, max_Lon]
## Data_Type: An array containing the data types the user asked for (String)
## File_Type: A sting containg the file type the user asked for
##
## Returns an string array with the data the user asked for from the pre-prosessed data file(s).
def getData(Start_Date, End_Date, Header, Area, Data_Type, File_Type):

    ## Open the starting file
    file = open(file_path + str(Start_Date.year) + "data_Elevation.csv", 'r')
    line = file.readline()
    line = file.readline() # Skip Header

    Cur_Date = Start_Date
    return_list = []

    if (File_Type == "txt"):
        return_list.append(str(Cur_Date))
    
    return_list.append(Header)
    #input(Cur_Date)

    # TODO - Test this thing, see if it outputs the corect values
    # TODO - Split the source .csv files into days for more efficient performance.
    # TODO - Add an outer loop to switch files.
    while (Cur_Date <= End_Date) and (line != ''):
        line_check = [str(x) for x in line.split(",")]

        # Base line input
        if (File_Type == "txt"):
            line = f"{line_check[1]} | {line_check[2]} | "
        else:
            line = f"{line_check[0]},{line_check[1]},{line_check[2]},"

        # Updates the Cur_Date
        if (line_check[0] > str(Cur_Date)):
            Cur_Date += timedelta(days=1)

            if (Cur_Date > End_Date):
                break

            # Adds the next day for the .txt files
            if (File_Type == "txt"):
                return_list.append("")
                return_list.append(str(Cur_Date))
                return_list.append(Header)
                #input(Cur_Date)

        # Skips the line if the date on the file is less than the Cur_Date
        if (line_check[0] < str(Cur_Date)):
            line = file.readline()
            continue

        # Check the lat
        if (formatValue(line_check[1]) < Area[0]) or (formatValue(line_check[1]) > Area[1]):
            line = file.readline()
            continue

        # Check the lon
        if (formatValue(line_check[2]) < Area[2]) or (formatValue(line_check[2]) > Area[3]):
            line = file.readline()
            continue
        
        
        # Gets the needed data from the source .csv files
        if "EVI" in Data_Type:
            line += f"{line_check[3]}{" | " if File_Type == "txt" else ","}"
        if "TA" in Data_Type:
            line += f"{line_check[4]}{" | " if File_Type == "txt" else ","}"
        if "LST" in Data_Type:
            line += f"{line_check[5]}{" | " if File_Type == "txt" else ","}"
        if "Wind" in Data_Type:
            line += f"{line_check[6]}{" | " if File_Type == "txt" else ","}"
        if "Fire" in Data_Type:
            if File_Type == "txt":
                line += f"{"Yes" if bool(int(line_check[7])) else "No"} | "
            else:
                line += f"{line_check[7]},"
        if "Elevation" in Data_Type:
            line += f"{line_check[8]}{" | " if File_Type == "txt" else ","}"

        # Formats and adds the value to the return list.
        # (Removes last " | " or "," and '\n' at the end of the string)
        line = line[:-4] if File_Type == "txt" else line[:-2]
        #input(line)
        return_list.append(line)

        # Next line for next loop
        line = file.readline()
    
    file.close()
    return return_list

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

    file_type = request.args.get('filetype', default = "", type = str)

    ## IF ANY OF THE REQUIRED FIELDS ARE THE DEFAULT VALUES, JUST LOAD THE PAGE ##
    ## (Unless you clicked on the "Download Dataset" button, this should always be true) ##
    if (sd == "" or ed == "" or method == "" or len(data_type) == 0 or file_type == ""):
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
    date_range = (int)(temp[:(temp.find(" "))])
##    print(date_range > 20)
##    print("\n")

    # Date range checker (to prevent a large file from being generated)
    ## The limit is less then 3 weeks (less then 21 days) because if it is any higher,
    ## then the worst case senario is that a file could be over 0.5 GB in size, making
    ## it unopenable by the user, which is the whole point of the downloader. ##
    if (date_range > 20):
        flash("Date range is too large: must be less than 3 weeks (< 21 days)")
        print("Date range = " + temp[:(temp.find(" "))])
        return redirect(url_for('data_sources'))
    
    if (method == "LL"):

        # Input Validation for Latitude and Lonitude inputs
        try:
            if (min_Lat != ""): float(min_Lat)
            if (max_Lat != ""): float(max_Lat)
            if (min_Lon != ""): float(min_Lon)
            if (max_Lon != ""): float(min_Lon)
        except:
            flash("Invalid Laititude or Lottitute value entered: Please enter a number (decimal or whole) or leave blank.")
            return redirect(url_for('data_sources'))
        
        min_Lat = MIN_LAT if (min_Lat == "") else formatValue(min_Lat)
        max_Lat = MAX_LAT if (max_Lat == "") else formatValue(max_Lat)
        min_Lon = MIN_LON if (min_Lon == "") else formatValue(min_Lon)
        max_Lon = MAX_LON if (max_Lon == "") else formatValue(max_Lon)
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

##    print(file_type)

    ## END DATA VALIDATION, START FILE GENERATION ##

    # Generate header
    Header = generateHeader(data_type, file_type)
    print(Header)
    
    # Generate date
    for i in range(date_range + 1):
        Date = start_date + timedelta(i)
        print(Date)
        
    # Find values in lat and log and get the data type the user requested
    values = getData(start_date, end_date, Header,
                     [min_Lat, max_Lat, min_Lon, max_Lon],
                     data_type, file_type)

    
    # Flaten the array at the end of the file reader


    # PLACEHOLDER FOR FILE DOWNLOADER
    
    #flash("WIP")
    #return redirect(url_for('data_sources')) # Removes parameters from URL

    return createFile(values, file_type)

@app.route('/dbtest')
def db_test():

    year_param = request.args.get('year')

    # 1
    _1 = coll.find({"year": int(year_param)}, {"_id": 0})
    return(list(_1))

if __name__ == "__main__":
    app.run()
