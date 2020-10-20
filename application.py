from flask import Flask, render_template
import sqlite3

# Configure application
app = Flask(__name__)

@app.route('/')
def home():
    db = sqlite3.connect('database/motoresultstemp2.db')
    eventcount = db.execute("SELECT COUNT(DISTINCT EventID) FROM events").fetchone()[0]
    return render_template("index.html", eventcount=eventcount)

@app.route('/riders')
def riders():
    db = sqlite3.connect('database/motoresultstemp2.db')
    rows = db.execute("SELECT RiderName, RiderNumber, RiderID FROM RIDERLIST ORDER BY RiderName")
    riders = rows.fetchall()
    return render_template ("riders.html", riders=riders)

@app.route('/riders/<RiderID>')
def riderdetails(RiderID):
    db = sqlite3.connect('database/motoresultstemp2.db')
    rows = db.execute("SELECT EventName, SessionName, Position, \
        Status, LapsCompleted, RiderName FROM RACERESULTSVIEW WHERE RiderID=:RiderID \
        ORDER BY EventID", {"RiderID":RiderID})
    RiderDetails = rows.fetchall()    
    return render_template("riderdetails.html", RiderDetails=RiderDetails)     

@app.route('/events')
def events():
    db = sqlite3.connect('database/motoresultstemp2.db')
    rows = db.execute("SELECT * FROM events")
    events = rows.fetchall()
    return render_template ("events.html", events=events)


@app.route('/events/<EventID>')
def eventdetails(EventID):
    db = sqlite3.connect('database/motoresultstemp2.db')
    rows = db.execute("SELECT DISTINCT SessionName, SessionNumber \
        FROM sessions WHERE EventID=:EventID AND HeaderA IN (2,3) \
        AND SessionNumber > 0", {"EventID":EventID})
    EventDetails = rows.fetchall()    
    return render_template("eventdetails.html", EventDetails=EventDetails, EventID=EventID)


@app.route('/events/<EventID>/<SessionNumber>')
def sessiondetails(EventID, SessionNumber):
    db = sqlite3.connect('database/motoresultstemp2.db')
    rows = db.execute("SELECT DISTINCT Position, RiderName, BestLapTime FROM RESULTSVIEW \
        WHERE EventID=? AND SessionNumber=? ORDER BY Position", [EventID, SessionNumber])
    SessionDetails = rows.fetchall()    
    return render_template("sessiondetails.html", SessionDetails=SessionDetails)


         