import os
from flask import Flask
from flask import request, render_template

app = Flask(__name__)


def load_all_fonts():
    with open(os.path.join("static", "fontlist.txt")) as fp:
        fonts = [line.strip() for line in fp]
        return fonts


@app.route('/')
def hello_world():
    headers = request.headers
    fonts = load_all_fonts()
    return render_template("home_page.html", headers=dict(headers), fonts=fonts)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
