import psycopg2
from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from db import *
from users import Users
from organizations import Organizations, organization_schema, organizations_schema
from users import Users, user_schema, users_schema

from pprint import pprint

# CREATES APP
app = Flask(__name__)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://mike:Chevron19851832@localhost:5432/alchemy"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

init_db(app, db)
ma = Marshmallow(app)


def create_all():
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        print("All done!")


@app.route("/user/add", methods=["POST"])
def user_add():
    post_data = request.json
    if not post_data:
        post_data = request.post

    first_name = post_data.get("first_name")
    last_name = post_data.get("last_name")
    email = post_data.get("email")
    phone = post_data.get("phone")
    city = post_data.get("city")
    state = post_data.get("state")
    org_id = post_data.get("org_id")
    active = post_data.get("active")

    add_user(first_name, last_name, email, phone, city, state, org_id, active)

    new_user = db.session.query(Users).filter(Users.email == email).first()

    if new_user:

        return jsonify(user_schema.dump(new_user)), 201
    else:
        return jsonify("Error in User Creation"), 400


def add_user(first_name, last_name, email, phone, city, state, org_id, active):
    new_user = Users(first_name, last_name, email, phone, city, state, org_id, active)

    db.session.add(new_user)

    db.session.commit()


@app.route("/user/get/all/active", methods=["GET"])
def get_all_active_users():
    users = db.session.query(Users).filter(Users.active == True).all()
    # users_list = []

    # if users:
    #     for user in users:
    #         user = {
    #             "user_id": user.user_id,
    #             "first_name": user.first_name,
    #             "last_name": user.last_name,
    #             "email": user.email,
    #             "phone": user.phone,
    #             "city": user.city,
    #             "state": user.state,
    #             "organization": {
    #                 "org_id": user.organization.org_id,
    #                 "name": user.organization.name,
    #                 "phone": user.organization.phone,
    #                 "city": user.organization.city,
    #                 "state": user.organization.state,
    #             },
    #             "active": user.active,
    #         }
    #         users_list.append(user)
    if users:

        return jsonify(users_schema.dump(users)), 200
    else:
        return jsonify("No users found")


# GET USERS BY ID
@app.route("/user/get/<user_id>", methods=["GET"])
def get_users_by_id(user_id):
    user = db.session.query(Users).filter(Users.user_id == user_id).first()

    if user:
        # user = {
        #     "user_id": user.user_id,
        #     "first_name": user.first_name,
        #     "last_name": user.last_name,
        #     "email": user.email,
        #     "phone": user.phone,
        #     "city": user.city,
        #     "state": user.state,
        #     "organization": {
        #         "org_id": user.organization.org_id,
        #         "name": user.organization.name,
        #         "phone": user.organization.phone,
        #         "city": user.organization.city,
        #         "state": user.organization.state,
        #     },
        #     "active": user.active,
        # }

        return jsonify(users_schema.dump(user)), 200
    else:
        return jsonify("No user found"), 404


# UPDATING A USER
@app.route("/user/update/<user_id>", methods=["POST"])
def user_update(user_id):
    user = db.session.query(Users).filter(Users.user_id == user_id).first()

    post_data = request.json
    if not post_data:
        post_data = request.post

    if user:
        if post_data.get("user_id"):
            user.user_id = post_data.get("user_id")
        if post_data.get("first_name"):
            user.first_name = post_data.get("first_name")
        if post_data.get("last_name"):
            user.last_name = post_data.get("last_name")
        if post_data.get("email"):
            user.email = post_data.get("email")
        if post_data.get("phone"):
            user.phone = post_data.get("phone")
        if post_data.get("city"):
            user.city = post_data.get("city")
        if post_data.get("state"):
            user.state = post_data.get("state")
        if post_data.get("org_id"):
            user.org_id = post_data.get("org_id")
        if post_data.get("active") is not None:
            user.active = post_data.get("active")

        db.session.commit()

        if not post_data:

            return jsonify("No values sent in body"), 400
        else:
            return jsonify(user_schema.dump(user)), 200
    else:
        return jsonify("User not found"), 404


# DELETING A USER
@app.route("/user/delete/<user_id>", methods=["DELETE"])
def user_delete(user_id):
    user = db.session.query(Users).filter(Users.user_id == user_id).first()

    if user:
        db.session.delete(user)

        db.session.commit()

        return jsonify(user_schema.dump(user)), 200
    else:
        return jsonify("User does not exist"), 404


# DEACTIVATING A USER
@app.route("/user/deactivate/<user_id>", methods=["PATCH"])
def user_deactivate(user_id):
    user = db.session.query(Users).filter(Users.user_id == user_id).first()

    if user:
        if user.active == True:
            user.active = False

            db.session.commit()

        else:
            return jsonify("User is already inactive"), 400

        return jsonify(user_schema.dump(user)), 200
    else:
        return jsonify("User not found"), 404


