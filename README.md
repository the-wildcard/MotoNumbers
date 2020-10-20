# MotoNumbers
MotoNumbers is an application for collecting and viewing data for AMA Motocross and Supercross events

## Components
There are 3 primary components to this application.
- Python scripts for populating the results database
- SQLite Results Database
- Flask/Python web application for viewing results

### Database population
This app collects data from the AMA live timing JSON feeds at:
http://americanmotocrosslive.com/xml/mx/racelaptimes.json
http://americanmotocrosslive.com/xml/mx/raceresults.json
to populate the results database during live events. There is also a script for downloading information from these locations (as a backup)
during races. Data from these feeds is captured using the **requests** module, parsed using the **json** module and written to the database
using **sqlite3**.

### Flask
The flask app for this project has 6 routes, 4 of which use dynamic urls.

### Database Schema
Database tables:
    CREATE TABLE IF NOT EXISTS "riders" (
            "id"    INTEGER,
            "RiderID"       INTEGER,
            "RiderName"     TEXT,
            "RiderNumber"   TEXT,
            "Class" TEXT,
            "Bike"  TEXT,
            "Team"  INTEGER,
            "Hometown"      TEXT,
            "EventID"       INTEGER,
            PRIMARY KEY("id" AUTOINCREMENT)
    );
    CREATE TABLE IF NOT EXISTS "events" (
            "id"    INTEGER,
            "EventID"       TEXT,
            "EventName"     TEXT,
            "Track" INTEGER,
            PRIMARY KEY("id" AUTOINCREMENT)
    );
    CREATE TABLE IF NOT EXISTS "positions" (
            "id"    INTEGER,
            "EventID"       TEXT,
            "SessionNumber" INTEGER,
            "RiderID"       INTEGER,
            "RiderName"     TEXT,
            "Position"      INTEGER,
            "LapsCompleted" INTEGER,
            "LastLapTime"   TEXT,
            "BestLapTime"   TEXT,
            "BestLapLap"    INTEGER,
            "TimeDown"      TEXT,
            "Gap"   TEXT,
            "Status"        TEXT,
            "TimeDay"       TEXT,
            PRIMARY KEY("id" AUTOINCREMENT)
    );
    CREATE TABLE IF NOT EXISTS "laps" (
            "id"    INTEGER,
            "SessionNumber" INTEGER,
            "RiderNumber"   TEXT,
            "LapNumber"     INTEGER,
            "LapTime"       TEXT,
            "LapTimeSec"    REAL,
            "Position"      INTEGER,
            "EventID"       TEXT,
            PRIMARY KEY("id" AUTOINCREMENT)
    );
    CREATE VIEW LAPVIEW
    AS
    SELECT * FROM laps JOIN riders ON laps.RiderNumber = riders.RiderNumber
    ORDER BY SessionNumber, RiderNumber, LapNumber
    /* LAPVIEW(id,SessionNumber,RiderNumber,LapNumber,LapTime,LapTimeSec,Position,EventID,"id:1",RiderID,RiderName,"RiderNumber:1",Class,Bike,Team,Hometown,"EventID:1") */;
    CREATE TABLE IF NOT EXISTS "sessions" (
            "id"    INTEGER,
            "HeaderA"       INTEGER,
            "SessionNumber" INTEGER,
            "SessionName"   TEXT,
            "EventID"       INTEGER,
            "DayTime"       TEXT,
            PRIMARY KEY("id" AUTOINCREMENT)
    );

    CREATE VIEW PRACTICERESULTSVIEW
    AS
    SELECT DISTINCT events.EventName,  sessions.SessionName, positions.Position, positions.RiderName, positions.TimeDay, positions.Status, positions.BestLapTime, riders.Class
    FROM positions JOIN sessions ON positions.SessionNumber = sessions.SessionNumber AND positions.EventID = sessions.EventID
                    JOIN events ON positions.EventID=events.EventID JOIN riders ON positions.RiderID = riders.RiderID
    WHERE positions.TimeDay IN
            (SELECT MAX(sessions.DayTime) FROM sessions GROUP BY SessionNumber)  /* Finds the max time for each session */
            AND sessions.HeaderA = 2
    ORDER BY riders.Class, positions.BestLapTime, sessions.SessionNumber, positions.Position
    /* PRACTICERESULTSVIEW(EventName,SessionName,Position,RiderName,TimeDay,Status,BestLapTime,Class) */;
    CREATE VIEW RACE_POSITIONS_BY_LAP
    AS
    SELECT DISTINCT events.EventName,  sessions.SessionName, positions.LapsCompleted, positions.Position, positions.RiderName, positions.Status, riders.Class
    FROM positions JOIN sessions ON positions.SessionNumber = sessions.SessionNumber AND positions.EventID = sessions.EventID
                    JOIN events ON positions.EventID=events.EventID JOIN riders ON positions.RiderID = riders.RiderID
    WHERE sessions.HeaderA = 3
    ORDER BY sessions.SessionNumber, riders.RiderID, positions.LapsCompleted
    /* RACE_POSITIONS_BY_LAP(EventName,SessionName,LapsCompleted,Position,RiderName,Status,Class) */;
    CREATE VIEW RIDERLIST
    AS
    SELECT DISTINCT RiderName, RiderNumber, RiderID FROM riders
    /* RIDERLIST(RiderName,RiderNumber,RiderID) */;

    CREATE VIEW RACERESULTSVIEW
    AS
    SELECT DISTINCT events.EventID, events.EventName,  sessions.SessionName, positions.Position, positions.RiderName, positions.TimeDay, positions.Status,positions.LapsCompleted, riders.Class, riders.RiderID
    FROM positions JOIN sessions ON positions.SessionNumber = sessions.SessionNumber AND positions.EventID = sessions.EventID
                    JOIN events ON positions.EventID=events.EventID JOIN riders ON positions.RiderID = riders.RiderID
    WHERE positions.TimeDay IN
            (SELECT MAX(sessions.DayTime) FROM sessions GROUP BY EventID, SessionNumber)  /* Finds the max time for each session */
            AND sessions.HeaderA = 3
    ORDER BY sessions.SessionNumber, positions.TimeDay, positions.Position
    /* RACERESULTSVIEW(EventID,EventName,SessionName,Position,RiderName,TimeDay,Status,LapsCompleted,Class,RiderID) */;
    CREATE VIEW RESULTSVIEW
    AS
    SELECT DISTINCT events.EventID, events.EventName, sessions.SessionNumber, sessions.SessionName, positions.Position, positions.RiderName, positions.TimeDay, positions.Status,positions.LapsCompleted, riders.Class, riders.RiderID
    FROM positions JOIN sessions ON positions.SessionNumber = sessions.SessionNumber AND positions.EventID = sessions.EventID
                    JOIN events ON positions.EventID=events.EventID JOIN riders ON positions.RiderID = riders.RiderID
    WHERE positions.TimeDay IN
            (SELECT MAX(sessions.DayTime) FROM sessions GROUP BY EventID, SessionNumber)  /* Finds the max time for each session */
    ORDER BY sessions.SessionNumber, positions.TimeDay, positions.Position
    /* RESULTSVIEW(EventID,EventName,SessionNumber,SessionName,Position,RiderName,TimeDay,Status,LapsCompleted,Class,RiderID) */;