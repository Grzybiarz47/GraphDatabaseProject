from flask import Flask, render_template
from connection import Connection
from employee import show_employee
from hire import add_employee

app = Flask(__name__)
app.register_blueprint(show_employee, url_prefix='')
app.register_blueprint(add_employee, url_prefix='')

app.config.update(
    DEBUG=True,
    TEMPLATES_AUTO_RELOAD=True
)

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)