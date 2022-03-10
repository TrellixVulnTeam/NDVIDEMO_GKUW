# This is Tom's sandpit where he hopes to make some shit happen or die trying.

import os

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt, make_path_filter
from IPython.display import display
from datetime import date, datetime
import cv2
# from tkinter import *
from tkinter.filedialog import askopenfilename
# from tkcalendar import Calendar, DateEntry


user = 'group29'
password = 'COMP3850'
api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')
cols = [0, 4]
titles = []
redPath = ""
nirPath = ""

def findProducts():
    products = []
    for i in range(0, length):
        print(str(i) + ": ")
        # shows found products from sentinel with title and date.
        display(images_df[images_df.columns[cols]].iloc[i])
        titles.append(images_df[images_df.columns[0]].iloc[i])
        #builds selection list from UUIDs of located images to correspond to show titles
        products.append(str(images_df.uuid.iloc[i]))
    return products

def selectProduct():
    while True:
            selected = int(input("Select Product for Download and Conversion: "))
            if selected >= length:
                print("Enter Valid Product: ")
                continue
            else:
                return selected

def selectRes():
    while True:
        res = int(input("Select Resolution level for processing: \n1 -> 10m \n2 -> 20m \n3 -> 60m \n"))
        if int(res) not in range(1, 4):
            print("Enter Valid Resolution: ")
            continue
        else:
            if res == 1:
                return "10m"
            if res == 2:
                return "20m"
            if res == 3:
                return "60m"


def createNDVI(redIm, nirIm):
    ndvi = ((nirIm - redIm) / (nirIm + redIm + 0.001))
    print("NDVI Channels is: " + str(ndvi.shape[2]))
    print("TESTING: " + str(ndvi[0, 0]))
    w = ndvi.shape[1]
    h = ndvi.shape[0]

    # ndviprep = cv2.cvtColor(ndviconv, cv2.COLOR_BGR2GRAY) absolutely could not get it to behave but fixing this will likely speed the whole thing up
    ndvicoloured = ndvi
    for i in range(h):
        for j in range(w):
            if (ndvi[i][j][0] >= -1 and ndvi[i][j][0] < 0):
                ndvicoloured[i][j] = [128, 128, 128]  # grey
            elif (ndvi[i][j][0] >= 0 and ndvi[i][j][0] < 0.2):
                ndvicoloured[i][j] = [64, 255, 0]  # parrot green
            elif (ndvi[i][j][0] >= 0.2 and ndvi[i][j][0] < 0.3):
                ndvicoloured[i][j] = [125, 255, 255]  # yellow
            elif (ndvi[i][j][0] >= 0.3 and ndvi[i][j][0] < 0.4):
                ndvicoloured[i][j] = [0, 128, 128]  # dark green
            elif (ndvi[i][j][0] >= 0.4 and ndvi[i][j][0] < 0.5):
                ndvicoloured[i][j] = [255, 255, 0]  # sky blue
            elif (ndvi[i][j][0] >= 0.5 and ndvi[i][j][0] < 0.6):
                ndvicoloured[i][j] = [255, 51, 153]  # purple
            elif (ndvi[i][j][0] >= 0.6 and ndvi[i][j][0] < 0.7):
                ndvicoloured[i][j] = [0, 128, 255]  # orange
            elif (ndvi[i][j][0] >= 0.7 and ndvi[i][j][0] < 0.8):
                ndvicoloured[i][j] = [255, 43, 255]  # pink
            elif (ndvi[i][j][0] >= 0.8 and ndvi[i][j][0] < 0.9):
                ndvicoloured[i][j] = [40, 40, 255]  # red
            else:
                ndvicoloured[i][j] = [255, 0, 0]  # dark blue
    return ndvicoloured

def getDate():
    while True:
        try:
            date1 = str(input("Choose start date (Format: dd-mm-yyyy) : "))
            dateStart = datetime.strptime(date1, '%d-%m-%Y')
        except:
            print("Invalid Date")
            continue
        try:
            date2 = str(input("Choose end date (Format: dd-mm-yyyy) : "))
            dateEnd = datetime.strptime(date2, '%d-%m-%Y')
        except:
            print("Invalid Date")
            continue

        return dateStart, dateEnd

#GUI I couldnt be bothered fiddling with anymore
# def runDateDialog():
#     # Create an instance of tkinter frame
#     win = Tk()
#     # Set the Geometry
#     win.geometry("320x150")
#     win.title("Date Picker")
#     # Create a Label
#     Label(win, text="Choose a Date", background='gray61', foreground="white").grid(row=0, column=2)
#     # Create a Calendar using DateEntry
#     Label(win, text="Start Date", background='gray61', foreground="white").grid(row=1, column=1)
#     startDate = DateEntry(win, width=16, background="magenta3", foreground="white", bd=2).grid(row=2, column=1)
#     Label(win, text="End Date", background='gray61', foreground="white").grid(row=1, column=3)
#     endDate = DateEntry(win, width=16, background="magenta3", foreground="white", bd=2).grid(row=2, column=3)
#     button
#     dates = startDate, endDate
#     win.mainloop()
#     return dates


print("Pick JSON file for Sentinel to reference!!!")
filename = str(askopenfilename())
date = getDate()
area = geojson_to_wkt(read_geojson(filename))
cloudCover = str(input("Enter maximum acceptable cloud cover percentage (0-100): "))
images = api.query(
    area,
    date=date,
#date=(date(2022, 1, 1), date(2022, 6, 1)),
    platformname="Sentinel-2",
    processinglevel="Level-2A",
    cloudcoverpercentage=(0, cloudCover),
)
images_df = api.to_dataframe(images)
length = len(images_df)
print("Working in: " + os.getcwd())
products = findProducts()
selected = selectProduct()
res = selectRes()
path_filter = make_path_filter("*B*[48]*" + res + ".jp2") #filering to just downloading files needed for NDVI creation.

#retrieving files from Sentinel Server
api.download(products[selected], nodefilter=path_filter)

#finding downloaded files
if res == "10m":
    for dirpath, subdirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith("4_10m.jp2"):
                redPath = str(os.path.join(dirpath, file))
            if file.endswith("8_10m.jp2"):
                nirPath = str(os.path.join(dirpath, file))

else:
    for dirpath, subdirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith("4_" + res + ".jp2"):
                redPath = str(os.path.join(dirpath, file))
            if file.endswith("8A_" + res + ".jp2"):
                nirPath = str(os.path.join(dirpath, file))
#For debugging
# print("Path to Red Band: " + redPath)
# print("Path to NIR Band: " + nirPath)

redIm = cv2.imread(redPath).astype(float)
nirIm = cv2.imread(nirPath).astype(float)

output = createNDVI(redIm, nirIm)
today = date.today()
cv2.imwrite('OUT' + titles[selected] + today.strftime("%d/%m/%Y") +'.jp2', output)
