import os
from flask import Flask
from flask import request, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    headers = request.headers
    return render_template("index.html", headers=dict(headers),
                           ip=request.remote_addr)


@app.route('/social.html')
def social():
    headers = request.headers
    return render_template("social.html", headers=dict(headers),
                           ip=request.remote_addr)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
