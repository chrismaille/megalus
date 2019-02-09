import uuid

import arrow
import connexion
from flask import abort, make_response, render_template
from flask_pymongo import PyMongo

PEOPLE = [
    {
        "_id": uuid.uuid4("29b334ed-1d47-415d-82f8-fbfeb54df7af"),
        "first_name": "Doug",
        "last_name": "Farrell",
        "email": "doug.farrell@email.com",
        "timestamp": arrow.utcnow().to('local'),
    },
    {
        "_id": uuid.uuid4("16b48240-811c-4e42-9dea-1d99b78a4a32"),
        "fname": "Kent",
        "lname": "Brockman",
        "email": "kent.brockman@email.com",
        "timestamp": arrow.utcnow().to('local'),
    },
    {
        "_id": uuid.uuid4("c794134b-0972-4eee-9739-37b1982c8eb8"),
        "fname": "Bunny",
        "lname": "Easter",
        "email": "bunny.easter@email.com",
        "timestamp": arrow.utcnow().to('local'),
    },
]

app = connexion.App(__name__, template_folder="templates", specification_dir='./')
app.add_api('swagger.yml')

app.config["MONGO_URI"] = "mongodb://mongo:27017/myDatabase"
mongo = PyMongo(app)


@app.route('/')
def home():
    return render_template('home.html')


def read_all():
    collection = app.db.people
    return [collection[key] for key in collection.keys()]


def read_one(uuid):
    return app.db.people.find_one_or_404({'_id': uuid})


def create(person):
    last_name = person.get("last_name", None)
    first_name = person.get("first_name", None)
    email = person.get("email", None)

    if app.db.people.find_one({'email': email}) \
            or not last_name or not first_name or not email:
        abort(400, "Bad Request")

    new_uuid = app.db.people.insert_one(
        {
            '_id': uuid.uuid4(),
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'timestamp': arrow.utcnow().to('local')
        }
    ).inserted_id
    return make_response(
        new_uuid, 201
    )


def update(uuid, person):
    modified = bool(app.db.people.update_one({"_id": uuid}, person).modified_count)
    if not modified:
        abort(404, "Not Found")


def delete(uuid):
    deleted = bool(app.db.people.delete_one({"_id": uuid}).deleted_count)
    if not deleted:
        abort(404, "Not Found")


if __name__ == '__main__':
    app.run(debug=True)
