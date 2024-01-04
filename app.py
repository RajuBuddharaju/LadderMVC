from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employeeAndUser.db'
# Initialize the database
db = SQLAlchemy(app)

# Create db model
class ME(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   password = db.Column(db.String(200))
   activeUEID = db.Column(db.Integer)
   
   # Creae a fucntion to return a string when we add something
   def __repr__(self):
      return '<Name %r>' % self.id

# Create db model
class UE(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   meID = db.Column(db.Integer, foreign_key=True)
   dataValue1 = db.Column(db.String(64))
   dataValue2 = db.Column(db.String(64))
   dataValue3 = db.Column(db.String(64))
   dataValue4 = db.Column(db.String(64))
   date_created = db.Column(db.DateTime, default=datetime.utcnow)
   name = db.Column(db.String(200))
   
   # Creae a fucntion to return a string when we add something
   def __repr__(self):
      return '<Name %r>' % self.id



@app.route('/', methods=['POST', 'GET'])
def index():
    title = "The Ladder"
    if request.method == "POST":
        user_name = request.form['name']
        user_id = random.randint(100000,999999)
        new_user = UE(name=user_name, id=user_id, meID=1)

        # Push to Database
        try:
           db.session.add(new_user)
           db.session.commit()
           return redirect('/')
        except Exception as e:
           return "There was an error adding your user: " + str(e)
    else:
        users = UE.query.order_by(UE.date_created)
        return render_template("index.html", title=title, users=users)

@app.route('/login', methods=['POST', 'GET'])
def login():
   title = "Login"
   if request.method == "POST":
      user_id = request.form['id']
      user_password = request.form['password']
      user = ME.query.filter_by(id=user_id).first()
      if user is None:
         return redirect('/login')
      elif user.password == user_password:
         return redirect('/dashboard')
      else:
         return redirect('/login')
   else:
      return render_template("login.html", title=title)
   
@app.route('/dashboard')
def dashboard():
   title = "Dashboard"
   return render_template("dashboard.html", title=title)

@app.route('/about')
def about():
   title = "About The Ladder"
   return render_template("about.html", title=title)

@app.route('/contact')
def contact():
   title = "Contact Us"
   return render_template("contact.html", title=title)

@app.route('/form', methods=["POST"])
def form():
   email = request.form.get("email_id")
   question = request.form.get("query_question")
   title = "Thank You!!!"
   return render_template("form.html", title=title, email=email, question=question)