from lib2to3.pgen2 import driver
import document as document
import csv
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, url_for, session
from werkzeug.utils import redirect
from selenium import webdriver

import util

app = Flask(__name__)

username = 'postgres'
password = 'Password'
host = '127.0.0.1'
port = '5432'
database = 'CinemaNChill'


# the app route the main home page
@app.route('/', methods=["GET", 'POST'])
def index():
    session['username'] = ''
    return render_template('index.html')

#The function used to handle the signing in of a user already in our system.
@app.route('/signIn', methods=["GET", 'POST'])
def signIn():
    if request.method == 'POST':
        username1 = request.form.get("email")
        password1 = request.form.get("password")
        print(username1)
        print(password1)
        print("username and password:")
        print(username1 + " " + password1)
        # add code to ping the database for the username and password
        cursor, connection = util.connect_to_db(username, password, host, port, database)
        userpass = "username = " + "'" + username1 + "'" + " and password = " + "'" + password1 + "'"
        record = util.run_and_fetch_sql(cursor, "SELECT username from userpass where %s" % userpass)
        record = len(record)
        # print('size of the list' + record)
        util.disconnect_from_db(connection, cursor)
        if record == 0:
            # on failure print message to screen
            return redirect(url_for('signIn'))
        else:
            session['username'] = "'" + username1 + "'"
            return redirect(url_for('userPage'))
    return render_template('signIn.html')

#The function used to handle the signing up of a user into our system.
@app.route('/signUp', methods=["GET", 'POST'])
def signUp():
    if request.method == "POST":
        username1 = request.form.get("email")
        password1 = request.form.get("psw")
        print(username1 + ' ' + password1)
        cursor, connection = util.connect_to_db(username, password, host, port, database)
        userpass = "username = " + "'" + username1 + "'"
        record = util.run_and_fetch_sql(cursor, "SELECT username from userpass where %s" % userpass)
        # print('size of the list' + record)
        username1 = "'" + username1 + "'"
        password1 = "'" + password1 + "'"
        record = len(record)\
        #check to see if a user is already in the system, if not it will add them to the system.
        if record < 1:
            send = util.runSQL(cursor, "insert into userpass values ( %s , %s ); Commit;" % (username1, password1))
            send = util.runSQL(cursor, "insert into userinfo values (%s, 0, '{}', '{}','{}', '{}'); Commit;" % (username1))
            session['username'] = username1
            util.disconnect_from_db(connection, cursor)
            return redirect(url_for('userPage'))
        else:
            util.disconnect_from_db(connection, cursor)
            return redirect(url_for('index'))
    return render_template('signUp.html')

#This is the function used in the search pages to generate the list of genres and any search done in the search bar.
@app.route('/search', methods=["GET", 'POST'])
def search():
    #split into an if else statement to display different pages based on if the user is signed in or not.
    if(session['username'] == ''):
        if request.method == 'POST':
            if request.form.get("genrebutton"):
                print(request.form.get("genrebutton"))
                session['movieGenre'] = request.form.get("genrebutton")
                cursor, connection = util.connect_to_db(username, password, host, port, database)
                newGenre = "'%" + session['movieGenre'] + "%'"
                record = util.run_and_fetch_sql(cursor,"Select title, startyear, genres from moviedata where genres like %s and startyear is not null order by startyear desc" % newGenre)

                if record == -1:
                    print('Error in searchMovie')
                else:
                    log = record[:30]
                util.disconnect_from_db(connection, cursor)
                return render_template('search.html', sql_table=log)
            else:
                session['movieName'] = request.form.get("searched")
                cursor, connection = util.connect_to_db(username, password, host, port, database)
                titleSearched = session['movieName']
                newTitle = "'%" + titleSearched + "%'"
                record = util.run_and_fetch_sql(cursor,
                                                "Select title, startyear, genres from moviedata where title like %s and startyear is not null order by startyear desc" % newTitle)
                if record == -1:
                    print('Error in searchMovie')
                else:
                    log = record[:30]
                util.disconnect_from_db(connection, cursor)
                return render_template('search.html', sql_table=log)
        return render_template('search.html')
    else:
        if request.method == 'POST':
            if request.form.get("logout"):
                session['username'] = ''
                return redirect(url_for('index'))
            if request.form.get("genrebutton"):
                print(request.form.get("genrebutton"))
                session['movieGenre'] = request.form.get("genrebutton")
                cursor, connection = util.connect_to_db(username, password, host, port, database)
                newGenre = "'%" + session['movieGenre'] + "%'"
                record = util.run_and_fetch_sql(cursor,"Select title, startyear, genres from moviedata where genres like %s and startyear is not null order by startyear desc" % newGenre)
                if record == -1:
                    print('Error in searchMovie')
                else:
                    log = record[:30]
                util.disconnect_from_db(connection, cursor)
                return render_template('search2.html', sql_table=log)
            else:
                session['movieName'] = request.form.get("searched")
                cursor, connection = util.connect_to_db(username, password, host, port, database)
                titleSearched = session['movieName']
                newTitle = "'%" + titleSearched + "%'"
                record = util.run_and_fetch_sql(cursor,
                                                "Select title, startyear, genres from moviedata where ptitle like %s and startyear is not null order by startyear desc" % newTitle)
                if record == -1:
                    print('Error in searchMovie')
                else:
                    log = record[:30]
                util.disconnect_from_db(connection, cursor)
                return render_template('search2.html', sql_table=log)
        return render_template('search2.html')


