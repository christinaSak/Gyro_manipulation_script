import pandas as pd
import csv 
import math

# Import data from CarMaker csv
# df=pd.read_csv('C:/Users/CSA8260/Desktop/Navsens work/recordings/Location course 2/first part/Location_course_2_first_part_carmaker_csv.csv', usecols = ['PosApp.IO.latitude','PosApp.IO.longitude','PosApp.IO.vx','PosApp.IO.vy','PosApp.IO.vz','PosApp.IO.h'])

# KML Solution
df=pd.read_csv('C:/Users/CSA8260/Desktop/Navsens work/recordings/AUTH/AUTH_carmaker_csv.csv', usecols = ['PosApp.IO.latitude','PosApp.IO.longitude','PosApp.IO.vx','PosApp.IO.vy','PosApp.IO.vz','PosApp.IO.h','Time'])

df_latitude = df['PosApp.IO.latitude']
df_longitude = df['PosApp.IO.longitude']
CarMakerTime = df['Time']
# Find speed and heding information from CarMaker csv
vx = df['PosApp.IO.vx']
vy = df['PosApp.IO.vy']
vz = df['PosApp.IO.vz']
heading = df['PosApp.IO.h']

# Calculate horizontal speed from vx and vy 
hSpeed = []
for p in range(0,len(vx)):
    hSpeed.append(math.sqrt((vx[p])**2+(vy[p])**2))
print('max hSpeed = ' + str(max(hSpeed)))

# Find the heading depending of the angle if it if [0,180] or [0,-180]
headingD = []
for r in range(0,len(heading)):
    headingD.append(math.degrees(heading[r]))
    if headingD[r] < 0 and headingD[r] > -180:
        headingD[r] = 360+headingD[r]

# Convert latitude and longitude to degrees
df_latitudeD = []
df_longitudeD = []
pi = 3.14159265
for radian in df_latitude:
    df_latitudeD.append(round(radian*(180/pi),7))

for radian2 in df_longitude:
    df_longitudeD.append(round(float(radian2)*(180/pi),7))

# Last CarMaker csv value
print('Last longitude ', df_longitudeD[len(df_longitudeD)-1])
print('Last latitude ', df_latitudeD[len(df_latitudeD)-1])

# Round in 5 decimal digits, we can increase that for more accurate results
df_latitudeDround = []
for lk in range(len(df_latitudeD)):
    df_latitudeDround.append(round(df_latitudeD[lk],5))
print('max ', max(df_latitudeDround))

