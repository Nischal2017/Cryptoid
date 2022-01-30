from http import server
from flask import Flask,render_template,redirect
import sqlalchemy

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('homepg.html')


if __name__ == '__main__':
    app.debug(True)