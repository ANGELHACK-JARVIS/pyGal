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
    cursor.execute("Select * from Coordinates")
    places=cursor.fetchall()
    print places
    for place in places:
        cursor.execute("Select avg(Theft), avg(Violence), avg(Harassment) from Security, Coordinates where Security.Loc_id=Coordinates.Loc_id and Coordinates.Loc_name=%s",(place[1]))
        details=cursor.fetchall()[0]
        crime_graph.add(place[1],[details[0],details[1], details[2]])
    chart = crime_graph.render(is_unicode=True)
    return render_template('pygal.html', chart=chart)



############################################################
##################################################################

if __name__ == "__main__":
    app.debug = True
    app.run()
