
from flask import Flask, render_template, request, redirect, url_for
import boto3
app = Flask(__name__)

TABLE_NAME = "Album"

dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table(TABLE_NAME)

#asks the user to enter all the paramaters of the data table creating a new album, or new row of data and adding it to the table
def create_album():
    
    AlbumTitle = input("Enter Album Name: ")

    Artist = input("Enter Artist Name: ")

    Length = input("Enter Album Length(minuets): ")
 
    ReleaseDate = input("Enter Release Date: ")

    Rating = input("Eneter Album Ratings ")
    
    New_Album = {"AlbumTitle" : AlbumTitle,"Artist" : Artist, "Length(Minuets)" : int(Length), "Release Date" : int(ReleaseDate), "Rating" : int(Rating)}
    table.put_item(Item = New_Album)

#Prints out everything in a row of the data table
def print_Album(album_dict):
    # print out the values of the Album dictionary
    print("AlbumTitle: ", album_dict["AlbumTitle"])
    print()
    print("Artist: ",album_dict["Artist"])
    print()
    for rating in album_dict["Rating"]:
        print(rating, end=" , ")
    print(" Length(minuets): ", album_dict["Length(Minuets)"])
    print()
    print("Release Date: ",album_dict["Release Date"])
    print()

#Loops through all rows of the data table using print album to print all paramaters in the row out
def print_all_Albums():
    response = table.scan() #get all of the albums
    for Album in response["Items"]:
        print_Album(Album)



#asks the user which album they would like to update and then asks what rating they would like to add. 
#uses a try catch block keep from getting an error and terminating the code
def update_album_rating():
    AlbumTitle=input("What is the Album Title? ")
    Ratings = (input("What is the new rating: "))
    try:
        table.update_item(
        Key = {"AlbumTitle": AlbumTitle}, 
        UpdateExpression = "SET rating = list_append(Ratings, :r)", ExpressionAttributeValues = {':r': [Ratings],}
    )
    except:
        print('error in updating albums ratings')
    

#delets item from the table
def delete_album():
    table.delete_item(
    Key={
        'AlbumTitle': input("What is the Album Title of the Album you would like to delete? "),
        }
    )

#this code is incomleate but it is supposed to return just the row of data that is specified by the user
def query_Album():
        response = table.get_item(
        Key={
            'AlbumTitle': input("What is the Album Title of the Album you would like to Querry on? "),
            }
        )
        if "Item" not in response:
            print("Album not found")
            return
        item = response['Item']
        print(item)
        album = response.get("Item")
        artist_list = album["Item"] 
        print(artist_list)

# everything from here until def print_menu used a lot of help from chatgpt.
#I had a lot of trouble trying to get this to work with flask and I wasnted to at least try something.
#This part of the code still deosnt work as I only created one HTML file of the several needed.
#If I was able to figure out how to create this on my own I would have reused the same template more.  
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        album_title = request.form['AlbumTitle']
        artist = request.form['Artist']
        length = int(request.form['Length'])
        release_date = int(request.form['ReleaseDate'])
        rating = int(request.form['Rating'])
        create_album(album_title, artist, length, release_date, rating)
        return redirect(url_for('list_albums'))
    return render_template('create_album.html')


@app.route('/albums')
def list_albums():
    albums = print_all_Albums()
    return render_template('list_albums.html', albums=albums)


@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        album_title = request.form['AlbumTitle']
        new_rating = int(request.form['Rating'])
        update_album_rating(album_title, new_rating)
        return redirect(url_for('list_albums'))
    return render_template('update_rating.html')

@app.route('/delete', methods=['POST'])
def delete():
    album_title = request.form['AlbumTitle']
    delete_album(album_title)
    return redirect(url_for('list_albums'))

@app.route('/album/<album_title>')
def album_detail(AlbumTitle):
    album = query_Album(AlbumTitle)
    if album:
        return render_template('album_detail.html', album=album)
    return f"Album {AlbumTitle} not found", 404

#This was the original menu and main method I created that allowed the user to select how they wanted to interact with the database. 
#Before incorperating flask it was working and I was able to add and delete rows of data from my table. 
def print_menu():
    print("----------------------------")
    print("Press C: to CREATE a new player")
    print("Press R: to READ all players")
    print("Press U: to UPDATE a new player (add hits)")
    print("Press D: to DELETE a player")
    print("Press Q: to Query a player's average hits")
    print("Press X: to EXIT application")
    print("----------------------------")


def main():
    input_char = ""
    while input_char.upper() != "X":
        print_menu()
        input_char = input("Choice: ")
        if input_char.upper() == "C":
            create_album()
        elif input_char.upper() == "R":
            print_all_Albums()
        elif input_char.upper() == "U":
            update_album_rating()
        elif input_char.upper() == "D":
            delete_album()
        elif input_char.upper() == "Q":
            query_Album()
        elif input_char.upper() == "X":
            print("exiting...")
        else:
            print('Not a valid option. Try again.')
main()
