from flask import Flask
from flask import request, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    headers = request.headers
    return render_template("home_page.html", headers=dict(headers))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
