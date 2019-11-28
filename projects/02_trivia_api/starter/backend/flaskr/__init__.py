
from flask import Flask, request, abort, jsonify
from flask_cors import cross_origin
from models import setup_db, Question, Category
import random

QUESTIONS_PER_PAGE = 10
app = Flask(__name__)
setup_db(app)


# def create_app(test_config=None):
#     # create and configure the app
#     app = Flask(__name__)
#     setup_db(app)

def questions_by_page(request, selection):
    # Get the current, start, and end page from request
    current_page = request.args.get('page', 1, type=int)
    start_page = (current_page - 1) * QUESTIONS_PER_PAGE
    end_page = start_page + QUESTIONS_PER_PAGE

    # Use the Model format method to pretty the questions
    questions = [question.format() for question in selection]

    # Parse the questions by page
    questions = questions[start_page:end_page]

    # return pretty parsed questions
    return questions

def get_categories(id=None):

    # Get data based on Category ID or no Category ID
    if id:
        data = Category.query.filter_by(
            id=id).order_by(Category.type.asc()).all()
    else:
        data = Category.query.order_by(Category.type.asc()).all()

    # Abort if there are no categories
    if (data is None):
        abort(400)

    categories = {}
    # loop through categories and append the id and type to the list
    for row in data:
        categories[row.type] = str(row.id)

    return categories

# Get Categories
@app.route('/categories')
def categories():
    try:
        response = {
            "success": True,
            "categories": get_categories()
        }

        return jsonify(response)
    except:
        abort(422)

# Get questions by category id
@app.route('/questions/category=<int:id>')
def questions_by_id(id):
    try:
        question_data = Question.query.filter_by(category=id).order_by(Question.question.asc()).all()
        category_data = get_categories(id)

        # abort 404 if no questions
        if (question_data is None):
            abort(404)

        response = {
            'success': True,
            'questions': questions_by_page(request, question_data),
            'total_questions': len(question_data),
            'current_category': list(category_data.values())[0]
        }
        return jsonify(response)
    except:
        abort(422)

# Add a question
@app.route('/questions/create', methods=['POST'])
@cross_origin()  # Handling CORs at the route level is more granular.
def add_question():
    try:
        success = True

        # Get the JSON request
        req_data = request.get_json()

        # If the question or answer are missing throw an error
        if 'question' in req_data and 'answer' in req_data:

            # Make sure questions and answer are not blank
            if req_data['question'] != '' and req_data['answer'] != '':
                Question(req_data['question'], req_data['answer'],
                            req_data['category'], req_data['difficulty']).insert()
            else:
                success = False
        else:
            success = False

        # return success or error
        return jsonify({'success': success})
    except:
        abort(422)

# Search for questions
@app.route('/questions/search', methods=['POST'])
@cross_origin()  # Handling CORs at the route level is more granular.
def search_questions():
    try:
        req_data = request.get_json()

        question_data = Question.query.filter(
            Question.question.ilike("%" + req_data['searchTerm'] + "%")).order_by(Question.question.asc()).all()

        response = {
            'success': True,
            'questions': questions_by_page(request, question_data),
            'total_questions': len(question_data)
        }

        return jsonify(response)
    except:
        abort(422)

# Get Questions. 10 at a time. Pagination
@app.route('/questions')
def questions():
    try:
        data = Question.query.order_by(Question.question.asc()).all()

        # abort 404 if no questions
        if (data is None):
            abort(404)

        response = {
            'success': True,
            'questions': questions_by_page(request, data),
            'total_questions': len(data),
            'categories': get_categories()
        }

        return jsonify(response)
    except:
        abort(422)

# Delete Question by ID
@app.route('/questions/<int:id>', methods=['DELETE'])
def delete_question(id):
    try:
        data = Question.query.filter_by(id=id).one_or_none()

        # abort 404 if no questions
        if (data is None):
            abort(404)
        else:
            data.delete()
            return jsonify({'success': True, 'deleted': id})
    except:
        abort(422)

# Quiz the player with Random questions
@app.route('/quizzes', methods=['POST'])
@cross_origin()  # Handling CORs at the route level is more granular.
def quizzes():
    # Get the Request JSON
    request_data = request.get_json()

    # Get the previous question from the JSON
    previous_questions = request_data['previous_questions']

    # Get the Category Int. 0 is for all.
    category = request_data['quiz_category']['id']
    print(request_data['quiz_category']['id'])

    # Query the DB and filter on category. The DB does not have a 0 category
    if category != 0:
        current_q_data = Question.query.filter_by(category=category)
    else:
        current_q_data = Question.query

    # Get questions from DB that have not be asked before
    current_q_data = current_q_data.filter(
        ~Question.id.in_(previous_questions))

    # Get the number of questions that have not been asked before
    row_count = int(current_q_data.count())

    # If all of the questions have been asked return empty list
    if row_count != 0:
        # Find the next random question
        randomRow = current_q_data.offset(
            int(row_count*random.random())).first()

        # Fromat question into a friendly Model format
        current_question = randomRow.format()
    else:
        # If all of the questions have been asked return an empty list
        current_question = None

    # Build the return response
    response = {
        'success': True,
        'question': current_question
    }

    # Send the response back to the JS
    return jsonify(response)

# @TODO: Create error handlers for all expected errors including 404 and 422.
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

    # return app
