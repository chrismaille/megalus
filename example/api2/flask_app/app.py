import random

from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    def get(self):
        return {'hello': "api2"}


class Name(Resource):
    def get(self):
        return {
            'name': random.choice(
                ['Jose', 'Maria', 'Joao']
            )}


api.add_resource(HelloWorld, '/')
api.add_resource(Name, '/name')

if __name__ == '__main__':
    app.run(debug=True)
