from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbExample.db'
# Initialize the database
db = SQLAlchemy(app)

# Create db model
class MEID(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   password = db.Column(db.String(200))
   activeUEID = db.Column(db.Integer)
   
   # Creae a fucntion to return a string when we add something
   def __repr__(self):
      return '<Name %r>' % self.id

# Create db model
class UEID(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   meID = db.Column(db.Integer)
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
      print(user_id)
      user_password = request.form['password']
      print(user_password)
      #user = MEID.query.filter_by(id=user_id).first()
      #print(user)
      #print(user.password)
      conn = sqlite3.connect('instance/dbExample.db')
      cursor = conn.cursor()
      raju_is_a_dumbass = cursor.execute("SELECT * FROM MEID WHERE id=?", (user_id,))
      result = raju_is_a_dumbass.fetchone()
      print(result)
      if result is None:
         print("User does not exist")
         return redirect('/login')
      elif result[1] == user_password:
         print("pp")
         return redirect(url_for('dashboard', me_id=result[0]))
      else:
         print("Incorrect Password")
         return redirect('/login')
   else:
      return render_template("login.html", title=title)
   
@app.route('/dashboard')
def dashboard():
   title = "Dashboard"
   me_id = request.args.get('me_id')  # Assuming the MEID is passed as a query parameter
   me = MEID.query.filter_by(id=me_id).first()
   if not me:
      return redirect('/login')
   ue_list = UEID.query.filter_by(meID=me_id).all()
   return render_template("dashboard.html", title=title, me=me, ue_list=ue_list)

@app.route('/update_ueids', methods=['POST'])
def update_ueids():
    me_id = request.form.get('meid')
    if not me_id:
        flash('No MEID provided.', 'error')
        return redirect(url_for('login'))

    # Retrieve all UEIDs for the given MEID
    ue_list = UEID.query.filter_by(meID=me_id).all()
    ue_ids = [ue.id for ue in ue_list]

    try:
        for ue_id in ue_ids:
            # Get the new data values from the form
            data_value_1 = request.form.get(f'dataValue1_{ue_id}')
            data_value_2 = request.form.get(f'dataValue2_{ue_id}')
            data_value_3 = request.form.get(f'dataValue3_{ue_id}')
            data_value_4 = request.form.get(f'dataValue4_{ue_id}')

            # Retrieve the UE object from the database
            ue = UEID.query.get(ue_id)
            if ue:
                # Update the UE object with new data values
                ue.dataValue1 = data_value_1
                ue.dataValue2 = data_value_2
                ue.dataValue3 = data_value_3
                ue.dataValue4 = data_value_4
                db.session.commit()
    except Exception as e:
        db.session.rollback()

    return redirect(url_for('dashboard', me_id=me_id))
 
 
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

if __name__ == "__main__":
    app.run(debug=True, port=6922)