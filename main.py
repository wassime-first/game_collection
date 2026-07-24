from flask import Flask, request, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from dotenv import load_dotenv
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user, LoginManager
import dbb
import os
import api
from rapidfuzz.process import extractOne

# creating flask app

load_dotenv()
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


# flask form for loging

class SinghUpForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class LogInForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

# loging manager

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# loading the manager

@login_manager.user_loader
def load_user(user_id):
    return dbb.session.get(dbb.User,int(user_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LogInForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = dbb.session.query(dbb.User).filter_by(email=email).first()
        if user:
            hashed_password = user.password
            if check_password_hash(hashed_password, password):
                login_user(user, remember=True)
                flash("You are now logged in!", category="secondary")
                return redirect("/")
            else:
                flash("Incorrect password!", category="danger")
                return render_template("login.html", form=form)
        else:
            return redirect(url_for("signup"))

    return render_template("login.html", form=form, title="Login")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SinghUpForm()

    if form.validate_on_submit():

        username = form.username.data
        email = form.email.data
        password = form.password.data
        all_emails = dbb.session.query(dbb.User).all()
        for m in all_emails:
            if m.email == email:
                flash("Email already registered!", category="danger")
                return redirect(url_for("login"))

        else:
            user = dbb.User(email=email, password=generate_password_hash(password), name=username)
            dbb.session.add(user)
            dbb.session.commit()
            login_user(user, remember=True)
            flash("Account created and logged in!", category="secondary")
            return redirect("/")

    return render_template("login.html", form=form, title="Sign Up")

@app.route("/logout")
def logout():
    logout_user()
    flash("You are now logged out!", category="secondary")
    return redirect("/")


@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    page = request.args.get("page", default=1, type=int)
    search = request.args.get("search", default="-rating", type=str)
    games = api.all_games(page, search)
    user_games_id = [game.id for game in current_user.games]
    last_page = (min(page + 8, games[1]))
    current_pages = range(page, last_page + 1)

    form_search = request.form.get("search")
    action_url = url_for('search', search=form_search)
    pagination_url = 'home'

    return render_template("main.html", games=games[0],
                           page=page,
                           search=search,
                           current_pages=current_pages,
                           user_games_id=user_games_id,
                           action_url=action_url,
                           pagination_url=pagination_url)


@app.route("/collection", methods=["GET", "POST"])
@login_required
def collection():
    if request.method == "POST":

        search = request.form.get("search")
        all_games_names = [game.name for game in current_user.games]

        result = extractOne(search, all_games_names, score_cutoff=50)
        if result:
            games = [game for game in current_user.games if game.name in result]
            action_url = (url_for('collection'))
            return render_template("collection.html",
                                   games=games,
                                   action_url=action_url)
        else:
            return redirect(url_for("collection"))

    else:
        games = current_user.games
        action_url = (url_for('collection'))
        return render_template("collection.html",
                               games=games,
                               action_url=action_url)


@app.route("/details")
@login_required
def details():
    id = request.args.get("id")
    game_detail = api.game_detail(id)
    search = request.form.get("search")
    game_screenshots = api.game_screenshot(id)
    action_url = (url_for('search', page=1, search=search))
    return render_template("details.html",
                           game=game_detail,
                           screenshots=game_screenshots,
                           action_url=action_url
                           )


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        search = request.form.get("search")
        page = request.args.get("page", default=1, type=int)
        return redirect(url_for("search", page=page, search=search))

    else:
        search = request.args.get("search")
        page = request.args.get("page", default=1, type=int)
        games = api.search_games(search, page)
        user_games_id = [game.id for game in current_user.games]
        last_page = (min(page + 8, games[1]))
        current_pages = range(page, last_page + 1)

    action_url = (url_for('search', search=search))
    pagination_url = 'search'

    return render_template("search.html",
                           games=games[0],
                           user_games_id=user_games_id,
                           page=page,
                           current_pages=current_pages,
                           max_pages=games[1],
                           search=search,
                           action_url=action_url,
                           pagination_url=pagination_url)


@app.route("/add")
@login_required
def add():
    id = int(request.args.get("id"))
    game = api.game_detail(id)
    screenshot = api.game_screenshot(id)
    existing = False
    for g in current_user.games:
        if g.id == id:
            existing = True
            break
    if existing:
        flash("This game already exists!", category="danger")
        return redirect(request.referrer)
    else:
        if not dbb.session.query(dbb.Game).filter_by(id=id).first():
            newGame = dbb.Game(id=id,
                               name=game[0],
                               metacritic=game[1] if game[1] is not None else 00,
                               rating=game[2],
                               background=game[3],
                               release_date=game[4] or "Unknown",
                               publishers=game[5],
                               description=game[6],
                               genre=game[7],
                               screenshots=screenshot
                               )
            try:
                current_user.games.append(newGame)
                dbb.session.add(newGame)
                dbb.session.commit()
                flash(f"Added {game[0]} successfully", category="secondary")
            except dbb.IntegrityError:
                flash("Game already exists!", category="danger")
                dbb.session.rollback()

        else:
            game = dbb.session.query(dbb.Game).filter_by(id=id).first()
            try:
                current_user.games.append(game)
                dbb.session.commit()
                flash(f"Added {game.name} successfully!", category="secondary")
            except dbb.IntegrityError:
                dbb.session.rollback()

    return redirect(request.referrer)


@app.route("/delete")
@login_required
def delete():
    id = request.args.get("id")
    game = None
    for g in current_user.games:
        if g.id == int(id):
            game = g
            break
    if game:
        current_user.games.remove(game)
        dbb.session.commit()
        flash(f"Deleted {game.name} successfully!", category="danger")
    return redirect(request.referrer)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)
