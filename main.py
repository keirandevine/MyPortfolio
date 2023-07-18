from flask import Flask, render_template
import requests

app = Flask(__name__)

BLOGS_API = 'https://api.npoint.io/802720ad4cf9deb722b0'

response = requests.get(BLOGS_API)
blog_posts = response.json()

@app.route('/')
def home():
    return render_template('index.html', blogs=blog_posts)


@app.route('/blog')
def get_post():
    return render_template('blog-single.html', blogs=blog_posts)

if __name__ == "__main__":
    app.run(debug=True)
