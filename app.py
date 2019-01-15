import os #stdlib

from flask import Flask, render_template, session, redirect, request, flash, url_for #pip install flask

from util import database, googleCivicInfo, news_api, fortune
from util import session as user

import pprint

app = Flask(__name__)
app.secret_key = os.urandom(32)


@app.route('/') #####
def home():
    #print(news_api.nyt_news("W"))
    #pp = pprint.PrettyPrinter(indent=4)
    civic_list = googleCivicInfo.civic(10282)
    # news_list = []
    if 'follow' in request.args:
        database.follow(session['id'], request.args['follow'])
        flash('You have successfully followed ' + request.args['follow'], 'success')
    if 'unfollow' in request.args:
        database.unfollow(session['id'], request.args['unfollow'])
        flash('You have successfully unfollowed ' + request.args['unfollow'], 'success')
    quote = fortune.getQuote()
    followed = []
    if 'id' in session:
        data = database.get_followed(session['id'])
        for row in data:
            followed.append(row[0])
    #print(civic_list)
    return render_template("index.html", s = session, l = civic_list, c = len(civic_list), q = quote, f = followed)

@app.route("/search", methods=["GET"])
def search():
    '''redirects search appropriately based on what was searched for'''
    zip = str(request.args.get('search'))
    if (len(zip) == 5):
        return redirect("politicians/" + zip)
    else:

        flash('Please insert a valid zip code', 'danger')
        return redirect('/')

@app.route("/politicians/<int:zip>")
def politicians(zip):
    civic_list = googleCivicInfo.civic(zip)
    news_list = []
    if civic_list == "error":
        print ("nope. error on google api")
        flash("Invalid search query!", 'danger')
        return redirect( url_for('home') )
    return render_template("index.html", s = session, l = civic_list, c = len(civic_list), nl = news_list)

@app.route("/politicianpage/<name>")
def politicianpage(name):
    artNYT = news_api.nyt_news(name)
    artNews = news_api.news_api(name)

    if len(artNYT) > 5:
        lenNYT = 5
    else:
        lenNYT = len(artNYT)

    if len(artNews) > 5:
        lenNews = 5
    else:
        lenNews = len(artNews)

    topArtNYT = artNYT[0 : lenNYT]
    topArtNews = artNews[0 : lenNews]

    print ('\n\n\n' + str(topArtNYT) + '\n\n\n')
    print ('\n\n\n' + str(topArtNews) + '\n\n\n')

    return render_template('politician.html', name=name , articles_nyt = topArtNYT , articles_news = topArtNews )

@app.route("/login", methods=['GET'])
def login():
    '''Redirects to the homepage if the user is logged in. Displays the login page if the user is not logged in.'''
    if (user.is_logged_in()):
        return redirect(url_for("home"))

    # flash("Please log in before following a politician!", 'danger')

    return render_template("login.html")

@app.route("/register")
def register():
    '''Display the register page.'''
    if (user.is_logged_in()):
        redirect(url_for("home"))
    return render_template("register.html", isLoggedIn = user.is_logged_in())

@app.route("/auth", methods=["POST"])
def authenticate():
    '''Handles the information that the user submits for either logging in or
    registering. It will redirect the user to the appropriate pages and flash
    messages if there are errors.'''
    submit_type = request.form.get("submit")
    username_list = database.get_username_list()
    msg = ''
    type = 'primary'
    if (submit_type == "Register"):
        username_input = request.form.get("username")
        password_input = request.form.get("password")
        c_password_input = request.form.get("confirm_password")
        if (len(username_input.replace(" ","")) < 4):
            flash('Username has to be at least 4 characters long.', 'danger')
        elif (len(password_input.replace(" ","")) < 4):
            flash('Password has to be at least 4 characters long.', 'danger')
        elif username_input in username_list:
            flash('Username already exists. Please try a different username.', 'danger')
        #check that password confirm
        elif (password_input != c_password_input):
            flash('Password and Confirm Password do not match.', 'danger')
        else:
            database.add_user(username_input,password_input)
            flash('Successfully created account.', 'success')
            return redirect(url_for("login"))
        return render_template("register.html", m = msg, t = type)
    elif (submit_type == "Login"):
        username_input = request.form.get("username")
        password_input = request.form.get("password")
        if (username_input in username_list):
            if (database.authenticate(username_input,password_input)):
                flash('Successfully logged in.', 'success')
                session["id"] = database.getIDFromUsername(username_input)
                return redirect(url_for("home"))
        msg = "Username or password is incorrect. Please try again."
        type = 'danger'
        return render_template("login.html")
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    '''Removes the current session and redirects users back to login page.'''
    session.pop("id")
    flash('Successfully logged out.', 'success')
    return redirect('/')

if __name__ == '__main__':
    app.debug = True #set to False in production mode
    database.setup()
    app.run()
