from flask import Flask, render_template, request, redirect
import requests
import smtplib
import os
from pprint import pprint

#_____________________________________________Constants______________________________________________________#

BLOGS_API = os.environ['BLOG_ENDPOINT']
response = requests.get(BLOGS_API)
blog_posts = response.json()

MY_EMAIL = os.environ['MY_EMAIL']
MY_PASSWORD = os.environ['MY_PASSWORD']

app = Flask(__name__)


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
    pprint(blog_posts)
    return render_template('index.html', blogs=blog_posts)


@app.route('/blog/<int:blog_id>')
def get_post(blog_id):
    selected_post = {}
    for post in blog_posts:
        if post['id'] == blog_id:
            selected_post = post
            pprint(selected_post)
    return render_template('blog-single.html', post=selected_post, encodings='utf-8')

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
    app.run(debug=True)
