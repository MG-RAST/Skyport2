from flask import Flask
from blueprints.api import api

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')


@app.after_request
def add_header(response):
    response.cache_control.max_age = 30
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0')

