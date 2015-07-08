from flask import (Flask, redirect, render_template, request)
from flask_login import (login_required, current_user, logout_user, login_user)
from bson import ObjectId
from pymongo import MongoClient
import login_system
import random

app = Flask(__name__)

DATABASE_NAME = 'summertime_webness'

USERS = 'users'
QUESTIONS = 'questions'
MATCHES = 'matches'

@app.route("/")
def index():
    return render_template("index.html")


################################## MATCHES ####################################################

@app.route("/matches", methods=['GET', 'POST'])
@login_required
def mathes_handler():
    if request.method == 'GET':
        filter_options = {}
        filter_options['players'] = {'$in': [current_user.data["_id"]]}
        invitations = list(app.db[MATCHES].find(filter_options))

        return render_template("matches.html", invitations=invitations)
    elif request.method == 'POST':
        opponent = request.form.get('opponent', '')
        all_questions = list(app.db[QUESTIONS].find())
        selected_question = random.sample(all_questions, 5)

        new_match = {
            'players': [current_user.data['_id'], ObjectId(opponent)],
            'players_names': [current_user.data['name'], opponent],
            'questions': selected_question,
            'status': 'open',
            'results': {}
        }
        app.db[MATCHES].insert(new_match)
        return redirect("/matches/%s" % new_match['_id'])


@app.route("/matches/<match_id>", methods=['GET', 'POST'])
@login_required
def match_handler(match_id):
    if request.method == 'GET':
        match = app.db[MATCHES].find_one(ObjectId(match_id))
        users = dict([(str(user['_id']), user) for user in app.db[USERS].find({'_id': {'$in': match['players']}})])
        return render_template(
            "match.html",
            match=match,
            cur_user = str(current_user.data['_id']),
            players = users
        )

    if request.method == 'POST':
        cur_user = str(current_user.data["_id"])
        match = app.db[MATCHES].find_one(ObjectId(match_id))
        answers = request.form.get('answers', '')
        answers = answers.split(',')
        match['results'][cur_user] = {"answers": answers}
        score = 0
        for answer, question in zip(answers, match['questions']):
            if answer == question['correct_answer']:
                score = score + 1
        match['results'][cur_user]["score"] = score
        if len(match['results']) == 2:
            match['status'] = "closed"
        app.db[MATCHES].save(match)
        return redirect("/matches/%s" % match_id)

################################### USERS #####################################################

@app.route("/users/add")
@login_required
def add_user_page():
    return render_template("add_user.html")


@app.route("/users", methods=['GET', 'POST'])
def users_handler():
    if request.method == 'GET':
        users = app.db['users'].find()
        return render_template("users.html", users=users)
    elif request.method == 'POST':
        name = request.form.get('name', '')
        full_name = request.form.get('full_name', '')
        skills = request.form.get('skills', '')
        position = request.form.get('position', '')
        photo = request.form.get('photo', '')
        password = request.form.get('password', '')
        new_user = {
            'name': name,
            'full_name': full_name,
            "skills": skills,
            "position": position,
            "photo": photo,
            'password': password,
        }
        app.db['users'].insert(new_user)
        return redirect("/users/%s" % name)
    else:
        raise RuntimeError("Only POST and GET methods are supported")


@app.route("/users/<user_name>/edit")
@login_required
def edit_user(user_name):
    user = app.db['users'].find({'name': user_name}).limit(1)[0]
    return render_template("edit_user.html", user=user)


################################### LOGIN SYSTEM ##############################################

@app.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        next_page = request.args.get('next', '/')
        return render_template("login.html", next_page=next_page)
    else:
        user_name = request.form.get('name' ,'')
        password = request.form.get('password', '')
        next_page = request.form.get('next_page', '/')
        # Get user from DB
        users = list(app.db['users'].find({'name': user_name}).limit(1))
        # Did we find anyone in DB?
        if not users:
            return render_template("login.html", error=True)
        # Lets take the first one
        user = users[0]
        # check password
        if user and password == user.get('password', ''):
            # if password is correct, login user
            login_user(login_system.load_user(user_name))
            return redirect(next_page)
        else:
            # if password is not correct, return error page
            return render_template("login.html", error=True)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


if __name__ == "__main__":
    app.db = MongoClient('wardoctor.nosoc.io', port=443)[DATABASE_NAME]
    login_system.init_login_system(app)
    app.run(debug=True)