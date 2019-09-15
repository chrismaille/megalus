import random

from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    def get(self):
        return {'hello': "api1"}


class Number(Resource):
    def get(self):
        return {'number': random.randint(10)}


api.add_resource(HelloWorld, '/')
api.add_resource(Number, '/number')

if __name__ == '__main__':
    app.run(debug=True)
