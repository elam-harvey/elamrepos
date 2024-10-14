from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from farmblog import db, bcrypt
from farmblog.utils import save_picture 
from datetime import datetime
from werkzeug.utils import secure_filename
from farmblog.models import User, Post, Products
from flask import current_app as app
from farmblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm, ProductEditForm,
                            RequestResetForm, ResetPasswordForm,
                            ProductCreationForm, NewPostForm)
import os

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html',show_footer=True, title='Home')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', show_footer=False, title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login',show_footer=False, form=form)

@app.route("/logout")
def logout():
    logout_user()
    print(f"User logged out: {current_user.is_authenticated}") 
    return redirect(url_for('home'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()  # Correct form for account updates
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    # Assuming you have a default user image file path
    image_file = url_for('static', filename='images/' + (current_user.image_file or 'profile_pic.jpg'))
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/market")
@login_required
def market():
    products = Products.query.all()  # Fetching all products
    return render_template('marketplace.html', title='Market', products=products)

@app.route("/product/<int:product_id>")
@login_required
def product_details(product_id):
    product = Products.query.get_or_404(product_id)
    return render_template('p_details.html', product=product)

@app.route("/product/new", methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductCreationForm() 
    if request.method == 'POST' and form.validate_on_submit():
        if form.f_image.data:
            filename = save_picture(form.f_image.data)
        else:
            filename = None  # Handle the case where no image is uploaded
        upload_directory = 'farmblog/static/uploads'
        filename = secure_filename(form.f_image.data.filename)
        file_path = os.path.join(upload_directory, filename)

        # Create the upload directory if it doesn't exist
        if not os.path.exists(upload_directory):
            os.makedirs(upload_directory)

        # Save the uploaded file
        try:
            form.f_image.data.save(file_path)
            print(f"File saved at: {file_path}")  # Debug statement
        except Exception as e:
            print(f"Error saving file: {e}")

        #  product creation
        product = Products(
            name=form.name.data,
            quantity=form.quantity.data,
            new_quantity=form.new_quantity.data or form.quantity.data,
            description=form.description.data,
            price=form.price.data,
            new_price=form.new_price.data or form.price.data,
            f_image=filename,  
            date_posted=datetime.utcnow(),
            user_id=current_user.id  
        )
        db.session.add(product)
        db.session.commit()
        flash('Your product has been created!', 'success')
        return redirect(url_for('market'))

    return render_template('add_product.html', title='Add Product', form=form, legend='Add Product')

@app.route("/product/<int:product_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductEditForm(obj=product)  # Populate form with product details
    if request.method == 'POST' and form.validate_on_submit():
        product = Product.query.get_or_404(product_id)
    if post.author != current_user:
        abort(403)
    form = ProductEditForm()
    if form.validate_on_submit():
        product.title = form.title.data
        product.content = form.content.data
        db.session.commit()
        flash('Your post has been updated successfully!', 'success')
        return redirect(url_for('product', product_id=product.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('edit_product.html', title='Edit Product', form=form, legend='Update Product')

@app.route("/community")
@login_required
def community():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5) # Fetch all posts
    return render_template('community.html', title='Community', posts=posts)

@app.route("/community/<int:post_id>")
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_details.html', title='Details', post=post)

@app.route("/community/new", methods=['GET', 'POST'])
@login_required
def add_post():
    form = NewPostForm()  # Correct form for post creation
    if request.method == 'POST' and form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post added SUCCESSFULLY!', 'success')
        return redirect(url_for('community'))
    return render_template('add_post.html', title='New Post', form=form, legend='New Post')

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id) 
    if post.author != current_user:
        abort(403)
    form = NewPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been updated", 'success')
        return redirect(url_for('post_detail', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('add_post.html',post_id=post.id, title='Update Post', form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted SUCCESSFULLY!', 'success')
    return redirect(url_for('community'))

@app.route("/product/<int:product_id>/update", methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = Products.query.get_or_404(product_id)
    
    # Ensure the user owns the product (you might need this if multiple users can post products)
    if product.user_id != current_user.id:
        abort(403)  # Forbidden access
    
    form = ProductCreationForm()

    if form.validate_on_submit():
        if form.f_image.data:
            # Handle image update if a new image is uploaded
            new_filename = save_picture(form.f_image.data)
            product.f_image = new_filename  # Update image filename

        # Update product fields
        product.name = form.name.data
        product.quantity = form.quantity.data
        product.new_quantity = form.new_quantity.data or form.quantity.data
        product.description = form.description.data
        product.price = form.price.data
        product.new_price = form.new_price.data or form.price.data
        product.date_posted = datetime.utcnow()  # Update date

        db.session.commit()
        flash('Your product has been updated!', 'success')
        return redirect(url_for('market'))

    # Pre-populate the form with the existing product data
    elif request.method == 'GET':
        form.name.data = product.name
        form.quantity.data = product.quantity
        form.new_quantity.data = product.new_quantity
        form.description.data = product.description
        form.price.data = product.price
        form.new_price.data = product.new_price

    return render_template('add_product.html', title='Update Product', form=form, legend='Update Product')

@app.route("/product/<int:product_id>/delete", methods=['POST'])
@login_required
def delete_product(product_id):
    product = Products.query.get_or_404(product_id)

    # Ensure the user owns the product
    if product.user_id != current_user.id:
        abort(403)  # Forbidden access

    db.session.delete(product)
    db.session.commit()
    flash('Your product has been deleted!', 'success')
    return redirect(url_for('market'))

@app.route("/product/<int:product_id>/buy", methods=['GET','POST'])
@login_required
def buy(product_id):
    # Fetch the product
    product = Products.query.get_or_404(product_id)

    # Check if the product is available in sufficient quantity
    if product.quantity > 0:
        # Decrease the product quantity after purchase
        product.quantity -= 1
        db.session.commit()

        # Optionally, add to the user's purchase history
        purchase = PurchaseHistory(
            user_id=current_user.id,
            product_id=product_id,
            date_purchased=datetime.utcnow()
        )
        db.session.add(purchase)
        db.session.commit()

        flash(f"You have successfully bought {product.name}!", "success")
    else:
        flash(f"{product.name} is out of stock!", "danger")

    return redirect(url_for('market'))    


