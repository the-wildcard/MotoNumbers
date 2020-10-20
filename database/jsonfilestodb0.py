'''
Script to write data from AMA live timing jsons to SQLite db
TODO- bundle db writes as a transaction, convert DT to 24 hr time
'''
import json
import sqlite3
import requests
import datetime
import re
import os

def main():
    # Open database
    database = sqlite3.connect(r"C:\Users\orlow\Google Drive\Computing\CS50 Final\python\database\motoresultstemp2.db")
    filelist = os.listdir()
    
    # Get event ID
    EventID = "M2040" #re.findall(r'M[\d{4}]+', str(requests.get('http://americanmotocrosslive.com/xml/mx/racefiles.json').content))[0]

    # Call functions to write to db depending on url
    for afile in filelist:
        if 'racelaptimes.json' in str(afile):
            json_lap_file_to_db(afile, database, EventID)
        if 'raceresults.json' in str(afile):
            json_results_file_to_db(afile, database, EventID)

    # Close database
    database.close()


def json_lap_file_to_db(infile, database, EventID):
    # Open lap times json and load to contents
    with open(infile) as input: 
        contents = json.load(input)

    # Get list of lap times in database for comparison
    rows = database.execute("SELECT EventID, SessionNumber, RiderNumber, LapNumber, LapTimeSec, Position FROM laps")
    lapList = rows.fetchall()

    # Iterate through riders and laps for each rider
    for rider in range(len(contents['B'])):
        for lap in range(len(contents['B'][rider]['C'])):
            row = contents['B'][rider]['C'][lap]
            
            # Convert lap times to seconds
            try:
                lapseconds = float(row['D'].split(':')[0])*60 + float(row['D'].split(':')[1])
            except:
                lapseconds = None    
            
            # Check for null lap times, or duplicate records. If not, write to db.           
            if lapseconds == None: print('Skipped null laptime')
            elif (EventID, contents['A'], contents['B'][rider]['A'], row['A'], lapseconds, row['P']) in lapList: print('Skipped duplicate laps')
            else:
                database.execute("INSERT INTO laps (SessionNumber, RiderNumber, LapNumber, LapTime, LapTimeSec, Position, EventID) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                    [contents['A'], contents['B'][rider]['A'], row['A'], row['D'], lapseconds, row['P'], EventID])
                print('Wrote session ' + str(contents['A']) + ' lap details')
   
    # Save database
    database.commit()

def json_results_file_to_db(infile, database, EventID):
    # Open results json and load to contents
    with open(infile) as input: 
        contents = json.load(input)

    # Write event to events table if not there
    rows = database.execute("SELECT * FROM events WHERE EventID=? AND EventName=?", (EventID, contents['E']))
    if len(rows.fetchall()) == 0:
        database.execute("INSERT INTO events (EventID, EventName, Track) VALUES (?, ?, ?)", [EventID, contents['E'], contents['T']])
        print('Event details added')

    # Write rider details to riders table and positions to unofficial results. Checks to see if riders are already in table and skips if so. Positions checks to see if records exist for current time and skips if so
    rows = database.execute("SELECT EventID, RiderID FROM riders")
    riderList = rows.fetchall()
    rows = database.execute("SELECT EventID, RiderID, TimeDay FROM positions")
    positionList = rows.fetchall()

    try:
        for rider in range(len(contents['B'])):
            row = contents['B'][rider]
            riderTest = (EventID, row['I'])
            
            # Check to see if rider is in riderlist for current event, add to list if not
            if riderTest in riderList: pass
            else: # Write riders
                database.execute("INSERT INTO riders (EventID, RiderID, RiderName, RiderNumber, Class, Bike, Team, Hometown) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                    [EventID, row['I'], row['F'], row['N'], row['C'], row['V'], row['T'], row['H']])
                print('Added ' + row['F'] + 'to riders table')
                
            # Check to see if a record for current time exists. If not, write positions        
            positionTest = (EventID, row['I'], time_to_24(contents['DT']))
            if positionTest in positionList: pass
            else:
                database.execute("INSERT INTO positions (EventID, SessionNumber, RiderID, RiderName, Position, LapsCompleted, LastLapTime, \
                    BestLapTime, BestLapLap, TimeDown, Gap, Status, TimeDay) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [EventID, contents['R'],  row['I'], row['F'], row['A'], row['L'], row['LL'], row['BL'], row['IN'], row['D'], row['G'], row['S'], time_to_24(contents['DT'])])
    
    except KeyError: pass

    # Write session details to sessions table
    database.execute("INSERT INTO sessions (EventID, HeaderA, SessionNumber, SessionName, DayTime) VALUES (?, ?, ?, ?, ?)",
        [EventID, contents['A'], contents['R'], contents['S'], time_to_24(contents['DT'])])

    database.commit()
    print('Wrote results details at ' + str(datetime.datetime.now()))

def time_to_24(timein):
    # Convert time in results file to 24 hr format
    if timein.find('AM') > 0:
        timeout = timein.split(' ')
        timeout = timeout[0]
        timeout = timeout.split(':')
        if int(timeout[0]) == 12:
            timeout[0] = '00'
        if int(timeout[0]) < 10:
            timeout[0] = str(0) + timeout[0]
        timeout = ':'.join(map(str,timeout))
        return timeout
    elif timein.find('PM') > 0:
        timeout = timein.split(' ')
        timeout = timeout[0]
        timeout = timeout.split(':')
        if int(timeout[0]) != 12:
            timeout[0] = int(timeout[0]) + 12
        timeout = ':'.join(map(str,timeout))
        return timeout
    else: 
        return timein


main()