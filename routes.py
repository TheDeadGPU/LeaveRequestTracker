from flask import (
    Flask,
    render_template,
    redirect,
    flash,
    url_for,
    request,
    session
)

from datetime import timedelta, datetime
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError


from flask_bcrypt import Bcrypt,generate_password_hash, check_password_hash

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

from functions import create_leaverequest, update_leaverequest, send_email,send_reset_password_email

from app import create_app,db,login_manager,bcrypt
from models import User, LeaveRequest
from forms import login_form,register_form, leave_request_edit_form, ResetPasswordRequestForm, ResetPasswordForm
from sqlalchemy import select

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app = create_app()

@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)

@login_required
@app.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
    # Retrieve all leave requests from the database
    if request.method == 'POST':
        # Create Leave Request from Form Data
        leave_request = create_leaverequest(request,db,current_user.id)
        # Add to the database
        db.session.add(leave_request)
        db.session.commit()

        # Redirect User to the Index Page
        return redirect(url_for('index'))
    
    try:
        leave_requests = LeaveRequest.query.filter_by(user_id = current_user.id)
        print(leave_requests.count())
    except:
        leave_requests = LeaveRequest.query.all()
    return render_template("index.html",title="Home",leave_requests=leave_requests)


@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = login_form()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if check_password_hash(user.pwd, form.pwd.data):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")

    return render_template("auth.html",
        form=form,
        text="Login",
        title="Login",
        btn_action="Login"
        )



# Register route
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data
            
            newuser = User(
                username=username,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd),
            )
    
            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")
    return render_template("auth.html",
        form=form,
        text="Create account",
        title="Register",
        btn_action="Register account"
        )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/reset_password/", methods=["GET", "POST"])
def reset_password_request():
    if(current_user.is_authenticated):
        return redirect(url_for("index"))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user_select = select(User).where(User.email == form.email.data)
        user = db.session.scalar(user_select)

        if user:
            send_reset_password_email(user,app)

        flash("Instructions for resetting your password were sent to your email address,"
              "if it exists in our system.")
        
        return redirect(url_for("reset_password_request"))
    
    return render_template("reset_password_request.html", title = "Password Reset", form = form)

@app.route("/reset_password/<token>/<int:user_id>", methods=["GET", "POST"])
def reset_password(token, user_id):
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    user = User.validate_reset_password_token(token, user_id,app)
    print(user)
    if not user:
        return render_template(
            "reset_password_error.html", title="Reset Password error"
        )

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()

        return render_template(
            "reset_password_success.html", title="Reset Password success"
        )

    return render_template(
        "reset_password.html", title="Reset Password", form=form
    )

@app.route('/edit/<int:request_id>', methods=['GET','POST'])
def edit_leaverequest(request_id):
        # Define the Leave Approved Options
    leave_approved_options = [
        {'value': 'Pending', 'label': 'Pending'},
        {'value': 'Approved', 'label': 'Approved'},
        {'value': 'Rejected', 'label': 'Rejected'}]
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
    
    # Retrieve the LeaveRequest object
    leave_request = LeaveRequest.query.get_or_404(request_id)

    # Set selected value for leave_approved
    selected_approved_value = leave_request.leave_approved

    # Set selected value for leave_type
    selected_leavetype_value = leave_request.leave_type

    # Create a form with the existing data
    form = leave_request_edit_form(obj=leave_request)

    if request.method == 'POST':
        # Update the leaverequest with the new data
        update_leaverequest(request,request_id,db,current_user.id)

        # Redirect to the index page
        return redirect(url_for('index'))
    date_object = datetime.strptime(leave_request.date, "%m/%d/%Y")
    iso_date_str = date_object.strftime("%Y-%m-%d")
    # Render the edit form
    return render_template('edit_request.html', form=form, request_id=request_id, leave_approved_options = leave_approved_options, selected_approved_value = selected_approved_value, leave_type_options=leave_type_options, selected_leavetype_value=selected_leavetype_value, iso_date_str=iso_date_str)

@app.route('/delete/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    # Retrieve the LeaveRequest object
    if current_user.id == LeaveRequest.query.get_or_404(request_id).user_id:
        leave_request = LeaveRequest.query.filter_by(id = request_id).delete()
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/emailrequest/<int:request_id>', methods=['POST'])
def email_request(request_id):
    # Retrieve the LeaveRequest object
    leave_request = LeaveRequest.query.get_or_404(request_id)
    if current_user.id == leave_request.user_id:
        send_email(leave_request.name, leave_request.date, leave_request.hours, leave_request.leave_type)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)