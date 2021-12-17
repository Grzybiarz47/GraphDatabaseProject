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
    str = connection.find_person("Keanu Reeves")
    connection.close()
    str = "<p>" + str + "</p>"
    return str

if __name__ == '__main__':
    app.run(debug=True)