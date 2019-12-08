import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS, cross_origin

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

#  Get Short Drinks
@app.route('/drinks', methods=['GET'], strict_slashes=False)
def short_drinks():
    data = Drink.query.order_by(Drink.title.asc()).all()

    # abort 404 if no drinks
    if (data is None):
        abort(404)
    else:
        drinks = [drinks.short() for drinks in data]

        response = {
            'success': True,
            'drinks': drinks
        }

        return jsonify(response)

# Get Short Drinks by ID
@app.route('/drinks/<int:id>', methods=['GET'])
def short_drinks_by_id(id):
    data = Drink.query.filter_by(id=id).first()

    # abort 404 if no drinks
    if (data is None):
        abort(404)
    else:
        drinks = data.short()
        response = {
            'success': True,
            'drinks': drinks
        }
        return jsonify(response)


#  Get Long Drinks
@app.route('/drinks-detail', methods=['GET'], strict_slashes=False)
@requires_auth('get:drinks-detail')
def long_drinks(jwt):
    data = Drink.query.order_by(Drink.title.asc()).all()
    # abort 404 if no drinks
    if (data is None):
        abort(404)
    else:
        drinks = [drinks.long() for drinks in data]
        response = {
            'success': True,
            'drinks': drinks
        }
        return jsonify(response)


# Add a drink
@app.route('/drinks', methods=['POST'])
@cross_origin()  # Handling CORs at the route level is more granular.
@requires_auth('post:drinks')
def add_drinks(jwt):

    # Get the JSON request
    req_data = request.get_json()

    # If the title or recipe are missing throw an error
    if 'title' in req_data and 'recipe' in req_data:

        # Make sure title and recipe are not blank
        if req_data['title'] != '' and req_data['recipe'] != '':
            try:
                new_drink = Drink(title= req_data['title'], recipe=json.dumps(req_data['recipe'])).insert()
                response = {
                    'success': True,
                    'drinks': new_drink
                }
                return jsonify(response)
            except exc.IntegrityError as e:
                abort(409)
        else:
            abort(400)
    else:
        abort(400)

# @TODO 'patch:drinks' permission

# Update a drink
@app.route('/drinks/<int:id>', methods=['PATCH'])
@cross_origin()  # Handling CORs at the route level is more granular.
@requires_auth('patch:drinks')
def update_drinks(jwt, id):
    req_data = request.get_json()
    data = Drink.query.filter_by(id=id).one_or_none()

    # abort 404 if no drinks
    if (data is None):
        abort(404)
    else:
        # If the title or recipe are missing throw an error
        if 'title' in req_data and 'recipe' in req_data:
            if req_data['title'] != '' and req_data['recipe'] != '':
                data.title = req_data['title']
                data.recipe = json.dumps(req_data['recipe'])
                try:
                    data.update()
                    drinks = data.long()
                    response = {
                        'success': True,
                        'drinks': drinks
                    }
                    return jsonify(response)
                except exc.IntegrityError as e:
                    abort(409)
            else:
                abort(400)
        else:
            abort(400)


# Delete drinks by ID
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, id):
    data = Drink.query.filter_by(id=id).one_or_none()
    # abort 404 if no drinks
    if (data is None):
        abort(404)
    else:
        data.delete()
        response = {
            'success': True,
            'deleted': id
        }
        return jsonify(response)

# Error Handling
@app.errorhandler(400)
def bad_request(error):
    response = {
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }
    return jsonify(response), 400

@app.errorhandler(401)
def bad_request(error):
    response = {
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }
    return jsonify(response), 401

@app.errorhandler(404)
def resource_not_found(error):
    response = {
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }
    return jsonify(response), 404

@app.errorhandler(409)
def resource_not_found(error):
    response = {
        "success": False,
        "error": 409,
        "message": "Conflict"
    }
    return jsonify(response), 409

@app.errorhandler(422)
def unprocessable_entity(error):
    response = {
        "success": False,
        "error": 422,
        "message": "Unprocessable Entity"
    }
    return jsonify(response), 422

@app.errorhandler(500)
def internal_server_error(error):
    response = {
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }
    return jsonify(response), 500

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response