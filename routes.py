import logging
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, mail
from models import User, SMSHistory, CallHistory, LookupHistory
from flask_mail import Message
from twilio_service import TwilioService
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

twilio_service = TwilioService()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            logger.debug(f"Signup attempt for email: {email}")

            # Check if the email already exists
            if User.query.filter_by(email=email).first():
                flash('Email already exists. Please log in.', 'danger')
                logger.warning(f"Email already exists: {email}")
                return redirect(url_for('login'))

            new_user = User(email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            logger.info(f"New user created: {email}")

            # Send verification email
            token = generate_confirmation_token(email)  # Ensure this function is defined
            confirm_url = url_for('confirm_email', token=token, _external=True)
            html = f'<p>Please confirm your email by clicking on the link: <a href="{confirm_url}">Confirm Email</a></p>'
            msg = Message('Email Confirmation', sender='noreply@example.com', recipients=[email])
            msg.html = html
            mail.send(msg)
            logger.info(f"Verification email sent to: {email}")

            flash('Signup successful! Please check your email for confirmation.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            logger.error(f"Error in signup: {e}", exc_info=True)  # Log the error with traceback
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('signup.html')

@app.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)  # Ensure this function is defined
    user = User.query.filter_by(email=email).first()
    if user:
        user.is_active = True
        db.session.commit()
        flash('Email confirmed! You can now log in.', 'success')
        logger.info(f"Email confirmed for user: {email}")
    else:
        flash('Email confirmation failed.', 'danger')
        logger.warning(f"Email confirmation failed for token: {token}")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        logger.debug(f"Login attempt for email: {email}")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if user.is_active:
                login_user(user)
                logger.info(f"User  logged in: {email}")
                return redirect(url_for('dashboard'))
            else:
                flash('Your account is not approved yet.', 'warning')
                logger.warning(f"User  account not approved: {email}")
        else:
            flash('Invalid email or password.', 'danger')
            logger.warning(f"Invalid login attempt for email: {email}")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logger.info(f"User  logged out: {current_user.email}")
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    logger.debug(f"Dashboard accessed by user: {current_user.email}")
    return render_template('dashboard.html')

@app.route('/admin/users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        logger.warning(f"Unauthorized access attempt by user: {current_user.email}")
        return redirect(url_for('dashboard'))
    users = User.query.all()
    logger.debug("Admin accessed user management.")
    return render_template('manage_users.html', users=users)

@app.route('/admin/approve/<int:user_id>')
@login_required
def approve_user(user_id):
    if current_user.role != 'admin':
        logger.warning(f"Unauthorized approval attempt by user: {current_user.email}")
        return redirect(url_for('dashboard'))
    user = User.query.get(user_id)
    if user:
        user.is_active = True
        db.session.commit()
        flash('User  approved successfully.', 'success')
        logger.info(f"User  approved: {user.email}")
    return redirect(url_for('manage_users'))

@app.route('/admin/reject/<int:user_id>')
@login_required
def reject_user(user_id):
    if current_user.role != 'admin':
        logger.warning(f"Unauthorized rejection attempt by user: {current_user.email}")
        return redirect(url_for('dashboard'))
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User  rejected and deleted.', 'success')
        logger.info(f"User  rejected: {user.email}")
    return redirect(url_for('manage_users'))

@app.route('/sms_campaign', methods=['GET', 'POST'])
@login_required
def sms_campaign():
    if request.method == 'POST':
        to = request.form['to']
        message = request.form['message']
        logger.debug(f"SMS campaign attempt by user: {current_user.email} to {to}")

        # Ensure the current_user has a phone_number attribute
        if not hasattr(current_user, 'phone_number'):
            flash('Your account does not have a phone number associated.', 'danger')
            logger.warning(f"No phone number associated with user: {current_user.email}")
            return redirect(url_for('sms_campaign'))

        twilio_service.send_sms(to, current_user.phone_number, message)
        flash('SMS sent successfully!', 'success')
        logger.info(f"SMS sent from {current_user.phone_number} to {to}")
        return redirect(url_for('sms_campaign'))
    return render_template('sms_campaign.html')

@app.route('/sms_history')
@login_required
def sms_history():
    page = request.args.get('page', 1, type=int)
    sms_records = SMSHistory.query.paginate(page, per_page=10)
    logger.debug(f"SMS history accessed by user: {current_user.email}")
    return render_template('sms_history.html', sms_records=sms_records)

@app.errorhandler(404)
def page_not_found(e):
    logger.error(f"Page not found: {e}", exc_info=True)
    return render_template('error.html', error=str(e)), 404