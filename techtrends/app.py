import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

no_of_connections = 0   # variable to count the no of connections made with the database


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    get_db_connection.counter += 1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection


get_db_connection.counter = 0


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post


# Function to count no of posts
def get_no_of_posts():
    connection = sqlite3.connect('database.db')
    no_of_posts = connection.execute('SELECT count(*) FROM posts').fetchone()
    connection.close()
    return no_of_posts


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logging.debug("Error 404: Page not found!!")
      return render_template('404.html'), 404
    else:
      logging.debug("Article {} retrived!".format(post['title']))
      return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    logging.debug("About us page retrived")
    return render_template('about.html')


# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logging.debug("New article created: {{%(title)s}}")
            return redirect(url_for('index'))

    return render_template('create.html')


# Defines the route that displays health of website
@app.route('/healthz')
def status():
    response = app.response_class(
        response=json.dumps({ 
            "result": "OK - healthy" 
        }),
        status=200,
        mimetype='application/json'
    )

    return response


# Defines the route that displays metrics for the website
@app.route('/metrics')
def metrics():
    no_of_posts = get_no_of_posts()
    response = app.response_class(
        response=json.dumps({
            "posts_count": no_of_posts,
            "db_connection_count": get_db_connection.counter  
        }),
        status=200,
        mimetype='application/json'
    )

    return response


# start the application on port 3111
if __name__ == "__main__":

   logging.basicConfig(
       level=logging.DEBUG, 
       format="{{%(asctime)s}}, {{%(message)s}}"
    ) 

   app.run(host='0.0.0.0', port='3111')
