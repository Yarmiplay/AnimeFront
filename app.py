from flask import Flask, request, render_template, redirect, url_for, session, abort, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from sqlalchemy import CheckConstraint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.secret_key = 'benny_yarmolovich'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, unique=False, nullable=False)
    is_admin = db.Column(db.Boolean, unique=False, nullable=False)

    __table_args__ = (db.UniqueConstraint("username", name="unique_username"),)

    def __str__(self):
        return f"Username: {self.username}, ID: {self.id}"
    
class Anime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=False, nullable=False)
    image_link = db.Column(db.String, unique=False, nullable=False)
    desc = db.Column(db.String, unique=False, nullable=False)
    studio = db.Column(db.String, unique=False, nullable=False)
    release_year = db.Column(db.Integer, unique=False, nullable=False)
    characters = db.Column(db.String, unique=False, nullable=False)

    user_reviews = relationship('UserReview', backref='anime', lazy=True)

    def __str__(self):
        return f"Title: {self.title}, ID: {self.id}"
    
    @property
    def average_stars(self):
        if self.user_reviews:
            total_stars = sum(review.stars for review in self.user_reviews)
            total_reviews = len(self.user_reviews)
            average_rating = total_stars / total_reviews if total_reviews else 0.0
            return round(average_rating, 2)
        else:
            return "0"

class UserReview(db.Model):
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    review = db.Column(db.String, nullable=False)
    stars = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref='reviews')

    __table_args__ = (
        CheckConstraint('stars >= 1 AND stars <= 10', name='check_stars_range'),
    )


@app.route("/", methods=["POST", "GET"])
def homepage():
    user = session.get('user')
    is_admin = session.get('is_admin')
    anime_list = Anime.query.all()

    if search_query := request.args.get('search'):
        # Filter anime by name containing the search query
        anime_list = [anime for anime in Anime.query.all() if search_query.lower() in anime.title.lower()]
        if not anime_list:
            abort(404)

    return render_template('homepage.html', user=user, is_admin=is_admin, anime_list=anime_list)

@app.route("/login/", methods=["POST", "GET"])
def login():
    user = session.get('user')
    is_admin = session.get('is_admin')
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # Authentication successful
            session['user'] = user.username
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            return redirect(url_for('homepage'))
        else:
            return render_template("login.html", user=user, is_admin=is_admin, login_failed=True)
    else:
        return render_template("login.html", user=user, is_admin=is_admin, login_failed=False)
    
@app.route("/signup/", methods=["POST", "GET"])
def signup():
    user = session.get('user')
    is_admin = session.get('is_admin')
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        profile = User(username=username, password=password, is_admin=False)
        if User.query.filter_by(username=username).first():
            render_template("signup.html", user=user, is_admin=is_admin, user_exists_error=True)
        try: 
            db.session.add(profile) # Should fail if unique constraint exists on User, but I failed to get it to work
            db.session.commit()
            # Also log in as this user right away
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                # Authentication successful
                session['user'] = user.username
                session['user_id'] = user.id
                session['is_admin'] = user.is_admin
                return redirect(url_for('homepage'))
        except IntegrityError as e:
            db.session.rollback()  # Rollback the transaction
            return render_template("signup.html", user=user, is_admin=is_admin, user_exists_error=True)
    else:
        return render_template("signup.html", user=user, is_admin=is_admin, user_exists_error=False)

@app.route('/logout')
def logout():
    # Clear the user's session
    session.pop('user', None)
    return redirect(url_for('homepage'))

@app.route('/anime/<int:anime_id>')
def anime_details(anime_id):
    user = session.get('user')
    user_id = session.get('user_id')
    is_admin = session.get('is_admin')
    existing_review = UserReview.query.filter_by(anime_id=anime_id, user_id=user_id).first()
    anime = Anime.query.get(anime_id)
    if anime:
        return render_template('anime_details.html', user=user, is_admin=is_admin, anime=anime, existing_review=existing_review)
    else:
        abort(404) # Anime id not found

@app.route('/review/<int:anime_id>', methods=["POST", "GET"])
def review(anime_id):
    user = session.get('user')
    user_id = session.get('user_id')
    is_admin = session.get('is_admin')
    anime = Anime.query.get(anime_id)
    if request.method == "POST":
        if not user:
            abort(403)
        if not anime:
            abort(404)

        review_text = request.form.get('review_text')
        star_rating = int(request.form.get('star_rating'))
        if star_rating > 10 or star_rating < 1:
            abort(400)

        existing_review = UserReview.query.filter_by(anime_id=anime_id, user_id=user_id).first()
        if existing_review:
            # Update existing review
            existing_review.review = review_text
            existing_review.stars = star_rating
        else:
            # Create a new review
            new_review = UserReview(anime_id=anime_id, user_id=user_id, review=review_text, stars=star_rating)
            db.session.add(new_review)
        db.session.commit()
        return redirect(url_for('anime_details', anime_id=anime_id))
    else:
        if anime and user:
            existing_review = UserReview.query.filter_by(anime_id=anime_id, user_id=user_id).first()
            return render_template('review_anime.html', user=user, is_admin=is_admin, anime=anime, existing_review=existing_review)
        elif not user:
            abort(403)
        else:
            abort(404)

@app.route('/add_anime', methods=['GET', 'POST'])
def add_anime():
    user = session.get('user')
    is_admin = session.get('is_admin')
    if not user or not User.query.filter_by(username=user, is_admin=True).first():
        abort(403)  # Forbidden access

    if request.method == 'POST':
        # Process form data and add the new anime to the database
        title = request.form.get('title')
        image_link = request.form.get('image_link')
        desc = request.form.get('desc')
        studio = request.form.get('studio')
        release_year = int(request.form.get('release_year'))
        characters = request.form.get('characters')

        # Create a new Anime instance with form data
        new_anime = Anime(
            title=title,
            image_link=image_link,
            desc=desc,
            studio=studio,
            release_year=release_year,
            characters=characters
        )

        # Add the new anime to the database
        db.session.add(new_anime)
        db.session.commit()
        return redirect(url_for('homepage'))

    return render_template('add_anime.html', user=user, is_admin=is_admin)

@app.errorhandler(404)
def page_not_found(error):
    user = session.get('user')
    is_admin = session.get('is_admin')
    error_code = '404 Not Found'
    error_message = 'The requested anime could not be found.'
    return render_template('error.html', user=user, is_admin=is_admin, error_code=error_code, error_message=error_message), 404

@app.errorhandler(403)
def forbidden_error(error):
    user = session.get('user')
    is_admin = session.get('is_admin')
    error_code = '403 Forbidden'
    error_message = "Sorry, you don't have permission to access this page."
    return render_template('error.html', user=user, is_admin=is_admin, error_code=error_code, error_message=error_message), 403

@app.errorhandler(400)
def bad_request(error):
    user = session.get('user')
    is_admin = session.get('is_admin')
    error_code = '400 Bad request'
    error_message = "Sorry, something about that request caused an issue."
    return render_template('error.html', user=user, is_admin=is_admin, error_code=error_code, error_message=error_message), 400

if __name__ == "__main__":
    app.run(debug=True)