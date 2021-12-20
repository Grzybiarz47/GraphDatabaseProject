from flask import Flask
from connection import Connection
from employee import show_employee

app = Flask(__name__)
app.register_blueprint(show_employee, url_prefix='')

app.config.update(
    DEBUG=True,
    TEMPLATES_AUTO_RELOAD=True
)

@app.route("/")
def index():
    db = Connection()
    """"
    connection.add_employee({
    "card_id":connection.next_card_id(),
    "first":"Alan",
    "last":"Novak",
    "title":"Marketing Manager Worldwide",
    "nation":"German",
    "born":1967,
    "start":2007
    })
    """
    out = "<p>"
    out += str(db.list_all())
    out += "</p>"
    out += "<p>"
    out += str(db.list_subordinates(1))
    out += "</p>"
    return out

if __name__ == '__main__':
    app.run(debug=True)