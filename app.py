from flask import Flask, render_template, url_for, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/trade'
app.secret_key = "sdhferh9aerht458tyfhertg485trhg"
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    acc_holder = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    balance = db.Column(db.Integer, nullable=False)

class News(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    posted_by = db.Column(db.String, nullable=False)


@app.route('/')
def index():
    return render_template("index.html")

@app.route("/news") # News posted by the users to be displayed here. Create another route for posting news.
def news():
    news = News.query.order_by(News.sno.desc()).all()
    return render_template("news.html", news=news)

@app.route("/news/post", methods=["GET", "POST"])
def addNews(): # The logged in user can post news to be stored in the database.
    if "user_id" in session and request.method=="POST":
        user_id = session["user_id"]  # Get the user id from the session.
        title = request.form.get("title")
        content = request.form.get("content")
        user = Users.query.get(user_id)
        print(user.acc_holder)
        if user:
            new_news = News(title=title, content=content, posted_by=user.acc_holder)
            db.session.add(new_news)
            db.session.commit()
            return redirect(url_for("news"))
        return redirect(url_for("index"))
    return render_template("postNews.html")
    
@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        acc_holder = request.form.get("acc_holder")
        password = request.form.get("password")
        user = Users.query.filter_by(acc_holder=acc_holder).first()
        if not user:
            new_user = Users(acc_holder=acc_holder, password=password, balance=10)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
        else:
            return render_template("signup.html", error="Account already exists")
    return render_template("signup.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        acc_holder = request.form.get("acc_holder")
        password = request.form.get("password")
        user = Users.query.filter_by(acc_holder=acc_holder, password=password).first()
        if user:
            session["user_id"] = user.id
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))

@app.route("/profile")
def profile():
    if "user_id" in session:
        user_id = session["user_id"]
        user = Users.query.get(user_id)
        balance = user.balance
        return render_template("profile.html", user=user, balance=balance)
    else:
        return redirect(url_for("login"))
    
@app.route("/changepassword", methods=["GET", "POST"])
def changepassword():
    if request.method == "POST":
        user_id = session["user_id"]
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        user = Users.query.get(user_id)
        if user.password == old_password:
            user.password = new_password
            db.session.commit()
            return redirect(url_for("profile"))
        else:
            return render_template("changepassword.html", error="Incorrect old password")
    return render_template("changepassword.html")

@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    if request.method == "POST":
        user_id = session["user_id"]
        recipient_acc_holder = request.form.get("recipient_acc_holder")
        amount = int(request.form.get("amount"))
        user = Users.query.get(user_id)
        recipient = Users.query.filter_by(acc_holder=recipient_acc_holder).first()
        if recipient and user.balance >= amount:
            user.balance -= amount
            recipient.balance += amount
            db.session.commit()
            return redirect(url_for("profile"))
        else:
            return render_template("transfer.html", error="Invalid recipient or insufficient funds")
    return render_template("transfer.html")

