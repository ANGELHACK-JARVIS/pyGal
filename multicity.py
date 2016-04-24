from flask import Flask, render_template, json, request, redirect, session
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
import pygal
from pygal.style import BlueStyle, NeonStyle,DarkSolarizedStyle, LightSolarizedStyle, LightColorizedStyle, DarkColorizedStyle, TurquoiseStyle
app = Flask(__name__)
GoogleMaps(app)
app.secret_key = 'ssh...Big secret!'
#MySQL configurations

mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'utkarsh@mit'
app.config['MYSQL_DATABASE_DB'] = 'safelocality'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/pygal')
def mulCity():
    title="Crime Rates"
    crime_graph=pygal.Bar(width=600, height=600, explicit_size=True, title=title, style=BlueStyle, disable_xml_declaration=True, range=(0,10))
    crime_graph.x_labels=['Theft','Violence', 'Harassment']
    conn = mysql.connect()
    cursor = conn.cursor()
    lifestyle_graph=pygal.Bar(width=1200, height=600, explicit_size=True, title="Living Standards", style=BlueStyle, disable_xml_declaration=True, range=(0,10))
    lifestyle_graph.x_labels=["Water", "Electricity", "Network Availability", "Cleanliness", "Green Space", "Local Entertainment", "Night Life", "Services", "Education", "Neighbourhood"]
    cursor.execute("Select * from Coordinates")
    places=cursor.fetchall()
    print places
    for place in places:
        cursor.execute("SELECT avg(Theft), avg(Violence), avg(Harassment) from Security, Coordinates where Security.Loc_id=%s", (place[0]))
        crime_details=cursor.fetchall()[0]
        crime_graph.add(place[1], [crime_details[0], crime_details[1], crime_details[2]])
        cursor.execute("SELECT avg(Water), avg(Electricity), avg(Network_Availability), avg(Cleanliness), avg(Green_space), avg(Local_Entertainment), avg(NightLife), avg(Repairmen_avail), avg(Education), avg(Neighbourhood) from LifeStyle where Loc_id=%s", (place[0]))
        lifestyle_details=cursor.fetchall()[0]
        lifestyle_graph.add(place[1],[lifestyle_details[0], lifestyle_details[1], lifestyle_details[2], lifestyle_details[3], lifestyle_details[4], lifestyle_details[5], lifestyle_details[6], lifestyle_details[7], lifestyle_details[8], lifestyle_details[9] ])

    chart = crime_graph.render(is_unicode=True)
    life=lifestyle_graph.render(is_unicode=True)
    return render_template('pygal.html', chart=chart, life=life)



############################################################
##################################################################

if __name__ == "__main__":
    app.debug = True
    app.run()