timestamp = []
linesWithPos = []
counter = 0
synchronizeValue = 0
lineWithSynchronizeValue = 0
counterFindTheFirstNonZero = 0
timestampFindTheFirstNonZero = 0
with open('C:/Users/CSA8260/Desktop/Navsens work/recording/AUTH/navsens_record_o_AUTH.csv','r') as csvfile:
    csv_reader = csv.reader(csvfile, delimeter = ',')
    for row in csv_reader:
        counter = counter + 1
        if row[2] == '$GVGNPOS':
            timestamp.append(row[3])
    linesWithPos.append(counter)
    # Should also check if the first value is closed to real route because data logger sometimes saves the last remembered coordinate
    if float(row[4]) != 0 and float(row[4]) > 0 and float(row[5]) > 0 and counterFindTheFirstNonZero == 0:
        try:
            print('trying')
            synchronizeValue = float(row[4])
            lineWithSynchronizeValue = linesWithPos.index(counter)
            counterFindTheFirstNonZero = counter
            timestampFindTheFirstNonZero = row[3]
            # First line of CarMaker csv
            startingLineOfCarMakerCSV = df_latitudeDround.index(round(synchronizeValue,5))
        except ValueError:
            print('catched')
            counterFindTheFirstNonZero = 0
            pass
    print('synchronize Value '+ str(round(synchronizeValue,5)))
    print('starting line of CarMaker csv '+ str(startingLineOfCarMakerCSV))

    # After this value, we will consider the dt
    timestampNotZeroValues = timestamp.index(timestampFindTheFirstNonZero)
    # Find the dt of the GVGNPOS timestamps of navsens csv file
    dt = []
    sume = int()
    for f in range(len(timestamp)-1):
        dt.append(float(timestamp[f+1])-float(timestamp[f]))
        sume = sume + float(dt[f])

    print('Max dt time of GVGNPOS is ' + str(max(dt)))
    print('Min dt time of GVGNPOS is ' + str(min(dt)))
    print('Avg dt time of GVGNPOS is ' + str(sume/len(dt)))
    dt.append(0)

    # Open navsens csv, just copy the unused lines and replace in lines with GVGNPOS the latitude and longitude
    offset = 0
    coord1 = []
    coord2 = []
    with open('C:/Users/CSA8260/Desktop/Navsens work/recordings/AUTH/navsens_record_o_AUTH.csv','r') as csvfile:
        csv_reader2 = csv_reader(csvfile, delimeter = ';')
        #mylist = listy(csv_reader2)
        mylist = []
        for row in list(csv_reader2):
            listofrow = [x for x in list(row) if x !='']
            mylist.append(listofrow)
            # Uncomment this if you want to stop the manipulation at some point of the file
            # if len(mylist)) > 5000000:
            # break;
            for i in range(0,len(linesWithPos)-len(lineWithSynchronizeValue)):
                # First non zero value in navsens is in line lineWithSynchronizeValue
                mylist[linesWithPos[i+lineWithSynchronizeValue]-1][4] = df_latitudeD[startingLineOfCarMakerCSV + int(offset)]
                mylist[linesWithPos[i+lineWithSynchronizeValue]-1][5] = df_longitudeD[startingLineOfCarMakerCSV + int(offset)]
                # 8 is hSpeed
                mylist[linesWithPos[i+lineWithSynchronizeValue]-1][8] = hSpeed[startingLineOfCarMakerCSV + int(offset)]
                # 10 is heading in degrees
                mylist[linesWithPos[i+lineWithSynchronizeValue]-1][10] = headingD[startingLineOfCarMakerCSV + int(offset)]
                coord1.append(df_latitudeD[startingLineOfCarMakerCSV + int(offset)])
                coord2.append(df_longitudeD[startingLineOfCarMakerCSV + int(offset)])
                # Offset is the correction value to skip some lines of carmaker csv because of the changing sampling time in the navsens file
                offset = offset + dt[i+timestampNotZeroValues]
                # if offset + next_offset exceeds the carmaker time limits, break
                # print('offset ' + str(offset))
                if offset + dt[i+1+timestampNotZeroValues] > (len(df_latitudeD)-startingLineOfCarMakerCSV):
                    break

    ### 1st sync check
    # Check if dt array and for loop (loop to replace values) are sync 
    # 3 is the column of Timestamp in navsens 
    print('Last time value of navsens ' + str(mylist[linesWithPos[len(linesWithPos)-1]-1][3]))
    print('Before last time value of navsens ' + str(mylist[linesWithPos[len(linesWithPos)-2]-1][3]))
    last_time_value_navsens = mylist[linesWithPos[len(linesWithPos)-1]-1][3]
    before_last_time_value_nasvsens = mylist[linesWithPos[len(linesWithPos)-2]-1][3]
    dt_navsens_original = float(last_time_value_navsens) - float(before_last_time_value_nasvsens)
    # If the last dt values are the same, the for loop and dt array are sync
    if dt_navsens_original == dt[len(dt)-2]:
        print('First sync check is ok')


    ### 2nd sync check
    # Last carmaker time value - carmaker time in seconds, navsens time in ms
    # First carmaker time value from where is starts manipulating 
    print('Last carmaker time value ' + str(CarMakerTime[startingLineOfCarMakerCSV + int(offset)]))
    print('First carmaker time value ' + str(CarMakerTime[startingLineOfCarMakerCSV]))
    timingForManipulation = CarMakerTime[startingLineOfCarMakerCSV + int(offset)] - CarMakerTime[startingLineOfCarMakerCSV]
    print(timingForManipulation)
    first_time_value_navsens = mylist[linesWithPos[lineWithSynchronizeValue]-1][3] 
    print('Last time navsens ' + str(last_time_value_navsens))
    print('First time navsens ' + str(first_time_value_navsens))
    dt_navsens = float(last_time_value_navsens) - float(first_time_value_navsens)
    print(dt_navsens)
    if timingForManipulation*1000 == dt_navsens:
        print('Second sync check is ok')

    # Write the new list with manipulated navsens data in a new file
    with open('C:/Users/CSA8260/Desktop/Navsens work/recordings/AUTH/newFile.csv', 'w', newline='') as f:
        for line in mylist:
            write = csv.writer(f)
            write.writerow(line)