# session made for testing purporses: first sprint build
# loads the userpage for the user's profile.
@app.route('/userprofile', methods=["GET", 'POST'])
def userPage():
    # code for the button mechanics on the userprofile, not currently setup atm: sprint one build.
    if request.method == "POST":
        if request.form.get('movieAdd'):
            return redirect(url_for('search'))
        if request.form.get("wishlistAdd"):
            return redirect(url_for('search'))
        if request.form.get("historyAdd"):
            return redirect(url_for('search'))
        if request.form.get("recommendationUpdate"):
            recAlgorithm(session['username'])
            return redirect(url_for('userPage'))
        elif request.form.get("logout"):
            session['username'] = ''
            return redirect(url_for('index'))
    # code for adding the list of favorite movies to the user profile
    cursor, connection = util.connect_to_db(username, password, host, port, database)
    record = util.run_and_fetch_sql(cursor, "select favorites from userinfo where username = " + session['username'])
    #print(record)
    records = []
    if record != -1:
        for x in record:
            for y in x:
                for z in y:
                    #print(z)
                    records.append(z)
    #print(records)
    if record == -1:
        print('Error in retrieving info from userinfo table on favorites column')
    else:
        col_names = [desc[0] for desc in cursor.description]
        log4 = records[:10]
    # code for adding the list of wishlist movies to the user profile
    record2 = util.run_and_fetch_sql(cursor, "select wishlist from userinfo where username = " + session['username'])
    #print(record2)
    records2 = []
    if record2 != -1:
        for x in record2:
            for y in x:
                for z in y:
                    #print(z)
                    records2.append(z)
    #print(records2)
    if record2 == -1:
        print('Error in retrieving info from userinfo table on wishlist column')
    else:
        col_names = [desc[0] for desc in cursor.description]
        log2 = records2[:10]
    # code for adding the list of the watched movies to the userprofile
    record3 = util.run_and_fetch_sql(cursor,
                                     "select watched from userinfo where username = " + session['username'])
    #print(record3)
    records3 = []
    if record3 != -1:
        for x in record3:
            for y in x:
                for z in y:
                    #print(z)
                    records3.append(z)
    #print(records3)
    if record3 == -1:
        print('Error in retrieving info from userinfo table on wishlist column')
    else:
        col_names = [desc[0] for desc in cursor.description]
        log3 = records3[:10]
    # code for adding the list of recommended movies to the userprofile
    record5 = util.run_and_fetch_sql(cursor,
                                     "select recommendations from userinfo where username = " + session['username'])
    print("printing the list of movies from the userprofile recommendation list")
    print(record5)
    records5 = []
    if record5 != -1:
        for x in record5:
            for y in x:
                for z in y:
                    print(z)
                    records5.append(z)
    print(records5)
    if record5 == -1:
        print('Error in retrieving info from userinfo table on wishlist column')
    else:
        col_names = [desc[0] for desc in cursor.description]
        log5 = records5[:10]
    # end code for the liked books, again do not edit.
    if session['username']== '':
         return redirect(url_for('signIn'))
    else:
        return render_template('userProfile.html', username=session['username'], sql_table=log4, sql_table2=log2,
                           sql_table3=log3, sql_table5 = log5, table_title=col_names)

