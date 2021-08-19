import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    get_db_connection.counter += 1  # increments every time a connection is established with the DB
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection


get_db_connection.counter = 0     # variable to count the no of connections made with the database


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

# Define StreamHandlers for stdout and stderr
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.ERROR)
dual_handlers = [stdout_handler, stderr_handler]

# Define basic configuration for the log messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(name)s:[%(asctime)s] - %(message)s',
)


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
        app.logger.info('Error 404: Page not found!!')
        return render_template('404.html'), 404
    else:
        app.logger.info('Retrieved Article: %s', post['title'])
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Us page retrieved!')
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
            app.logger.info('New article created: %s', title)
            return redirect(url_for('index'))

    return render_template('create.html')


# Defines the route that displays health of website
@app.route('/healthz')
def status():
    response = app.response_class(
        response=json.dumps({ 
            'result': 'OK - healthy'
        }),
        status=200,
        mimetype='application/json'
    )
    app.logger.info('healthz route reached successfully!')
    return response


# Defines the route that displays metrics for the website
@app.route('/metrics')
def metrics():
    no_of_posts = get_no_of_posts()
    response = app.response_class(
        response=json.dumps({
            'posts_count': no_of_posts,
            'db_connection_count': get_db_connection.counter
        }),
        status=200,
        mimetype='application/json'
    )
    app.logger.info('metrics route reached successfully!')
    return response


# start the application on port 3111
if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3111')
