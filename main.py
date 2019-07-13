from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Productive@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '123ndh78'
db = SQLAlchemy(app) #Constructor db object to use in application
BLOGS_PER_PAGE = 3

class Blog(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(500))
    content = db.Column(db.String(5000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,title,content,user):
        self.title = title
        self.content = content
        self.user = user

class User(db.Model):
   id = db.Column(db.Integer,primary_key = True)
   email = db.Column(db.String(120), unique = True)
   password = db.Column(db.String(120))
   blog = db.relationship('Blog', backref='user')

   def __init__(self,email,password):
       self.email = email
       self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login','blogs','signup','index','blog']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect("/login")

@app.route("/login",methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if not is_email(email):
            flash('Invalid Email!!')
            return redirect("/login")
        if password == "":
            flash("Please enter password..")
            return redirect("/login")
        user = User.query.filter_by(email = email).first()
        if user:
            if password != user.password:
                flash("This combination of Username & Password does not exist!")
                return redirect("/login")
            else:
                session['user'] = user.email
                flash("Logged in...")
                return redirect('/newpost')
        else:
            flash("This username does not exist!!")
            return redirect("/login")
    else:
        return render_template("login.html")

@app.route("/signup",methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if not is_email(email):
            flash('Invalid Email: ' + email)
            return redirect('/signup')
        if len(password)<=3:
            flash('Password should be more than 3 characters.')
            return redirect('/signup')
        if password == "" or password != verify:
            flash("Password does not match!!")
            return redirect('/signup')
        user = User.query.filter_by(email = email).first()
        if user:
            flash("Email already exist. Kindly login..")
            return redirect("/signup")
        else:
            user = User(email=email, password=password)
            db.session.add(user)
            db.session.commit()
            session['user'] = user.email
            return redirect("/newpost")
    else:
        return render_template('signup.html')
 
@app.route("/logout")
def logout():
    if 'user' in session:
        del session['user']
    return redirect("/blogs")

@app.route('/blogs')
def blogs():
    prev_url=''
    next_url=''
    page = request.args.get('page', 1, type=int)
    blogs = Blog.query.paginate(page, BLOGS_PER_PAGE, False)
    if blogs.has_next:
        next_url = url_for('blogs', page=blogs.next_num)
    else:
        None
    if blogs.has_prev:
        prev_url = url_for('blogs', page=blogs.prev_num)
    else:
        None
    return render_template('blogs.html',blogs = blogs.items, next_url=next_url, prev_url=prev_url)

@app.route('/blog')
def blog():
    myuser = ''
    if 'user' not in session:
        myuser =  request.args.get('id')
    else:
        myuser = session['user']
    user = User.query.filter_by(email = myuser).first()
    blog =  Blog.query.filter_by(user_id=user.id).all()
    return render_template('singleUser.html', blogs=blog)

@app.route("/")
def index():
    users =  User.query.all()
    return render_template('index.html',users = users)

@app.route('/view_blog')
def view_blog():
    blog_id =  request.args.get('id')
    blog =  Blog.query.filter_by(id=blog_id).first()
    return render_template('viewblog.html', blog=blog)

@app.route("/newpost", methods=['POST','GET'])
def add_blog():
    if request.method == 'POST':
        title = cgi.escape(request.form['blog_title'])
        description = cgi.escape(request.form['blog_desc'])
        if title == "":
            flash("Please enter blog title.")
            return redirect("/newpost")
        if description == "":
            flash("Please enter blog description.")
            return redirect("/newpost")
        else:
            user = User.query.filter_by(email=session['user']).first()
            new_blog = Blog(title, description,user)            
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/view_blog?id={0}".format(new_blog.id))
    else:
        if 'user' not in session:
            return redirect("/login")
        else:
            return render_template("addblog.html")
    
def is_email(string):
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

if __name__ == '__main__':
    app.run()