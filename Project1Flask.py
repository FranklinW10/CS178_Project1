from flask import Flask, render_template, request
app = Flask(__name__)

from flask import render_template
import pymysql
import creds 


def get_conn():
    conn = pymysql.connect(
        host= creds.host,
        user= creds.user, 
        password = creds.password,
        db=creds.db,
        )
    return conn

def execute_query(query, args=()):
    cur = get_conn().cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows

#Code to desplay all data from the RDS
def display_html(rows):
    html = ""
    html += """<table><tr><th>ArtistID</th><th>Artist</th><th>Track Title</th><th>Price</th><th>Milliseconds</th></tr>"""

    for r in rows:
        html += "<tr><td>" + str(r[0]) + "</td><td>" + str(r[1]) + "</td><td>" + str(r[2]) + "</td><td>" + str(r[3]) + "</td><td>" + str(r[4]) + "</td></tr>"
    html += "</table></body>"
    return html

#route that allows user to veiw the entire database. Selects all feilds from the database returing them all. 
@app.route("/viewdb")
def viewdb():
    rows = execute_query("""SELECT ArtistId, Artist.Name, Track.Name, UnitPrice, Milliseconds
                FROM Artist JOIN Album using (ArtistID) JOIN Track using (AlbumID)
                ORDER BY Track.Name 
                Limit 500""")
    return display_html(rows)

## When called by /pricequerytextbox returns all rows of data that are longer then the specified time
@app.route("/timequery/<time>")
def viewtime(time):
    rows = execute_query("""select ArtistId, Artist.Name, Track.Name, UnitPrice, Milliseconds
            from Artist JOIN Album using (ArtistID) JOIN Track using (AlbumID)
            where Milliseconds >= %s order by Track.Name 
            Limit 500""", (int(time)))
    return display_html(rows) 

#when called by /pricequerytextbox returns all rows of data that have a unit price equal to the specified one
@app.route("/pricequery/<price>")
def viewprices(price):
    rows = execute_query("""select ArtistId, Artist.Name, Track.Name, UnitPrice, Milliseconds
            from Artist JOIN Album using (ArtistID) JOIN Track using (AlbumID)
            where UnitPrice = %s order by Track.Name 
            Limit 500""", (str(price)))
    return display_html(rows) 

#when called by /artistquerytextbox retuns all artists that have a name equal to the specified name
@app.route("/artistquery/<artist>")
def viewartists(artist):
    rows = execute_query("""select ArtistId, Artist.Name, Track.Name, UnitPrice, Milliseconds
            from Artist JOIN Album using (ArtistID) JOIN Track using (AlbumID)
            where Artist.Name = %s order by Track.Name 
            Limit 500""", (str(artist)))
    return display_html(rows) 

from flask import request

#method that gets the layout for the text box and asks user for price 
@app.route("/pricequerytextbox", methods = ['GET'])
def price_form():
  return render_template('textbox.html', fieldname = "Price")

#Sends given text to viewprices method
@app.route("/pricequerytextbox", methods = ['POST'])
def price_form_post():
  text = request.form['text']
  return viewprices(text)

#similar to /pricequerytextbox
@app.route("/timequerytextbox", methods = ['GET'])
def time_form():
  return render_template('textbox.html', fieldname = "time")


@app.route("/timequerytextbox", methods = ['POST'])
def time_form_post():
    text = request.form['text']
    return viewtime(text)

#similar to /pricequerytextbox
@app.route("/artistquerytextbox", methods = ['GET'])
def artist_form():
  return render_template('textbox.html', fieldname = "artist")


@app.route("/artistquerytextbox", methods = ['POST'])
def artist_form_post():
    text = request.form['text']
    return viewartists(text)

#asks user which paramater they would like to queery on using a new template 
@app.route("/CURD", methods = ['GET'])
def selection():
  return render_template('selectiontextbox.html', fieldname = "What would you like to queery on: artist, time, or price")

#uses the inputed text form the text box to call the method that relates to it. I wasnt able to make this work compleatly because I couldnt figure out how to change URLS
@app.route("/CURD", methods = ['POST'])
def selction_post():
   text = request.form['text']
   if text == "artist":
        return artist_form()
   if text == "time":
      return time_form()
   if text == "price":
      return price_form()




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)


