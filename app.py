
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

# route to index.html
@app.route("/")
def main():
    return render_template('index.html')

# route to signup.html
@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

# interact with MySQL for sign up
@app.route('/signUp',methods=['POST'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        _firstname = request.form['inputFirstName']
        _lastname = request.form['inputLastName']

        # validate the received values
        if _name and _email and _password:

            # All Good, let's call MySQL

            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser',(_name,_firstname,_lastname,_email,_hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return redirect('/showSignin')
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']

        # connect to mysql
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0][5]),_password):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()

@app.route('/userHome')
def userHome():
    if session.get('user'):
        mymap = Map(
        identifier="view-side",
        lat=37.4419,
        lng=-122.1419,
        style = "height:600px;width:600px;",
        markers={'http://maps.google.com/mapfiles/ms/icons/green-dot.png':[(37.4419, -122.1419)],
                 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png':[(37.4300, -122.1400)]}
        )
        return render_template('userHome.html', mymap=mymap)
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

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
    lifestyle_graph=pygal.Bar(width=600, height=600, explicit_size=True, title="Living Standards", style=BlueStyle, disable_xml_declaration=True, range=(0,10))
    cursor.close()
    conn.close()
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.callproc('lifestyle')
    data=cursor.fetchone()
    lifestyle_values=[data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9]]
    lifestyle_labels=["Water", "Electricity", "Network_Availability", "Cleanliness", "Green_space", "Local_Entertainment", "NightLife", "Repairmen_avail", "Education", "Neighbourhood"]
    lifestyle_graph.x_values=lifestyle_labels
    lifestyle_graph.add('Rating', lifestyle_values)
    graphs=[crime_graph, lifestyle_graph]
    cursor.close()
    conn.close()
    graphs=[crime_graph, lifestyle_graph]
    return render_template('pygal.html', graphs=graphs)
if __name__ == "__main__":
    app.debug = True
    app.run()