# ACTIVATING A USER
@app.route("/user/activate/<user_id>", methods=["PATCH"])
def user_activate(user_id):
    user = db.session.query(Users).filter(Users.user_id == user_id).first()

    if user:
        if user.active == False:
            user.active = True

            db.session.commit()

        else:
            return jsonify("User is already active"), 400

        return jsonify(user_schema.dump(user)), 200
    else:
        return jsonify("User not found"), 404


# ADD AN ORGANIZATION
@app.route("/organization/add", methods=["POST"])
def organization_add():
    post_data = request.json
    if not post_data:
        post_data = request.post

    name = post_data.get("name")
    phone = post_data.get("phone")
    city = post_data.get("city")
    state = post_data.get("state")
    active = post_data.get("active")
    if active is not None and active == False:
        active = False
    elif active is not None and active == True:
        active = True
    else:
        active = True

    add_organization(name, phone, city, state, active)

    new_organization = (
        db.session.query(Organizations)
        .filter(Organizations.name == name)
        .filter(Organizations.phone == phone)
        .filter(Organizations.city == city)
        .filter(Organizations.state == state)
        .filter(Organizations.active == active)
        .first()
    )

    if new_organization:

        return jsonify(organization_schema.dump(new_organization)), 201
    else:
        return jsonify("Error in Organization Creation"), 400


def add_organization(name, phone, city, state, active):
    new_org = Organizations(name, phone, city, state, active)

    db.session.add(new_org)

    db.session.commit()


# GET ALL ACTIVE ORGANIZATIONS
@app.route("/organization/get/all", methods=["GET"])
def get_all_active_organizations():
    organizations = (
        db.session.query(Organizations).filter(Organizations.active == True).all()
    )
    # organizations_list = []

    # if organizations:
    #     for organization in organizations:
    #         organization = {
    #             "org_id": organization.org_id,
    #             "name": organization.name,
    #             "phone": organization.phone,
    #             "city": organization.city,
    #             "state": organization.state,
    #             "active": organization.active,
    #         }
    #         organizations_list.append(organization)

    if organizations:
        return jsonify(organizations_schema.dump(organizations)), 200

    else:
        return jsonify("No active organizations found"), 404


# GET ALL ORGANIZATIONS BY ID
@app.route("/organization/get/<org_id>", methods=["GET"])
def organization_get_by_id(org_id):
    organization = (
        db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
    )

    # if organization:
    #     organization = {
    #         "org_id": organization.org_id,
    #         "name": organization.name,
    #         "phone": organization.phone,
    #         "city": organization.city,
    #         "state": organization.state,
    #         "active": organization.active,
    #     }

    if organization:
        return jsonify(organization_schema.dump(organization)), 200
    else:
        return jsonify("No organization found"), 404


# UPDATING AN ORGANIZATION
@app.route("/organization/update/<org_id>", methods=["POST"])
def organization_update(org_id):
    organization = (
        db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
    )

    post_data = request.json
    if not post_data:
        post_data = request.post

    if organization:
        if post_data.get("org_id"):
            organization.org_id = post_data.get("org_id")
        if post_data.get("name"):
            organization.name = post_data.get("name")
        if post_data.get("phone"):
            organization.phone = post_data.get("phone")
        if post_data.get("city"):
            organization.city = post_data.get("city")
        if post_data.get("state"):
            organization.state = post_data.get("state")
        if post_data.get("active") is not None:
            organization.active = post_data.get("active")

        db.session.commit()

        if not post_data:

            return jsonify("No values sent in body"), 400
        else:
            return jsonify(organization_schema.dump(organization)), 200
    else:
        return jsonify("Organization not found"), 404


# DELETING AN ORGANIZATION
@app.route("/organization/delete/<org_id>", methods=["DELETE"])
def organization_delete(org_id):
    organization = (
        db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
    )

    if organization:
        db.session.delete(organization)

        db.session.commit()

        return jsonify(organization_schema.dump(organization)), 200
    else:
        return jsonify("Organization does not exist"), 404


# DEACTIVATING AN ORGANIZATION
@app.route("/organization/deactivate/<org_id>", methods=["PATCH"])
def organization_deactivate(org_id):
    organization = (
        db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
    )

    if organization:
        if organization.active == True:
            organization.active = False

            db.session.commit()

        else:
            return jsonify("Organization is already inactive"), 400

        return jsonify(organization_schema.dump(organization)), 200
    else:
        return jsonify("Organization not found"), 404


# ACTIVATING AN ORGANIZATION
@app.route("/organization/activate/<org_id>", methods=["PATCH"])
def organization_activate(org_id):
    organization = (
        db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
    )

    if organization:
        if organization.active == False:
            organization.active = True

            db.session.commit()

        else:
            return jsonify("Organization is already active"), 400

        return jsonify(organization_schema.dump(organization)), 200
    else:
        return jsonify("Organization not found"), 404


# INITIALIZES APP
if __name__ == "__main__":
    create_all()
    app.run(debug=True, port="4000")
