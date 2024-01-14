from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
from datetime import datetime, timedelta
import sqlite3
import random

app = Flask(__name__)
app.secret_key = b'\x12\xfbF\xf3\xc5\xa6\x9e\xc6\xa8\x11\xdf\x9e\x95\xf1\xa1\x8f\xe6K\x89u7\x18\x19\x8f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbExample.db'

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Set the session to expire after 30 minutes of inactivity
app.permanent_session_lifetime = timedelta(minutes=30)

# Create db model for Municipality Employees
class MEID(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   password = db.Column(db.String(200))
   activeUEID = db.Column(db.Integer)
   name = db.Column(db.String(200))
   
   # Creae a fucntion to return a string when we add something
   def __repr__(self):
      return '<Name %r>' % self.id

# Create db model for Users
class UEID(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   meID = db.Column(db.Integer)
   date_created = db.Column(db.DateTime, default=datetime.utcnow)
   name = db.Column(db.String(200))

   # Foreign keys for goals
   goal1_id = db.Column(db.Integer, db.ForeignKey('goal.id'))
   goal2_id = db.Column(db.Integer, db.ForeignKey('goal.id'))
   goal3_id = db.Column(db.Integer, db.ForeignKey('goal.id'))
   goal4_id = db.Column(db.Integer, db.ForeignKey('goal.id'))

    # Relationships to Goal model
   goal1 = db.relationship('Goal', foreign_keys=[goal1_id])
   goal2 = db.relationship('Goal', foreign_keys=[goal2_id])
   goal3 = db.relationship('Goal', foreign_keys=[goal3_id])
   goal4 = db.relationship('Goal', foreign_keys=[goal4_id])
   
   # Creae a fucntion to return a string when we add something
   def __repr__(self):
      return '<Name %r>' % self.id

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_value = db.Column(db.String(64))  # This might represent a goal title or category
    progress = db.Column(db.Integer)  # Progress as an integer (1 to 3)
    description = db.Column(db.String(200))  # Description of the goal

    def __repr__(self):
        return '<Goal %r>' % self.id


@app.before_request
def before_request():
    if not session.get('meid') and request.endpoint not in ['login', 'static']:
        flash('Your session has expired. Please log in again.', 'info')
        return redirect(url_for('login'))

# Redirect root to the login page
@app.route('/')
def root():
    return redirect(url_for('login'))

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
         session.permanent = True
         session['meid'] = result[0]
         return redirect(url_for('dashboard', me_id=result[0]))
      else:
         print("Incorrect Password")
         return redirect('/login')
   else:
      return render_template("login.html", title=title)
   
@app.route('/dashboard')
def dashboard():
   print(request.endpoint)
   title = "Dashboard"
   me_id = request.args.get('me_id') or session.get('meid')
   if not me_id:
       return redirect(url_for('login'))
   
   me = MEID.query.filter_by(id=me_id).first()
   if not me or not me.activeUEID:
       flash('No active UEID found.', 'error')
       return redirect(url_for('login'))

   active_ue = UEID.query.get(me.activeUEID)
   if not active_ue:
       flash('Active UEID not found.', 'error')
       return redirect(url_for('login'))

   return render_template("dashboard.html", title=title, active_ue=active_ue, me=me)

@app.route('/edit_goal', methods=['GET', 'POST'])
def edit_goal():
    ueid = request.form.get('ueid');
    if not ueid:
        print('No UEID provided.')
        return redirect(url_for('dashboard'))
    
    ue = UEID.query.get(ueid)
    
    if request.method == 'POST':
        goalNumber = request.form.get('goalNumber')
        if not goalNumber:
            print('No goal number provided.')
            return redirect(url_for('dashboard'))
        
        # Retrieve form data]
        if goalNumber == '1':
                print('Updating goal 1')
                ue.goal1.data_value = request.form.get('goal_name')
                ue.goal1.progress = request.form.get('goal_progress')
                ue.goal1.description = request.form.get('goal_detail')
        elif goalNumber == '2':
                ue.goal2.data_value = request.form.get('goal_name')
                ue.goal2.progress = request.form.get('goal_progress')
                ue.goal2.description = request.form.get('goal_detail')
        elif goalNumber == '3':
                ue.goal3.data_value = request.form.get('goal_name')
                ue.goal3.progress = request.form.get('goal_progress')
                ue.goal3.description = request.form.get('goal_detail')
        elif goalNumber == '4':
                ue.goal4.data_value = request.form.get('goal_name')
                ue.goal4.progress = request.form.get('goal_progress')
                ue.goal4.description = request.form.get('goal_detail')

        db.session.commit()
        print('Goal updated successfully!')
        return redirect(url_for('dashboard'))

    return render_template('dashboard.html', ueid=ueid)

@app.route('/clients_overview')
def clients_overview():
   title = "Clients Overview"
   me_id = request.args.get('me_id')  # Assuming the MEID is passed as a query parameter
   me = MEID.query.filter_by(id=me_id).first()
   if not me:
      return redirect('/login')
   
   ue_list = UEID.query.filter_by(meID=me_id).all()

   return render_template("clients_overview.html", title=title, me=me, ue_list=ue_list)

@app.route('/update_ueids', methods=['POST'])
def update_ueids():
    me_id = request.form.get('meid')
    if not me_id:
        return redirect(url_for('login'))

    # Retrieve the ME object for the given MEID
    me = MEID.query.get(me_id)
    if not me:
        return redirect(url_for('login'))

    # Check if we're setting a new active UEID
    new_active_ueid = request.form.get('activeUEID')
    if new_active_ueid:
        me.activeUEID = new_active_ueid
        db.session.commit()

    # Retrieve all UEIDs for the given MEID
    ue_list = UEID.query.filter_by(meID=me_id).all()
    ue_ids = [ue.id for ue in ue_list]

    try:
        # Update data values for UEIDs
        for ue_id in ue_ids:
            # If deleting a UEID
            if request.form.get('delete_ueid') == str(ue_id):
                ue = UEID.query.get(ue_id)
                if ue:
                    # Check if the UEID to delete is the active UEID for the ME
                    if me.activeUEID == ue_id:
                        me.activeUEID = None  # Reset the activeUEID

                    db.session.delete(ue)
                    db.session.delete(ue.goal1)
                    db.session.delete(ue.goal2)
                    db.session.delete(ue.goal3)
                    db.session.delete(ue.goal4)
                    continue  # Skip the rest of the loop for this UEID


            # Retrieve the UE object from the database
            ue = UEID.query.get(ue_id)
            if ue:
                # Update the UE object with new data values
                ue.goal1.data_value = request.form.get(f'dataValue1_{ue_id}')
                ue.goal2.data_value = request.form.get(f'dataValue2_{ue_id}')
                ue.goal3.data_value = request.form.get(f'dataValue3_{ue_id}')
                ue.goal4.data_value = request.form.get(f'dataValue4_{ue_id}')

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Optionally, add a message to inform the user of the error
        # flash(f'An error occurred: {e}', 'error')

    # Redirect back to the dashboard after processing updates
    return redirect(url_for('clients_overview', me_id=me_id))


@app.route('/create_ueid', methods=['POST'])
def create_ueid():
    me_id = request.form.get('meid')
    if not me_id:
        flash('No MEID provided.', 'error')
        return redirect(url_for('login'))

    # Retrieve the ME object for the given MEID
    me = MEID.query.get(me_id)
    if not me:
        flash('MEID not found.', 'error')
        return redirect(url_for('login'))

    # Get the data values from the form
    name = request.form.get('name')
    data_value_1 = request.form.get('dataValue1')
    data_value_2 = request.form.get('dataValue2')
    data_value_3 = request.form.get('dataValue3')
    data_value_4 = request.form.get('dataValue4')

    # Create a new UE object and set its attributes
    new_ueid = UEID(meID=me_id, name=name)
    new_ueid.goal1 = Goal(data_value=data_value_1, progress=1, description='')
    new_ueid.goal2 = Goal(data_value=data_value_2, progress=1, description='')
    new_ueid.goal3 = Goal(data_value=data_value_3, progress=1, description='')
    new_ueid.goal4 = Goal(data_value=data_value_4, progress=1, description='')
    try:
        # Add the new UE object to the session and commit it to the database
        db.session.add(new_ueid)
        db.session.commit()
    except Exception as e:
        db.session.rollback()

    # Redirect back to the dashboard after processing
    return redirect(url_for('clients_overview', me_id=me_id))

@app.route('/secret', methods=['GET', 'POST'])
def secret():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "bobobobobo" and password == "bananamonkeytime":
            return render_template('meid_creation.html')
        else:
            return redirect(url_for('login'))

    return render_template('secret_login.html')

@app.route('/create_meid', methods=['POST'])
def create_meid():
    meid_input = request.form.get('meid')
    meid_password = request.form.get('meid_password')
    meid_name = request.form.get('meid_name')

    try:
        # Convert MEID input to an integer
        meid_number = int(meid_input)
    except ValueError:
        # Handle the case where conversion fails
        flash('MEID must be a number.', 'error')
        return redirect(url_for('secret'))

    # Proceed with creating the MEID
    new_meid = MEID(id=meid_number, password=meid_password, name=meid_name)

    try:
        db.session.add(new_meid)
        db.session.commit()
        flash('New MEID created successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {e}', 'error')

    return redirect(url_for('dashboard'))

@app.route('/get_active_ueid/<int:meid>')
def get_active_ueid(meid):
    # Query for the MEID entry
    me = MEID.query.get(meid)
    if me is None:
        return jsonify({'error': 'MEID not found'}), 404

    # Check if an active UEID exists
    active_ue = UEID.query.get(me.activeUEID)
    if active_ue is None:
        return jsonify({'activeUEID': None})

    # Return the data of the active UEID
    active_ue_data = {
        'id': active_ue.id,
        'name': active_ue.name,
        'dataValue1': active_ue.goal1.data_value,
        'dataValue2': active_ue.goal2.data_value,
        'dataValue3': active_ue.goal3.data_value,
        'dataValue4': active_ue.goal4.data_value,
        'progress1': active_ue.goal1.progress,
        'progress2': active_ue.goal2.progress,
        'progress3': active_ue.goal3.progress,
        'progress4': active_ue.goal4.progress
    }

    return jsonify({'activeUEID': active_ue_data})

@app.route('/more_info')
def more_info():
   title = "More Info"
   return render_template("more_info.html", title=title)

@app.route('/form', methods=["POST"])
def form():
   email = request.form.get("email_id")
   question = request.form.get("query_question")
   title = "Thank You!!!"
   return render_template("form.html", title=title, email=email, question=question)

@app.route('/logout', methods=['POST'])
def logout():
    # Remove the MEID from the session if it's there
    session.pop('meid', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=6922)