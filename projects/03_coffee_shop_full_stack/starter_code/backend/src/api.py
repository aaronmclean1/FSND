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

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
#  Drinks
@app.route('/drinks', methods=['GET'])
def short_drinks():
    data = Drink.query.order_by(Drink.title.asc()).all()
    # Figure out how to show data.short()
    response = {
        'success': True,
        'drinks': data
    }

    return jsonify(response)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
#  Drinks
@app.route('/drinks-detail', methods=['GET'])
def long_drinks():
    data = Drink.query.order_by(Drink.title.asc()).all()
    for row in data:

        print(row.id)
        print(row.title)
        print(row.recipe)

    # questions = [question.format() for question in selection]

    # Figure out how to show data.long()
    response = {
        'success': True,
        'drinks': 'hi'
    }

    return jsonify(response)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
# Add a drink
@app.route('/drinks', methods=['POST'])
@cross_origin()  # Handling CORs at the route level is more granular.
def add_drinks():

    success = True

    # Get the JSON request
    req_data = request.get_json()

    # If the title or recipe are missing throw an error
    if 'title' in req_data and 'recipe' in req_data:

        # Make sure title and recipe are not blank
        if req_data['title'] != '' and req_data['recipe'] != '':

            # This doesn't work. The array is wrong
            Drink(title= req_data['title'], recipe=str(req_data['recipe'])).insert()

            #this works
            # Drink(title= req_data['title']).insert()
            print(str(req_data['recipe']))
            # drink = Drink(title=req_title, recipe=req_recipe)
            # drink.insert()
        else:
            abort(400)
    else:
        abort(400)

    # return success or error
    return jsonify({'success': success})

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
# Update a drink
@app.route('/drinks/<int:id>', methods=['PATCH'])
@cross_origin()  # Handling CORs at the route level is more granular.
def update_drinks():

    success = True

    # Get the JSON request
    req_data = request.get_json()

    # If the title or recipe are missing throw an error
    if 'title' in req_data and 'recipe' in req_data:

        # Make sure title and recipe are not blank
        if req_data['title'] != '' and req_data['recipe'] != '':
            Drinks(req_data['title'], req_data['recipe']).insert()
        else:
            abort(400)
    else:
        abort(400)

    # return success or error
    return jsonify({'success': success})


# Delete drinks by ID
@app.route('/drinks/<int:id>', methods=['DELETE'])
def delete_drinks(id):
    data = Drink.query.filter_by(id=id).one_or_none()
    # abort 404 if no drinks
    if (data is None):
        abort(404)
    else:
        data.delete()
        return jsonify({'success': True, 'deleted': id})

# Error Handling
@app.errorhandler(400)
def bad_request(error):
    response = {
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }
    return jsonify(response), 400

@app.errorhandler(404)
def resource_not_found(error):
    response = {
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }
    return jsonify(response), 404

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
