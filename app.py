# Import necessary modules
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, login_required, logout_user, current_user, UserMixin, LoginManager
from werkzeug.utils import secure_filename
import os
import secrets  # Added for generating a secure secret key
import bcrypt

# Create a Flask application
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Use a secure secret key

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_blog.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

PASSWORD = 'ade34$$&ght103pre4&$$' 
bcrypt_salt_rounds = 12

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    subheading = db.Column(db.String(255))
    blog_body = db.Column(db.String(255))
    title2 = db.Column(db.String(255))
    body2 = db.Column(db.String(255))
    date = db.Column(db.String(255))
    image = db.Column(db.String(10))
    likes = db.Column(db.Integer, default=0) 

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

    @staticmethod
    def get_by_id(user_id):
        return User(user_id)
    
    @staticmethod
    def check_password(password_attempt, hashed_password):
        return bcrypt.checkpw(password_attempt.encode('utf-8'), hashed_password)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    blogs = Blog.query.all()
    per_page = 20  # Number of blogs to display per page

    # Get the current page from the request parameters
    page = request.args.get('page', 1, type=int)

    # Count the total number of blogs
    total_blogs = Blog.query.count()

    # Determine the number of pages
    num_pages = (total_blogs - 1) // per_page + 1

    # Calculate the offset for SQL query
    offset = (page - 1) * per_page

    # Query blogs for the current page
    blogs = Blog.query.offset(offset).limit(per_page).all()

    # Calculate the offset for SQL query
    return render_template("index.html", page=page, num_pages=num_pages, blogs=blogs, user=current_user)



@app.route("/add_blog", methods=["GET", 'POST'])
@login_required
def add_blog():
    if request.method == "POST":
        # Get form data
        blog_title = request.form.get("blog_title")
        blog_subheading = request.form.get("blog_subheading")
        blog_body = request.form.get("blog_body")
        body_2 = request.form.get("body_2")
        title2 = request.form.get("title2")
        date = request.form.get("date")
        image = request.files.get("image")

        # Check if an image file is part of the form data
        if 'image' in request.files:
            image = request.files['image']

            # Ensure that the image has an allowed extension
            allowed_image_extensions = {'.png'}
            image_extension = os.path.splitext(image.filename)[1].lower()

            if image_extension not in allowed_image_extensions:
                flash("Invalid image file format. Please use PNG.")
                return redirect(url_for('add_blog'))

            # Securely save the image using secure_filename
            image_filename = secure_filename(image.filename)
            image_path = os.path.join('static', 'image', image_filename)
            image.save(image_path)
        else:
            # If no image was provided in the form, set it to None
            image_filename = None

        # Validate other form fields
        if not all([blog_title, blog_subheading, blog_body, body_2, image]):
            flash('All Fields Are Required.', category='error')
            return redirect(url_for('add_blog'))

        # Create a new blog instance
        new_blog = Blog(
            title=blog_title,
            subheading=blog_subheading,
            blog_body=blog_body,
            body2=body_2,
            title2=title2,
            date=date,
            image=image_filename
        )

        # Add the new blog to the database session and commit the changes
        db.session.add(new_blog)
        db.session.commit()

        # Perform any additional processing or validation here
        return redirect(url_for("index"))

    return render_template("add_blog.html", user=current_user)


@login_manager.user_loader
def load_user(id):
    return User.get_by_id(int(id))

@app.route('/lo55664gg$$killgwcg', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password_attempt = request.form.get('password')
        
        hashed_password = bcrypt.hashpw("ade34$$&ght103pre4&$$".encode('utf-8'), bcrypt.gensalt(bcrypt_salt_rounds))

        if User.check_password(password_attempt, hashed_password):
            user = User(1)
            login_user(user)
            flash('Logged in successfully!', category='success')
            return redirect(url_for('add_blog'))
        else:
            flash('Incorrect username or password, try again.', category='error')

    return render_template("login.html")


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('index'))

@app.route('/blog-info/<int:blog_id>')
def blog_info(blog_id):
    blog = Blog.query.get(blog_id)  # Corrected variable name to 'blog'
    return render_template('blog_info.html', blog=blog, user=current_user)  # Corrected template name to 'blog_info.html'

@app.route('/like_blog/<int:blog_id>', methods=['POST'])
def like_blog(blog_id):
    blog = Blog.query.get(blog_id)

    if blog:
        blog.likes += 1
        db.session.commit()

        return jsonify({'likes': blog.likes})

    return jsonify({'error': 'Blog not found'}), 404


# DELETE BLOG
@app.route('/delete_blog/<int:blog_id>', methods=['POST'])
@login_required
def delete_blog(blog_id):
    blog = Blog.query.get(blog_id)

    if blog:
        # Remove the associated image file (if it exists)
        if blog.image:
            image_path = os.path.join('static', 'image', blog.image)
            try:
                os.remove(image_path)
            except FileNotFoundError:
                pass

        # Delete the blog from the database
        db.session.delete(blog)
        db.session.commit()

        flash('Blog deleted successfully!', category='success')
        return redirect(url_for('index'))

    flash('Blog not found', category='error')
    return redirect(url_for('index'))
# end of log in and out customization

if __name__ == '__main__':
    app.run(debug=True)
