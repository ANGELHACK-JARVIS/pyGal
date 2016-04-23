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


#pyGal implementation.
@app.route('/pygal')
def makeGraph():
    title="Crime Rates"
    crime_graph=pygal.Bar(width=600, height=600, explicit_size=True, title=title, style=BlueStyle, disable_xml_declaration=True, range=(0,10))
    crime_labels=['Theft','Violence', 'Harassment']
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.callproc('security')
    data=cursor.fetchone()
    crime_values=[data[0],data[1],data[2]]
    crime_graph.x_labels=crime_labels
    crime_graph.add('Rating', crime_values)
    lifestyle_graph=pygal.Bar(width=1200, height=600, explicit_size=True, title="Living Standards", style=BlueStyle, disable_xml_declaration=True, range=(0,10))
    cursor.close()
    conn.close()
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.callproc('lifestyle')
    data=cursor.fetchone()
    lifestyle_values=[data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9]]
    lifestyle_labels=["Water", "Electricity", "Network Availability", "Cleanliness", "Green Space", "Local Entertainment", "Night Life", "Services", "Education", "Neighbourhood"]
    lifestyle_graph.x_labels=lifestyle_labels
    lifestyle_graph.add('Rating', lifestyle_values)
    graphs=[crime_graph, lifestyle_graph]
    cursor.close()
    conn.close()
    return render_template('pygal.html', graphs=graphs)

if __name__ == "__main__":
    app.debug = True
    app.run()
