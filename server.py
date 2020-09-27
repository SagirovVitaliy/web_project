
from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello():
    world = 'ZA WARUDO'
    return (f'Hello {world}');


if __name__=='__main__':
    app.run()
