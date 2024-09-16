# from flask import Flask, render_template, request, redirect, url_for, flash
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# import firebase_admin
# from  firebase_admin import db, credentials


# app = Flask(__name__)

# cred = credentials.Certificate("crop-monitoring-key.json")
# firebase_admin.initialize_app(cred)






# app.config['SECRET_KEY'] = 'your_secret_key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hell.db'
# db = SQLAlchemy(app)

# login_manager = LoginManager(app)
# login_manager.login_view = 'login'


# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), unique=False, nullable=False)
#     password = db.Column(db.String(100), nullable=False)


# # Create database tables
# with app.app_context():
#     db.create_all()


# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))


# @app.route('/')
# def home():
#     return render_template('home.html')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = User.query.filter_by(username=username).first()

#         if user and user.password == password:  # Note: In a real app, use bcrypt or a similar library for password hashing
#             login_user(user)
#             return redirect(url_for('dashboard'))
#         else:
#             flash('Invalid username or password', 'error')

#     return render_template('login.html')


# @app.route('/login_admin', methods=['GET', 'POST'])
# def login_admin():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = User.query.filter_by(username=username).first()

#         if user and user.password == password:  # Note: In a real app, use bcrypt or a similar library for password hashing
#             login_user(user)
#             return redirect(url_for('dashboard_admin'))
#         else:
#             flash('Invalid username or password', 'error')

#     return render_template('login_admin.html')



# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         new_user = User(username=username, password=password)  # Note: In a real app, hash the password
#         db.session.add(new_user)
#         db.session.commit()
#         flash('Account created successfully. Please log in.', 'success')
#         return redirect(url_for('login'))

#     return render_template('signup.html')


# @app.route('/dashboard')
# @login_required
# def dashboard():
#     return render_template('dashboard.html', user=current_user)

# @app.route('/admin')
# @login_required
# def dashboard_admin():
#     return render_template('dashboard_admin.html', user=current_user)


# @app.route('/userslist')
# @login_required
# def users_list():
#     users = User.query.all()
#     return render_template('userslist.html', users=users)


# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('home'))


# if __name__ == '__main__':
#     app.run(debug=True)
