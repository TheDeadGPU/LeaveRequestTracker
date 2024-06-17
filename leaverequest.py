# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from email.mime.text import MIMEText
import smtplib


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
    date = db.Column(db.String(20), nullable=False)
    hours = db.Column(db.String(100), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)

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
            date = request.form['date']
            hours = request.form['hours']
            leave_type = request.form['leave_type']

            # Create a new LeaveRequest object
            leave_request = LeaveRequest(name=name, date=date, hours=hours, leave_type=leave_type)

            # Add to the database
            db.session.add(leave_request)
            db.session.commit()

            # Send an email
            send_email(name, date, leave_type)

            return redirect(url_for('index'))

        # Retrieve all leave requests from the database
        leave_requests = LeaveRequest.query.all()
        return render_template('index.html', leave_requests=leave_requests)

def send_email(name, date, leave_type):
    # Configure your email settings
    smtp_server = 'mail.stockton.edu'
    smtp_port = 25
    sender_email = 'test@stockton.edu'
    sender_password = 'your_email_password'
    recipient_email = 'james.girard@stockton.edu'

    # Create the email message
    subject = 'New Leave Request'
    body = f"Name: {name}\nDate: {date}\nLeave Type: {leave_type}"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Connect to the SMTP server and send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        #server.starttls()
        #server.login(sender_email, sender_password)
        server.sendmail(sender_email, [recipient_email], msg.as_string())

# main driver function
if __name__ == '__main__':

    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(debug=True)