# The logic and page rendering for the advanced search results page.
@app.route('/rPage', methods=["GET", 'POST'])
def recPage():
    if(session['username'] == ''):
        if request.method == "POST":
            print('testing')
            SQLscript = "Select title, startyear, genres from moviedata where startyear is not null and ( "
            listofoptions = ["Reality-TV", "Musical", "War", "Sport", "Romance", "Family", "Comedy", "Animation", "Western",
                             "Sci-Fi", "Short", "Action", "Biography", "History", "Adult", "Crime", "Music", "Fantasy",
                             "Horror", "Drama", "New", "Talk-Show", "Thriller", "Game-Show", "Adventure", "Documentary",
                             "Mystery", "video", "tvSpecial", "tvSeries", "tvShort", "tvPilot", "movie", "tvMovie",
                             'tvMiniSeries', 'videoGame', 'tvEpisode']
            for x in listofoptions:
                y = request.form.get(x)
                if y != None:
                    print(y)
                    SQLscript = SQLscript + y
            SQLscript = SQLscript[:len(SQLscript) - 3]
            SQLscript = SQLscript + " )order by moviedata.startyear desc"
            print(SQLscript)
            session['pass'] = SQLscript
            return redirect(url_for('recommendMovies'))
        return render_template('advancedSearchResults.html')
    else:
        if request.method == "POST":
            if request.form.get("logout"):
                session['username'] = ''
                return redirect(url_for('index'))
            print('testing')
            SQLscript = "Select title, startyear, genres from moviedata where startyear is not null  and ( "
            listofoptions = ["Reality-TV", "Musical", "War", "Sport", "Romance", "Family", "Comedy", "Animation", "Western",
                             "Sci-Fi", "Short", "Action", "Biography", "History", "Adult", "Crime", "Music", "Fantasy",
                             "Horror", "Drama", "New", "Talk-Show", "Thriller", "Game-Show", "Adventure", "Documentary",
                             "Mystery", "video", "tvSpecial", "tvSeries", "tvShort", "tvPilot", "movie", "tvMovie",
                             'tvMiniSeries', 'videoGame', 'tvEpisode']
            for x in listofoptions:
                y = request.form.get(x)
                if y != None:
                    print(y)
                    SQLscript = SQLscript + y
            SQLscript = SQLscript[:len(SQLscript) - 3]
            SQLscript = SQLscript + " )order by moviedata.startyear desc"
            print(SQLscript)
            session['pass'] = SQLscript
            return redirect(url_for('recommendMovies'))
        return render_template('advancedSearchResults2.html')

#This page hosts the results from the advanced search results, in a list format
@app.route('/recommendMovies', methods=["GET", 'POST'])
def recommendMovies():
    if(session['username'] == ''):
        cursor, connection = util.connect_to_db(username, password, host, port, database)
        record = util.run_and_fetch_sql(cursor,
                                        session['pass'])
        if record == -1:
            print('Error in recommendMovies')
        else:
            col_names = [desc[0] for desc in cursor.description]
            log5 = record[:30]
        util.disconnect_from_db(connection, cursor)
        if request.method == 'POST':
                if request.form.get("genrebutton"):
                    print(request.form.get("genrebutton"))
                    session['movieGenre'] = request.form.get("genrebutton")
                    cursor, connection = util.connect_to_db(username, password, host, port, database)
                    newGenre = "'%" + session['movieGenre'] + "%'"
                    record = util.run_and_fetch_sql(cursor,"Select title, startyear, genres from moviedata where genres like %s and startyear is not null order by startyear desc" % newGenre)
                    if record == -1:
                        print('Error in searchMovie')
                    else:
                        log = record[:30]
                    util.disconnect_from_db(connection, cursor)
                    return render_template('search.html', sql_table=log)
                else:
                    session['movieName'] = request.form.get("searched")
                    cursor, connection = util.connect_to_db(username, password, host, port, database)
                    titleSearched = session['movieName']
                    newTitle = "'%" + titleSearched + "%'"
                    record = util.run_and_fetch_sql(cursor,
                                                    "Select title, startyear, genres from moviedata where ptitle like %s and startyear is not null order by startyear desc" % newTitle)
                    if record == -1:
                        print('Error in searchMovie')
                    else:
                        log = record[:30]
                    util.disconnect_from_db(connection, cursor)
                    return render_template('search.html', sql_table=log)
        return render_template('recommendationsPage.html', sql_table=log5, table_title=col_names)
    else:
        cursor, connection = util.connect_to_db(username, password, host, port, database)
        record = util.run_and_fetch_sql(cursor,
                                        session['pass'])
        if record == -1:
            print('Error in recommendMovies')
        else:
            col_names = [desc[0] for desc in cursor.description]
            log5 = record[:30]
        util.disconnect_from_db(connection, cursor)
        if request.method == 'POST':
                if request.form.get("logout"):
                    session['username'] = ''
                    return redirect(url_for('index'))
                if request.form.get("genrebutton"):
                    print(request.form.get("genrebutton"))
                    session['movieGenre'] = request.form.get("genrebutton")
                    cursor, connection = util.connect_to_db(username, password, host, port, database)
                    newGenre = "'%" + session['movieGenre'] + "%'"
                    record = util.run_and_fetch_sql(cursor,"Select title, startyear, genres from moviedata where genres like %s and startyear is not null order by startyear desc" % newGenre)
                    if record == -1:
                        print('Error in searchMovie')
                    else:
                        log = record[:30]
                    util.disconnect_from_db(connection, cursor)
                    return render_template('search2.html', sql_table=log)
                else:
                    session['movieName'] = request.form.get("searched")
                    cursor, connection = util.connect_to_db(username, password, host, port, database)
                    titleSearched = session['movieName']
                    newTitle = "'%" + titleSearched + "%'"
                    record = util.run_and_fetch_sql(cursor,
                                                    "Select title, startyear, genres from moviedata where ptitle like %s and startyear is not null order by startyear desc" % newTitle)
                    if record == -1:
                        print('Error in searchMovie')
                    else:
                        log = record[:30]
                    util.disconnect_from_db(connection, cursor)
                    return render_template('search2.html', sql_table=log)
        return render_template('recommendationsPage2.html', sql_table=log5, table_title=col_names)

