from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Productive@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) #Constructor db object to use in application

class Blog(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(500))
    content = db.Column(db.String(5000))

    def __init__(self,title,content):
        self.title = title
        self.content = content

@app.route('/blogs')
def index():
    blogs =  Blog.query.all()
    return render_template('blogs.html',blogs = blogs)

@app.route('/view_blog')
def view_blog():
    blog_id =  request.args.get('id')
    blog =  Blog.query.filter_by(id=blog_id).first()
    return render_template('viewblog.html', blog=blog)

@app.route("/newpost", methods=['POST','GET'])
def add_blog():
    title_error = ""
    description_error = ""
    if request.method == 'POST':
        title = request.form['blog_title']  
        description = request.form['blog_desc']  
        if title == "":
            title_error = "Please enter blog title."
        if description == "":
            description_error = "Please enter blog description."
        if not title_error and not description_error:
            new_blog = Blog(title, description)
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/view_blog?id={0}".format(new_blog.id))
        else:
            return render_template("addblog.html", title_error=title_error,description_error=description_error,title=title,description=description)
    else:
        return render_template("addblog.html",title_error=title_error,description_error=description_error)

if __name__ == '__main__':
    app.run()