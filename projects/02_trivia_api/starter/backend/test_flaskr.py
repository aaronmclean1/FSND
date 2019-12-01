import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class Trivia_Test(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}/{}".format(
            'postgres:myPassword@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # sample question for use in tests

        self.question_1 = {
            "question": "my question",
            "answer": "my answer",
            "category": "1",
            "difficulty": "2"
        }

        self.question_2 = {
            "answer": "my answer",
            "category": "1",
            "difficulty": "2"
        }

        self.quiz_1 = {
            'previous_questions': [11, 10],
            'quiz_category': {
                'id': 2
            }
        }

        self.quiz_2 = {
            'previous_questions': []
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    # Test pagination - PASS
    def test_questions_by_page_pass(self):

        # Get page 1
        response = self.client().get('/questions?page=1')
        data = json.loads(response.data.decode('utf-8'))

        # Make sure 200 is status and success is returned
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # Make sure total_questions, categories, and questions are returned
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['questions'])

    # Test pagination - FAIL
    def test_questions_by_page_fail(self):

        # Get page 200
        response = self.client().get('/questions?page=200')
        data = json.loads(response.data.decode('utf-8'))

        # Make sure 404 is status and success False is returned
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)

    # Test categories - PASS
    def test_categories_pass(self):

        # Get categories
        response = self.client().get('/categories')
        data = json.loads(response.data.decode('utf-8'))

        # Make sure 200 is status and success is returned
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # Check for at least 6 categories
        self.assertEqual(len(data['categories']) >= 6, True)

    # Test categories - FAIL
    def test_categories_fail(self):

        # overload categories
        response = self.client().get('/categories/3')
        data = json.loads(response.data.decode('utf-8'))

        # Make sure 404 is status and success is returned false
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)

    # Test categories by ID - PASS
    def test_categories_by_id_pass(self):

        # Get questions by category id
        response = self.client().get('/questions/category=3')
        data = json.loads(response.data.decode('utf-8'))

        # Make sure 200 is status and success is returned
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    # Test categories by ID - FAIL
    def test_categories_by_id_fail(self):

        # Get questions by category id that does not exist
        response = self.client().get('/questions/category=3333')
        data = json.loads(response.data.decode('utf-8'))

        # Make sure 404 is status and success is returned false
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)

    # Test create question - PASS
    def test_create_question_pass(self):
        response = self.client().post('/questions/create', json=self.question_1)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    # Test create question - FAIL
    def test_create_question_fail(self):
        response = self.client().post('/questions/create', json=self.question_2)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)

   # Test search questions - PASS
    def test_search_questions_pass(self):

        # Get questions by search
        response = self.client().post('/questions/search',
                                      json=({'searchTerm': 'the'}))
        data = json.loads(response.data.decode('utf-8'))

        # Make sure 200 is status and success is returned
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

   # Test search questions - FAIL
    def test_search_questions_fail(self):

        # Get questions by search
        response = self.client().post('/questions/search',
                                      json=({'searchTerm': 'Jedi'}))
        data = json.loads(response.data.decode('utf-8'))

        # Make sure 404 is status and success false is returned
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)

   # Test delete question - PASS
    def test_delete_questions_pass(self):

        # Get questions by search
        response = self.client().delete('/questions/39')
        data = json.loads(response.data.decode('utf-8'))

        # Make sure 200 is status and success is returned
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['deleted'])

   # Test delete question - FAIL
    def test_delete_questions_fail(self):

        # Get questions by search
        response = self.client().delete('/questions/333333')
        data = json.loads(response.data.decode('utf-8'))

        # Make sure 404 is status and success is returned
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)

   # Test quiz - PASS
    def test_quiz_pass(self):

        # Get questions by search
        response = self.client().post('/quizzes', json=self.quiz_1)
        data = json.loads(response.data.decode('utf-8'))

        # Make sure 200 is status and success is returned
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

   # Test quiz - FAIL
    def test_quiz_fail(self):

        # Get questions by search
        response = self.client().post('/quizzes', json=self.quiz_2)
        data = json.loads(response.data.decode('utf-8'))

        # Make sure 200 is status and success is returned
        self.assertEqual(response.status_code, 500)
        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
