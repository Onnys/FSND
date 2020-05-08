import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = 'trivia_test'
        self.database_path = "postgres://{}:{}@{}/{}".format('onnys',
                                                             'onnys', 'localhost:5432', self.database_name)

        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        status = 200
        success = True
        if res.status_code == 404:
            status = 404
            success = False

        self.assertEqual(res.status_code, status)
        self.assertEqual(data['success'], success)

    def test_retrieve_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        status = 200
        success = True
        if res.status_code == 404:
            status = 404
            success = False
        self.assertEqual(res.status_code, status)
        self.assertEqual(data['success'], success)

    def test_delete_question(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)

        status = 200
        success = True
        if res.status_code == 422:
            status = 422
            success = False
        self.assertEqual(res.status_code, status)
        self.assertEqual(data['success'], success)

    def test_add_question(self):
        res = self.client().post('/questions',
                                 json={'question': 'Who is God you?', 'answer': 'God is the greatest', 'category': 1, 'difficulty': 5})
        data = json.loads(res.data)

        if res.status_code == 200:
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)
        else:
            self.assertEqual(res.status_code, 422)
            self.assertEqual(data['success'], False)

    def test_search_questions(self):
        res = self.client().post('/questions/search',
                                 json={'searchTerm': 'Who'})
        data = json.loads(res.data)
        if res.status_code == 200:
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)
        else:
            self.assertEqual(res.status_code, 422)
            self.assertEqual(data['success'], False)

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        if res.status_code == 200:
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)
        else:
            self.assertEqual(res.status_code, 422)
            self.assertEqual(data['success'], False)

    def test_get_next_question(self):
        post_data = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Science',
                'id': 1
            }
        }
        res = self.client().post('/quizzes', json=post_data)
        data = json.loads(res.data)
        if res.status_code == 200:
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data["success"], True)
            self.assertTrue(data["question"])
        else:
            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['success'], False)


        # Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