#logic for the movie page, linked to search list pages
@app.route('/movie/<string:movie_id>', methods=["GET", 'POST'])
def userbook(movie_id):
    #adding to the user profile on click of add button
    if(session['username'] == ''):
        movie_id = "'" + str(movie_id) + "'"
        print(movie_id)
        cursor, connection = util.connect_to_db(username, password, host, port, database)
        record = util.run_and_fetch_sql(cursor, f"""Select title, startyear, genres, avgrating from moviedata where title = {movie_id};""")
        util.disconnect_from_db(connection, cursor)
        print(record)
        if record == -1:
            print('Error in userbookinfo')
        else:
            # col_names = [desc[0] for desc in cursor.description]
            # data0 is title, data[1] is year, data[2] is genres
            data = record[0]
            movietitle = data[0]
            urls = get_url(movietitle)
            print(urls)
            movie_poster = get_image(movietitle)
            print(movie_poster)
            # add if statement to check the size of the urls returned
            print(data)
        return render_template('moviePage.html', data=data, url_table=urls, poster=movie_poster)
    else:
        if request.method == 'POST':
            if request.form.get("logout"):
                session['username'] = ''
                return redirect(url_for('index'))
            if(request.form.get('movie_add')):
                moviename = request.form.get('movie_add')
                cursor, connection = util.connect_to_db(username, password, host, port, database)
                script = "update userinfo set favorites = favorites || '{" + moviename + "}' where username = " +  session['username'] + " ; commit;"
                util.runnerSQL(cursor, script)
                util.disconnect_from_db(connection, cursor)
            if(request.form.get('wishlist')):
                moviename = request.form.get('wishlist')
                cursor, connection = util.connect_to_db(username, password, host, port, database)
                script = "update userinfo set wishlist = wishlist || '{" + moviename + "}' where username = " +  session['username'] + " ; commit;"
                util.runnerSQL(cursor, script)
                util.disconnect_from_db(connection, cursor)
            if(request.form.get('movieHistory')):
                moviename = request.form.get('movieHistory')
                cursor, connection = util.connect_to_db(username, password, host, port, database)
                script = "update userinfo set watched = watched || '{" + moviename + "}' where username = " +  session['username'] + " ; commit;"
                util.runnerSQL(cursor, script)
                util.disconnect_from_db(connection, cursor)
            return  redirect(url_for('userPage'))
        movie_id = "'" + str(movie_id) + "'"
        print(movie_id)
        cursor, connection = util.connect_to_db(username, password, host, port, database)
        record = util.run_and_fetch_sql(cursor, f"""Select title, startyear, genres, avgrating from moviedata where title = {movie_id};""")
        util.disconnect_from_db(connection, cursor)
        print(record)
        if record == -1:
            print('Error in userbookinfo')
        else:
            # col_names = [desc[0] for desc in cursor.description]
            # data0 is title, data[1] is year, data[2] is genres
            data = record[0]
            movietitle = data[0]
            urls = get_url(movietitle)
            print(urls)
            movie_poster = get_image(movietitle)
            print(movie_poster)
            # add if statement to check the size of the urls returned
            print(data)
        return render_template('moviePage2.html', data=data, url_table=urls, poster=movie_poster)
    
