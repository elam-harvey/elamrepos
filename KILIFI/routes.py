from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from .models import Room, User, Payments, Bookings, Rating
from KILIFI import db, bcrypt
from flask import current_app as app
from KILIFI.forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('registration successful', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title=register, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('kilifi.html'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.passwords.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful', 'success')
            return redirect(url_for('home'))
            if user.is_admin:
                return redirect(url_for('admin.index'))  # Redirect to Admin Panel
            else:
                return "Access Denied. You are not an admin.", 403
        else:
            flash('Login failed check email and password', 'warning')
    return render_template('login.html', title='Login', form=form)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Home')


@app.route('/logout', methods=['GET','POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/rooms')
def rooms():
    all_rooms = Room.query.all()  # fetch all rooms
    return render_template('rooms.html', rooms=rooms)
    available_rooms = Room.query.filter_by(booked=False).all()  # get the free rooms
    return render_template('available_rooms.html', rooms=available_rooms)
    
@app.route('/book/<int:room_id>', methods=['GET','POST'])
def book(room_id):
    data = request.json
    room = Room.query.get(data.get('room_id'))
    
    if not room or not room.availability:
        return jsonify({'error': 'Room not available'}), 400

    total_days = (data.get('check_out') - data.get('check_in')).days
    total_price = total_days * listing.price_per_night

    booking = Booking(
        user_id=current_user.id,
        room_id=room.id,
        check_in=data.get('check_in'),
        check_out=data.get('check_out'),
        price=total_price
    )

    db.session.add(booking)
    db.session.commit()
    return jsonify({'message': 'Booking successful', 'total_price': total_price})

# API: Get User's Bookings
@app.route('/api/my_bookings', methods=['GET'])
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'room': b.room_id,
        'check_in': b.check_in,
        'check_out': b.check_out,
        'price': b.total_price
    } for b in bookings])

@app.route('/pay', methods=['GET','POST'])
@login_required
def pay():
    pass

@app.route('/rate', methods=['GET', 'POST'])
@login_required
def rate():
    if request.method == 'POST':
        rating_value = request.form.get('rating')  # Rating value (1-5 stars)
        comment = request.form.get('comment')  # Optional comment

        # Ensure the user is logged in
        if not current_user.is_authenticated:
            flash('You must be logged in to rate.', 'danger')
            return redirect(url_for('login'))

        # Create a new rating instance
        rating = Rating(
            rating_value=rating_value,
            comment=comment,
            user_id=current_user.id  # Link rating to logged-in user
        )

        # Add rating to the database
        db.session.add(rating)
        db.session.commit()

        flash('Your rating has been submitted.', 'success')
        return redirect(url_for('home'))