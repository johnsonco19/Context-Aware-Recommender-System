import util
from main import get_url
from flask import Flask, render_template, request, url_for, session
from werkzeug.utils import redirect
app = Flask(__name__)

username = 'postgres'
password = 'Password'
host = '127.0.0.1'
port = '5432'
database = 'CinemaNChill'

#Test to check if the SQL scripts being run in the search function are returning the correct information
def testSearch():
    #testing using the search genre buttons from search page to pull correct genre information
    cursor, connection = util.connect_to_db(username, password, host, port, database)
    record = util.run_and_fetch_sql(cursor,
                                    "Select title, startyear, genres from moviedata where genres like '%Romance%' and startyear is not null order by startyear desc")
    util.disconnect_from_db(connection, cursor)
    #print(record[:10])
    if "Romance" in str(record[:10]):
        print('Success in using search genre in TestSearch')
    else:
        print('Fail in using search genre in TestSearch')
    #testing using the search bar sql script to pull the correct record from the database using a title
    cursor, connection = util.connect_to_db(username, password, host, port, database)
    record2 = util.run_and_fetch_sql(cursor, "Select title, startyear, genres from moviedata where title like '%One Giant Leap (2022)%'")
    util.disconnect_from_db(connection, cursor)
    #print(record2)
    if "One Giant Leap (2022)" in str(record2):
        print('Success in using search bar in  TestSearch')
    else:
        print("Fail in using search bar in TestSearch")

# testing signing in and signing up SQL statements to ensure functionality of those functions in the main.py using
# control statements.
def testSigin_Signup():
    #testing signin on a controlled account
    cursor, connection = util.connect_to_db(username, password, host, port, database)
    record = util.run_and_fetch_sql(cursor, "SELECT username from userpass where Tester")
    record = len(record)
    #if the record is empty, it failed to find the account in the database otherwise it's a success
    if record == 0:
        print("Failure in signin control")
    else:
        print("success in signin control")
    util.disconnect_from_db(connection, cursor)
    #testing the signup feature by inserting an account into the database and making sure the statements worked
    #checking first that the information is not already in the database
    cursor, connection = util.connect_to_db(username, password, host, port, database)
    userpass = "username = " + "'testing123'"
    record = util.run_and_fetch_sql(cursor, "SELECT username from userpass where %s" % userpass)
    username1 = "'testing123'"
    password1 = "'testing123'"
    record = len(record)
    #if the record is greater than 0, it found something in the database and should return a fail
    if record < 1:
        send = util.runSQL(cursor, "insert into userpass values ( %s , %s ); Commit;" % (username1, password1))
        send = util.runSQL(cursor, "insert into userinfo values (%s, 0, '{}', '{}','{}', '{}'); Commit;" % username1)
        session['username'] = username1
        print('Success in signing up a user account')
    else:
        print('failure in signing up a user account')
    util.disconnect_from_db(connection, cursor)

#testing the functionality of the SQL statements in the userpage to ensure they are pulling the correct information
def testUserPage():
    cursor, connection = util.connect_to_db(username, password, host, port, database)
    username123 = "'123test'"
    #pulling the records from a controlled account made in the database
    #send = util.runSQL(cursor, "insert into userinfo values (%s, 0, '{}', '{}','{}', '{}'); Commit;" % username)
    record = util.run_and_fetch_sql(cursor, "select favorites from userinfo where username = " + username123)
    record2 = util.run_and_fetch_sql(cursor, "select wishlist from userinfo where username = " + username123)
    record3 = util.run_and_fetch_sql(cursor, "select watched from userinfo where username = " + username123)
    record4 = util.run_and_fetch_sql(cursor, "select recommendations from userinfo where username = " + username123)
    #print(record)
    #ensuring the data pulled from each record in the correct information. The for loops allow for breaking down the list of tuples, which is how data
    #is returned from the database.
    for x in record:
        for y in x:
            if y==[]:
                print("successful grab of favorites in testUserPage")
            else:
                print('Failure to grab favorites in testUserPage')
    for x in record2:
        for y in x:
            if y==[]:
                print("successful grab of wishlist in testUserPage")
            else:
                print('Failure to grab wishlist in testUserPage')
    for x in record3:
        for y in x:
            if y==[]:
                print("successful grab of watched in testUserPage")
            else:
                print('Failure to grab watched in testUserPage')
    for x in record4:
        for y in x:
            if y==[]:
                print("successful grab of recommendations in testUserPage")
            else:
                print('Failure to grab recommendations in testUserPage')
    util.disconnect_from_db(connection, cursor)

# Tests if the correct URLs are collected by the function get_url
def testurl():
    # Runs get_url to get an example of links from a query
    urllist = get_url("home alone")
    # Prints all urls in the list
    print(urllist)
    # Checks if certain links are present in the lst
    if ("http://www.youtube.com/watch?v=m8RVpPri4BA" in urllist):
        print("Youtube Link Present")
    else:
        print("Youtube Link Missing")

    if ("https://www.disneyplus.com/video/18938eee-a818-4ebd-9d0e-ee9b330bf82d?distributionPartner=google" in urllist):
        print("Disney Link Present")
    else:
        print("Disney Link Missing")

    # Runs get_url to get an example of links from a query
    urllist = get_url("kung fu panda")
    # Prints all urls in the list
    print(urllist)
    # Checks if certain links are present in the list
    if ("http://www.youtube.com/watch?v=tuOA5WZVQRQ" in urllist):
        print("Youtube Link Present")
    else:
        print("Youtube Link Missing")

    if ("https://tv.apple.com/us/movie/kung-fu-panda/umc.cmc.34elthhr2qybuu3emdzn4d2fr?action=play" in urllist):
        print("Apple TV Link Present")
    else:
        print("Apple TV Link Missing")

