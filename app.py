from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from decouple import config


app = Flask(__name__)

# DB configuration
USER = config("DB_USER")
PASSWORD = config("DB_PASSWORD")
URL = config("DB_URL")
NAME = config("DB_NAME")
FULL_URL = f"postgresql://{USER}:{PASSWORD}@{URL}/{NAME}"

app.config["SQLALCHEMY_DATABASE_URI"] = FULL_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = config("SECRET_KEY")

#Init db
db = SQLAlchemy(app)

# Login config
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'danteaugsburger4@gmail.com'
app.config['MAIL_PASSWORD'] = config("EMAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


# Models
class Contact(db.Model):
    # __tablename__ = "contacts"
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    email = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, fullname, phone, email, user_id):
        self.fullname = fullname
        self.phone = phone
        self.email = email
        self.user_id = user_id

    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)


class User(db.Model, UserMixin):
    # __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(300))
    email = db.Column(db.String(100))
    contacts = db.relationship("Contact", backref="user", lazy="select")

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    else:
        return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        user = User.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password, password):
                if user.email == email:
                    login_user(user)
                    return redirect(url_for("home"))
                else:
                    flash("Wrong email")
                    return render_template("auth/login.html")
            else:
                flash("Wrong password")
                return render_template("auth/login.html")
        else:
            flash("Wrong username")
            return render_template("auth/login.html")

        return render_template("auth/login.html")
    else:
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        else:
            return render_template("auth/login.html")

@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]
            password2 = request.form["password2"]
            email = request.form["email"]

            user_username = User.query.filter_by(username=username).first()
            user_email = User.query.filter_by(email=email).first()

            if user_username:
                flash("Username already exist")
            else:
                if user_email:
                    flash("Email already used")
                else:
                    if password != password2:
                        flash("Passwords do not match")
                    else:
                        hashed_password = generate_password_hash(password)
                        user = User(username, hashed_password, email)

                        db.session.add(user)
                        db.session.commit()

                        login_user(user)

                        return redirect(url_for("home"))
        except Exception as e:
            return str(e)

    return render_template("auth/sign_up.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/home")
@login_required
def home():
    return render_template("home.html")

@app.route("/add_contact", methods=["GET", "POST"])
def add_contact():
    if request.method == "POST":
        fullname = request.form["fullname"]
        phone = request.form["phone"]
        email = request.form["email"]

        contact = Contact(fullname, phone, email, current_user.id)

        db.session.add(contact)
        db.session.commit()

        flash("Contact added successfully")

        return redirect(url_for("home"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    contact = Contact.query.get_or_404(id)
    if request.method == "POST":
        contact.fullname = request.form["fullname"]
        contact.phone = request.form["phone"]
        contact.email = request.form["email"]
        contact.user_id = current_user.id

        db.session.commit()

        flash("Contact updated successfully")

        return redirect(url_for("home"))

    return render_template("auth/edit.html", contact=contact)

@app.route("/delete/<int:id>")
def delete(id):
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    flash("Contact removed successfully")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)