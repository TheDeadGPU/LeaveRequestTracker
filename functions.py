from flask import render_template_string,url_for
from flask_mailman import EmailMessage
from models import LeaveRequest
from datetime import datetime
from email.mime.text import MIMEText
import smtplib
from strings import (
    reset_password_email_html_content
)
from itsdangerous import URLSafeTimedSerializer

def create_leaverequest(webrequest,db, user_id):
    return update_leaverequest(webrequest, None, db, user_id)

def update_leaverequest(webrequest,index,db, user_id):
    # Get form data
    name = webrequest.form['name']
    znumber = webrequest.form['znumber']
    date = webrequest.form['date']
    hours = webrequest.form['hours']
    leave_type = webrequest.form['leave_type']
    leave_approved = "Pending"
    comments = webrequest.form['comments']

    # Format Date
    date_object = datetime.strptime(date, "%Y-%m-%d")
    date = date_object.strftime("%m/%d/%Y")

    if(index == None):
        # Create a new LeaveRequest object
        leave_request = LeaveRequest(name=name, user_id=user_id, znumber = znumber, date=date, hours=hours, leave_type=leave_type, leave_approved=leave_approved, comments = comments)

        # Add to the database
        db.session.add(leave_request)
        db.session.commit()
        return leave_request
    else:
        # Update LeaveRequest at Specified Index
        leave_request = LeaveRequest.query.get_or_404(index)
        leave_request.name = name
        leave_request.znumber = znumber
        leave_request.date = date
        leave_request.hours = hours
        leave_request.leave_type = leave_type
        leave_request.leave_approved = leave_approved
        leave_request.comments = comments

        # Commit the changes to the database
        db.session.commit()
        return leave_request
    
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
            server.sendmail(sender_email, [recipient_email], msg)
            print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")


def send_reset_password_email(user,app):
    # Configure your email settings
    smtp_server = 'mail.stockton.edu'
    smtp_port = 25
    sender_email = 'test@stockton.edu'
    recipient_email = 'james.girard@stockton.edu'
    reset_password_url = url_for(
        "reset_password",
        token=user.generate_reset_password_token(app),
        user_id=user.id,
        _external=True,
    )

    email_body = render_template_string(
        reset_password_email_html_content, reset_password_url=reset_password_url
    )
    # Connect to the SMTP server and send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Uncomment the following lines if needed:
            # server.starttls()
            # server.login(sender_email, sender_password)
            server.sendmail(sender_email, [recipient_email], email_body)
            print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")

