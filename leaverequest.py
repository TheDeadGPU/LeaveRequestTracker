# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from email.mime.text import MIMEText
import smtplib
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import os



# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leave_requests1.db'
db = SQLAlchemy(app)
engine = db.create_engine('sqlite:///leave_requests1.db')



# Define the LeaveRequest model
class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    znumber = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    hours = db.Column(db.String(100), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)
    leave_approved = db.Column(db.String(50), nullable=False)
    comments = db.Column(db.String(100), nullable=True)

# Create the database tables
# Create the database tables within the application context
with app.app_context():
    db.create_all()

# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.
@app.route('/', methods=['GET', 'POST'])
# ‘/’ URL is bound with hello_world() function.
def index():
        if request.method == 'POST':
            # Get form data
            name = request.form['name']
            znumber = request.form['znumber']
            date = request.form['date']
            hours = request.form['hours']
            leave_type = request.form['leave_type']
            leave_approved = "Pending"
            comments = request.form['comments']

            # Create a new LeaveRequest object
            leave_request = LeaveRequest(name=name, znumber = znumber, date=date, hours=hours, leave_type=leave_type, leave_approved=leave_approved, comments = comments)

            # Add to the database
            db.session.add(leave_request)
            db.session.commit()

            # Send an email
            #send_email(name, date, hours, leave_type)

            return redirect(url_for('index', success=1))

        # Retrieve all leave requests from the database
        leave_requests = LeaveRequest.query.all()
        return render_template('index.html', leave_requests=leave_requests)

# Create an Edit Form using WTForms
class EditForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    znumber = StringField('ZNumber', validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    hours = StringField('Hours', validators=[DataRequired()])
    leave_type = StringField('Leave Type', validators=[DataRequired()])
    leave_approved = StringField('Leave Approved', validators=[DataRequired()])
    comments = StringField('Comments', validators=[DataRequired()])

# Edit route
@app.route('/edit/<int:request_id>', methods=['GET', 'POST'])
def edit_request(request_id):
    # Define the Leave Approved Options
    leave_approved_options = [
        {'value': 'Pending', 'label': 'Pending'},
        {'value': 'Approved', 'label': 'Approved'},
        {'value': 'Rejected', 'label': 'Rejected'}]


    # Retrieve the LeaveRequest object
    leave_request = LeaveRequest.query.get_or_404(request_id)
    print(leave_request.leave_approved)
    # Create a form with the existing data
    form = EditForm(obj=leave_request)

    #Set selected value
    selected_approved_value = leave_request.leave_approved

    leave_type_options = [
        {'value': 'SIC', 'label': 'Sick Leave'},
        {'value': 'VAC', 'label': 'Vacation'},
        {'value': 'Per', 'label': 'Personal'},
        {'value': 'CTT', 'label': 'Comp Time Taken'},
        {'value': 'PLB', 'label': 'Paid Leave Bank'},
        {'value': 'JUR', 'label': 'Jury Duty'},
        {'value': 'UA', 'label': 'Union Activity'},
        {'value': 'FUR', 'label': 'Furlough (HR Approval Required)'},
        {'value': 'NOP', 'label': 'Unpaid Leave'},
        {'value': 'CTE', 'label': 'Comp Time Earned - Straight'},
        {'value': 'CTO', 'label': 'Comp Time Earned - 1.5x'},
        {'value': 'OT', 'label': 'Overtime Approval Request'},
        {'value': 'CSC', 'label': 'CSC Exam Leave (HR Approval Required)'}]
        
    #Set selected value
    selected_leavetype_value = leave_request.leave_type

    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        znumber = request.form['znumber']
        date = request.form['date']
        hours = request.form['hours']
        leave_type = request.form['leave_type']
        leave_approved = request.form['leave_approved']
        comments = request.form['comments']

        # Update the existing LeaveRequest object
        leave_request.name = name
        leave_request.znumber = znumber
        leave_request.date = date
        leave_request.hours = hours
        leave_request.leave_type = leave_type
        leave_request.leave_approved = leave_approved
        leave_request.comments = comments

        # Commit the changes to the database
        db.session.commit()

        # Redirect to the index page
        return redirect(url_for('index', request_id=request_id, success=1))

    # Render the edit form
    return render_template('edit_request.html', form=form, request_id=request_id, leave_approved_options = leave_approved_options, selected_approved_value = selected_approved_value, leave_type_options=leave_type_options, selected_leavetype_value=selected_leavetype_value)

@app.route('/delete/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    # Retrieve the LeaveRequest object
    leave_request = LeaveRequest.query.filter_by(id = request_id).delete()
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/emailrequest/<int:request_id>', methods=['POST'])
def email_request(request_id):
    # Retrieve the LeaveRequest object
    leave_request = LeaveRequest.query.get_or_404(request_id)
    send_email(leave_request.name, leave_request.date, leave_request.hours, leave_request.leave_type)
    return redirect(url_for('index'))


def send_email(name, date, hours, leave_type):
    # Configure your email settings
    smtp_server = 'mail.stockton.edu'
    smtp_port = 25
    sender_email = 'test@stockton.edu'
    recipient_email = 'james.girard@stockton.edu'

    # Create the email message
    subject = 'Time Accrual/Leave Request Form Submission'
    body = f""" 
    A Time Accrual/Leave Request is awaiting your approval or denial. Click reply to respond to sender giving your authorization or rejection.

    
    Requestor's Name: {name}

    Requestor's Z-Num: NULL


    Date: {date}  Hrs: {hours}  Type: {leave_type}

    
    Num Hrs Paid: 

    Num Hrs Unpaid: 

    Comments:

    """
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Connect to the SMTP server and send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Uncomment the following lines if needed:
            # server.starttls()
            # server.login(sender_email, sender_password)
            server.sendmail(sender_email, [recipient_email], msg.as_string())
            print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")

# main driver function
if __name__ == '__main__':
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(debug=True)