#this is the function used to generate the list of movie recommendations for users. It is called when the user presses the update button on the user profile page.
#@app.route('/alg')
def recAlgorithm(userID):
    #need to grab the user's favorites list first
    #user = 'tester'
    cursor, connection = util.connect_to_db(username, password, host, port, database)
    record = util.run_and_fetch_sql(cursor, 'select favorites from userinfo where username = ' + userID)
    util.disconnect_from_db(connection, cursor)
    print(record)
    #prints out the favorites list up to this point.
    listofF = []
    for x in record:
        for y in x:
            for z in y:
                #grabs each element in the favorites list and stores in a new list; easy to access
                listofF.append(z)
    print(listofF)
    #pulling the genres for each movie id on the list of favorites
    listofG = []
    for x in listofF:
        cursor, connection = util.connect_to_db(username, password, host, port, database)
        record = util.run_and_fetch_sql(cursor, 'select genres from moviedata where title = ' + "'" + x + "'")
        util.disconnect_from_db(connection, cursor)
        #print(record)
        listofG.append(record)
    #complete list of genres, needs to be processed into usable format
    print(listofG)
    totalG = []
    for x in listofG:
        for y in x:
            for z in y:
                ls = z.split(',')
                for w in ls:
                    totalG.append(w)
    #totalG now holds all the genre tags from all the movies in the favorites list.
    print(totalG)
    #get the total number of tags
    numtags = len(totalG)
    gWeights = {}
    for x in totalG:
        if x in gWeights:
            num = gWeights[x]
            gWeights[x]= num + 1
        else:
            gWeights.update({x:1})
    #we now have each unique key(genre) and the number of tags(value) for each key
    print(gWeights)
    for k in gWeights:
        num = gWeights[k]
        gWeights[k] = num/numtags
    #top3 returns the top 3 genres by weight.
    top3 = sorted(gWeights, key=gWeights.get, reverse=True)[:3]
    print(gWeights)
    print(top3)
    cursor, connection = util.connect_to_db(username, password, host, port, database)
    record = util.run_and_fetch_sql(cursor, 'select title from moviedata where genres like ' + "'%"+ top3[0] + "%' and genres like " + "'%" + top3[1] + "%' and genres like " + "'%" + top3[2] + "%' order by avgrating desc")[:10]
    util.disconnect_from_db(connection, cursor)
    dbarray = "[ "
    for x in record:
        y = str(x)
        y = y[1:(len(y)-2)]
        print(y)
        dbarray = dbarray + y + ","
    # at this point, it returns the top 10 recommended movies based on genre and sorted by average rating.
    dbarray = dbarray[:-1] + "]"
    #print("update userinfo set recommendations = ARRAY " + str(dbarray) + " where username = " + user)
    cursor, connection = util.connect_to_db(username, password, host, port, database)
    util.runnerSQL(cursor, "update userinfo set recommendations = ARRAY " + dbarray + " where username = " + userID + "; COMMIT;")
    print('update to recommendation list successful')
    util.disconnect_from_db(connection, cursor)
    return

# Getting URL
#search term parameter is the movie name plus it's title ex: "avengers 2012"
def get_url(search_term):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome('chromedriver', chrome_options=options)
    template = 'https://www.google.com/search?q={}+stream'
    search_term = search_term.replace(' ', '+')
    # Generate a url from search term
    url = template.format(search_term)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    urls = []
    for h in soup.findAll('div', {'class': 'h0mQ3c'}):
        a = h.find('a')
        try:
            if 'href' in a.attrs:
                url = a.get('href')
                urls.append(url)
        except:
            pass

    for h in soup.findAll('div', {'class': 'fOYFme'}):
        a = h.find('a')
        try:
            if 'href' in a.attrs:
                url = a.get('href')
                urls.append(url)
        except:
            pass

    return urls[:5]


#This function handles getting the image displayed for the moviepage of a particular movie.
def get_image(search_term):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome('chromedriver', options=options)
    template = 'https://www.google.com/search?q={}+imdb+poster&source=lnms&tbm=isch'
    search_term = search_term.replace(' ', '+')
    # Generate a url from search term
    image_link = template.format(search_term)
    driver.get(image_link)
    #print(image_link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    result = soup.find('div', {'class': 'bRMDJf islir'})
    item = result
    tag = item.img
    return tag.get('src')

#Test to see if it prints src link
#print(get_image('avengers 2012'))



if __name__ == '__main__':
    # set debug mode
    app.debug = True
    app.secret_key = "banana"
    # your local machine ip
    ip = '127.0.0.1'
    app.run(host=ip)
