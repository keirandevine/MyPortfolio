import secrets

from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor, CKEditorField
import requests
import smtplib
import os
from pprint import pprint
import datetime

#_____________________________________________Constants / Instantiations______________________________________________________#


MY_EMAIL = os.environ['MY_EMAIL']
MY_PASSWORD = os.environ['MY_PASSWORD']


#____________________________________________Creation of Flask App / Datebase___________________________________________________#



app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex()
ckeditor = CKEditor(app)
bootstrap = Bootstrap(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)





#________________________________________Configure DB Tables___________________________________________________#

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

class PortfolioItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    git_url = db.Column(db.String(250), nullable=False)



# with app.app_context():
#     db.create_all()
#___________________________________________Creat WTF Form_________________________________________________________#

class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class AddProjectForm(FlaskForm):
    name = StringField("Project Name", validators=[DataRequired()])
    category = SelectField('Category', coerce=str, choices=["App", "Game", "Web"], validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    img_url = StringField("Project Image URL", validators=[DataRequired(), URL()])
    git_url = StringField("GitHub Link", validators=[DataRequired(), URL()])
    submit = SubmitField("Submit Project")

#_________________________________________Definition of Functions____________________________________________#

def send_email(name, email, subject, message):
    email_message = f"Subject: New Message\n\nName: {name}\nEmail: {email}\nSubject: {subject}\nMessage: {message}"
    with smtplib.SMTP('smtp.gmail.com') as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=MY_PASSWORD)
        connection.sendmail(from_addr=MY_EMAIL, to_addrs=MY_EMAIL, msg=email_message)
        connection.close()


#______________________________________Flask Server Routes___________________________________________________#
@app.route('/')
def home():
    recent_posts = db.session.query(BlogPost).order_by(BlogPost.date.desc()).limit(3).all()
    portfolio_projects = db.session.query(PortfolioItem).all()
    return render_template('index.html', posts=recent_posts, projects=portfolio_projects)


@app.route('/blog/<int:blog_id>')
def get_post(blog_id):
    requested_post = BlogPost.query.get(blog_id)
    return render_template('blog-single.html', post=requested_post, charset='UTF-8')

@app.route('/new-post', methods=['GET', 'POST'])
def create_new_post():
    form = CreatePostForm()
    if request.method == 'POST':
        title = form.title.data
        subtitle = form.subtitle.data
        body = form.body.data
        author = form.author.data
        img_url = form.img_url.data
        new_blog = BlogPost(
            title=title,
            subtitle=subtitle,
            body=body,
            date=datetime.datetime.today().strftime('%B-%d-%Y'),
            author=author,
            img_url=img_url,
        )
        db.session.add(new_blog)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('make-post.html', form=form)


@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post_to_edit = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post_to_edit.title,
        subtitle=post_to_edit.subtitle,
        author=post_to_edit.author,
        img_url=post_to_edit.img_url,
        body=post_to_edit.body
    )
    if request.method =='POST':
        title = edit_form.title.data
        subtitle = edit_form.subtitle.data
        body = edit_form.body.data
        author = edit_form.author.data
        img_url = edit_form.img_url.data
        post_to_edit.title = title
        post_to_edit.subtitle = subtitle
        post_to_edit.body = body
        post_to_edit.author = author
        post_to_edit.img_url = img_url
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('make-post.html', id=post_id, form=edit_form)

@app.route('/delete-post')
def delete_blog_post():
    post_id = request.args.get('index')
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_blog'))


@app.route('/add-project', methods=['GET', 'POST'])
def add_new_project():
    form = AddProjectForm()
    if request.method == 'POST':
        name = form.name.data
        category = form.category.data
        description = form.description.data
        img_url = form.img_url.data
        git_url = form.git_url.data
        new_project = PortfolioItem(
            name=name,
            category=category,
            description=description,
            img_url=img_url,
            git_url=git_url,
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add-project.html', form=form)

@app.route('/contact', methods=['GET', 'POST'])
def get_contact_info():
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']
    print(name, email, subject, message)
    send_email(name, email, subject, message)
    return render_template('index.html')




if __name__ == "__main__":
    app.run(debug=True, port=5000)
