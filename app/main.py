from flask import flask

app = Flask(__name__)


@app.route("/")
def front_page():
    return "<p>Home | Discoverd | Requests | Groups </p>"
