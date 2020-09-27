
from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def hello():
    world = 'ZA WARUDO'
    return render_template('hello_world.html', world=world);


if __name__=='__main__':
    app.run(debug=True)
