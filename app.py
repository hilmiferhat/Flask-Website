from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import os
from flask_mail import Mail, Message
from datetime import datetime

mail = Mail()
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Set a secret key

# SMTP
app.config['MAIL_SERVER'] = "smtp.fastmail.com"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "hilmiferhat88@fastmail.com"
app.config['MAIL_PASSWORD'] = "jxpzu5qmhrjef6g9"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail.init_app(app)

# SQLite veritabanı dosyasının yolu
db_path_post = os.path.join(os.path.dirname(__file__), 'Database/post.db')
db_path_user = os.path.join(os.path.dirname(__file__), 'Database/user.db')


# SQLite veritabanı oluşturma ve tablo oluşturma işlemleri
def create_table():
    with sqlite3.connect(db_path_post) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS post(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            topic TEXT NOT NULL,
            banner TEXT,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            date_posted integer
        )
        ''')
        conn.commit()
        
    with sqlite3.connect(db_path_user) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            mail TEXT NOT NULL
        )
        """)
        conn.commit()

create_table()

def register_mail(username, mail_adress):
    msg = Message(
        f"Merhaba, {username}",
        sender="hilmiferhat88@fastmail.com",
        recipients=[mail_adress]
    )
    msg.body = "Blog sitesine kayıt olduğun için teşekkürler."
    mail.send(msg)
    return "Sent email..."

# Tüm gönderileri getiren fonksiyon
def get_posts():
    with sqlite3.connect(db_path_post) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM post')
        posts = cursor.fetchall()
        # Convert each tuple to a dictionary
        posts_list = []
        for post in posts:
            post_dict = {
                'id': post[0],
                'title': post[1],
                'topic': post[2],
                'banner': post[3],
                'content': post[5],
                'author': post[4],
                'date_posted': post[6],
            }
            posts_list.append(post_dict)
        return posts_list
    


# ROUTES
@app.route('/')
def home():
    if 'username' not in session or session['username'] is None:
        return redirect(url_for('login'))
    else:
        posts = get_posts()
        return render_template('index.html', posts=posts)

@app.route('/post<int:post_id>')
def post(post_id):
    if 'username' not in session or session['username'] is None:
        return redirect(url_for('login'))
    else:
        conn = sqlite3.connect(db_path_post)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM post WHERE id = ?', (post_id,))
        post = cursor.fetchone()
        post_dict = {
            'id': post[0],
            'title': post[1],
            'topic': post[2],
            'banner': post[3],
            'content': post[5],
            'author': post[4],
            'date_posted': post[6],
        }
        conn.close()
        return render_template('post.html', post=post_dict)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form
        try:
            with sqlite3.connect(db_path_user) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user (username, password, mail) VALUES (?, ?, ?)", (user['username'], generate_password_hash(user['password']), user['email']))
                register_mail(user['username'], user['email'])
                conn.commit()
        except sqlite3.IntegrityError:
            flash('Username already exists! Please choose a different username.', 'danger')
            return render_template('register.html')
        else:
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        userForm = request.form
        username = userForm['username']
        with sqlite3.connect(db_path_user) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE username = ?", (username,))  # Changed table name to 'user' and removed unnecessary brackets
            result = cursor.fetchone()
            if result:
                _user = result
                if check_password_hash(_user[2], userForm['password']):  # Used check_password_hash function
                    session['username'] = _user[1]
                    flash('Welcome ' + session['username'] + '! You have been successfully logged in', 'success')
                    return redirect('/')
                else:
                    flash('Password does not match', 'danger')
            else:
                flash('User not found!', 'danger')
        return render_template('login.html')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove 'username' key from session
    flash('You have been logged out', 'info')  # Flash message to inform the user
    return redirect(url_for('login'))  # Redirect to login page


@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    if 'username' not in session or session['username'] is None:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            title = request.form['title']
            topic = request.form['topic']
            author = session['username']
            content = request.form['content']
            
            # File Upload Handling
            if 'banner' in request.files:
                banner = request.files['banner']
                if banner.filename != '':
                    banner.save(os.path.join('static', 'uploads', banner.filename))  # Save banner to static/uploads folder
                    banner_path = os.path.join('uploads', banner.filename)
                else:
                    banner_path = None
            else:
                banner_path = None
            
            # Inserting data into the database
            conn = sqlite3.connect(db_path_post)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO post (title, topic, banner, author, content, date_posted) VALUES (?, ?, ?, ?, ?, ?)', (title, topic, banner_path, author, content, datetime.now().date()))
            conn.commit()
            conn.close()
            
            return redirect(url_for('home'))
        return render_template('new_post.html')


if __name__ == '__main__':
    app.run(debug=True)