# Test recommendation algorithm for collecting favorites, generating recommendations, and updating the recommendation list.
def testrecalgorithm():

    # Gets favorites from an entry under the username "TEST123"
    cursor, connection = util.connect_to_db(username, password, host, port, database)
    record = util.run_and_fetch_sql(cursor, 'select favorites from userinfo where username = ' + "'TEST123'")
    # If favorites correctly found, "testvalue" should be present
    if ("testvalue" in record):
        print("Favorites Correctly Found")
    else:
        print("Error in favorites")

    # Runs a test where movies with genres "Fantasy", "Romance", and Animation
    cursor, connection = util.connect_to_db(username, password, host, port, database)
    record = util.run_and_fetch_sql(cursor, 'select title from moviedata where genres like ' + "'%" + "Fantasy" + "%' and genres like " + "'%" + "Romance" + "%' and genres like " + "'%" + "Animation" + "%' order by avgrating desc")[:10]
    util.disconnect_from_db(connection, cursor)
    #Shows movies found via the query
    print(record)

    # Commits the Recommendations into the user entry
    dbarray = "[ "
    for x in record[:8]:
        y = str(x)
        y = y[1:(len(y) - 2)]
        print(y)
        dbarray = dbarray + y + ","
    dbarray = dbarray[:-1] + "]"
    print("update userinfo set recommendations = ARRAY " + str(dbarray) + " where username = " + "'TEST123'" + "; COMMIT;")
    cursor, connection = util.connect_to_db(username, password, host, port, database)
    util.runnerSQL(cursor, "update userinfo set watched = ARRAY " + dbarray + " where username = " + "'TEST123'" + "; COMMIT;")
    record = util.runnerSQL(cursor, "select recommendations from userinfo where username = 'TEST123'")
    # Prints the recommendations placed into recommendations
    print(record)
    util.disconnect_from_db(connection, cursor)

# Tests if essential values are in the right place in the data array when searching. Verify 4 items, title, startyear, genre, avgrating.
def testmovieid():
    # Test Case with No Genres
    cursor, connection = util.connect_to_db(username, password, host, port, database)
    record = util.run_and_fetch_sql(cursor,"Select title, startyear, genres, avgrating from moviedata where title = 'Kinectimals (2010)'")
    print(record[0])
    titlevalue = record[0][0]
    yearvalue = record[0][1]
    genrevalue = record[0][2]
    ratevalue = record[0][3]
    if (titlevalue == "Kinectimals (2010)"):
        print("Title1 Correct")
    else:
        print("Title1 Missing")
    if (yearvalue == 2010):
        print("Year1 Correct")
    else:
        print("Year Missing")
    if (genrevalue == None):
        print("Genre1 Correct")
    else:
        print("Genre1 Missing")
    if (ratevalue == 7.2):
        print("Rating1 Correct")
    else:
        print("Rating1 Missing")
    util.disconnect_from_db(connection, cursor)

    # Test Case with Single Genre
    cursor, connection = util.connect_to_db(username, password, host, port, database)
    record = util.run_and_fetch_sql(cursor,"Select title, startyear, genres, avgrating from moviedata where title = 'The River (1988)'")
    print(record[0])
    titlevalue2 = record[0][0]
    yearvalue2 = record[0][1]
    genrevalue2 = record[0][2]
    ratevalue2 = record[0][3]
    if (titlevalue2 == "The River (1988)"):
        print("Title2 Correct")
    else:
        print("Title2 Missing")
    if (yearvalue2 == 1988):
        print("Year2 Correct")
    else:
        print("Year2 Missing")
    if (genrevalue2 == "Comedy"):
        print("Genre2 Correct")
    else:
        print("Genre2 Missing")
    if (ratevalue2 == 7.4):
        print("Rating2 Correct")
    else:
        print("Rating2 Missing")
    util.disconnect_from_db(connection, cursor)

    # Test Case with Multiple Genres
    cursor, connection = util.connect_to_db(username, password, host, port, database)
    record = util.run_and_fetch_sql(cursor,"Select title, startyear, genres, avgrating from moviedata where title = 'Three Days (2001)'")
    print(record[0])
    titlevalue3 = record[0][0]
    yearvalue3 = record[0][1]
    genrevalue3 = record[0][2]
    ratevalue3 = record[0][3]
    if (titlevalue3 == "Three Days (2001)"):
        print("Title3 Correct")
    else:
        print("Title3 Missing")
    if (yearvalue3 == 2001):
        print("Year3 Correct")
    else:
        print("Year3 Missing")
    if (genrevalue3 == "Drama,Family,Fantasy"):
        print("Genre3 Correct")
    else:
        print("Genre3 Missing")
    if (ratevalue3 == 7):
        print("Rating3 Correct")
    else:
        print("Rating3 Missing")
    util.disconnect_from_db(connection, cursor)
