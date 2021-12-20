from os import environ
from flask import Flask
from connection import Connection

uri = environ["CLOUDS_URI"]
user = environ["CLOUDS_USER"]
password = environ["CLOUDS_PASSWORD"]

app = Flask(__name__)

app.config.update(
    DEBUG=True,
    TEMPLATES_AUTO_RELOAD=True
)

@app.route("/")
def index():
    connection = Connection(uri, user, password)
    out =  "<p>"
    out += str(connection.find_employees_by_name("Maciej", "Bardas")) + " "
    out += str(connection.check_if_exists(card_id=1)) + " "
    out += str(connection.next_card_id()) + " "
    out += str(connection.list_all())
    out += "</p>"
    connection.close()
    return out

if __name__ == '__main__':
    app.run(debug=True)