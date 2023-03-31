import sqlite3, config, binbun
from flask import Flask, render_template, request, url_for, redirect, flash
from flaskwebgui import FlaskUI # import FlaskUI
from binbun import routes

app = Flask(__name__)
app.secret_key = config.APP_SECRET
app.register_blueprint(routes)

# Classes
class Points:
    def __init__(self,RSI_out_of_Red,MACD_Histo_rising,MACD_Torys_Trendzone_red,Heikin_Ashi_confirmed,Support_price_level,EMA_support,No_EMA_Resistance,Higher_Low,Higher_High):
        self.arg1 = RSI_out_of_Red
        self.arg2 = MACD_Histo_rising
        self.arg3 = MACD_Torys_Trendzone_red
        self.arg4 = Heikin_Ashi_confirmed
        self.arg5 = Support_price_level
        self.arg6 = EMA_support
        self.arg7 = No_EMA_Resistance
        self.arg8 = Higher_Low
        self.arg9 = Higher_High
    def points(self):
        pts = 0
        if self.arg1 == "YES":
            pts = pts+1
        elif self.arg1 == "half":
            pts = pts+0.5
            
        if self.arg2 == "YES":
            pts = pts+1
        elif self.arg2 == "half":
            pts = pts+0.5
            
        if self.arg3 == "YES":
            pts = pts+1
        elif self.arg3 == "half":
            pts = pts+0.5
        
        if self.arg4 == "YES":
            pts = pts+1
        elif self.arg4 == "half":
            pts = pts+0.5
            
        if self.arg5 == "YES":
            pts = pts+1
        elif self.arg5 == "half":
            pts = pts+0.5
        
        if self.arg6 == "YES":
            pts = pts+1
        elif self.arg6 == "half":
            pts = pts+0.5
        
        if self.arg7 == "YES":
            pts = pts+1
        elif self.arg7 == "half":
            pts = pts+0.5
            
        if self.arg8 == "YES":
            pts = pts+1
        elif self.arg8 == "half":
            pts = pts+0.5
        
        if self.arg9 == "YES":
            pts = pts+1
        elif self.arg9 == "half":
            pts = pts+0.5
        return pts

## Defs
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def db_entry(tf,arg1,arg2,arg3,arg4,arg5,arg6,arg7,pts):
    conn = get_db_connection()
    conn.execute(f'INSERT INTO {tf} (arg1,arg2,arg3,arg4,arg5,arg6,arg7,pts) VALUES (?,?,?,?,?,?,?,?)',(arg1,arg2,arg3,arg4,arg5,arg6,arg7,pts))
    conn.commit()
    conn.close()

@app.route("/updatechecklist", methods=['POST'])
def updatechecklist():
    print("Updatechecklist route:")
    tf = request.form['tf']
    print("Timeframe", tf, 'saved.')
    arg1 = request.form['arg1']
    arg2 = request.form['arg2']
    arg3 = request.form['arg3']
    arg4 = request.form['arg4']
    arg5 = request.form['arg5']
    arg6 = request.form['arg6']
    arg7 = request.form['arg7']
    arg8 = request.form['arg8']
    arg9 = request.form['arg9']
    pts = Points(arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9).points()  
    percent = round(pts/0.09, 0)
    conn = get_db_connection()
    conn.execute('UPDATE Checklist SET arg1 = ?, arg2 = ?, arg3 = ?, arg4 = ?, arg5 = ?, arg6 = ?, arg7 = ?, arg8 = ?, arg9 = ?, pts = ?, percent = ?'
                         ' WHERE tf = ?',
                         (arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, pts, percent, tf))
    conn.commit()
    conn.close()
    print("Database entry updated")
    return redirect(url_for('main'))

def query_db(query, args=(), one=False):
    cur = get_db_connection().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def floatandround(input):
    output = round(float(input),1)
    return input

# Main Route
@app.route("/")
def main():
    print("Main route:")
    conditions = ["RSI out of Red",
                  "MACD Histo rising",
                  "MACD Torys Trendzone red",
                  "Heikin Ashi confirmed",
                  "Support price level",
                  "EMA support",
                  "No EMA Resistance",
                  "Higher Low",
                  "Higher High"]
    conditionsMo = ["RSI reset above 50",
                  "MACD Histo rising",
                  "Heikin Ashi confirmed",
                  "Support price level",
                  "EMA support",
                  "No EMA Resistance",
                  "Higher Low",
                  "Higher High"]
    args = ["arg1","arg2","arg3","arg4","arg5","arg6","arg7","arg8","arg9"]
    tfnum = [1,3,15,60,240,1440,10080,40320]
    tfname = ["1 minute","3 minutes","15 minutes","1 hour","4 hours","Daily","Weekly","Monthly"]
    tfindex = len(tfname)  
    CL = query_db('SELECT * FROM Checklist')
    return render_template('main.html', CL=CL, tfname=tfname, tfindex=tfindex, tfnum=tfnum, conditions=conditions, conditionsMo=conditionsMo, args=args)

if __name__ == "__main__":
  # If you are debugging you can do that in the browser:
  # app.run()
  # If you want to view the flaskwebgui window:
  FlaskUI(app=app, server="flask", width=572, height=926).run()