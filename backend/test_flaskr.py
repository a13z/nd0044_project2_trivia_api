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
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)


        self.categories = {'1': "Science",'2': "Art", '3': "Geography", '4': "History", '5': "Entertainment", '6' : "Sports" }

        self.new_question = {
            'question': 'What director, based on a book, the real world is called Oasis?',
            'answer': 'Steven Spielber',
            'difficulty': 4,
            'category': 5
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        # self.app = Flask(__name__)
        # self.db.init_app(self.app)
        with self.app.app_context(): 
            self.db.session.remove()
            self.db.drop_all()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data, self.categories)

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 19)
        self.assertEqual(len(data['questions']), 10)
    
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def test_get_question_search_with_results(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'Movie'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 1)
    
    def test_get_question_search_without_results(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'ThisDoesntExist'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(len(data['questions']), 0)

    def test_delete_question(self):
        # We first create a question to delete later
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertEqual(data['total_questions'], 20)
        self.assertEqual(len(data['questions']), 10)
        
        # remove the question we added to keep the data consistent for the rest of the test
        question = Question.query.filter(Question.id == data["created"]).one_or_none()
        self.assertEqual(question.question, self.new_question['question'])

        res3 = self.client().delete(f'/questions/{data["created"]}')
        data3 = json.loads(res3.data)
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(data3['success'], True)
        self.assertTrue(data3['total_questions'])
        self.assertTrue(len(data3['questions']), 19)

    def test_delete_question_404_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertEqual(data['total_questions'], 20)
        self.assertEqual(len(data['questions']), 10)

        # search the question we just created
        res2 = self.client().post('/questions/search', json={'searchTerm': 'Oasis'})
        data2 = json.loads(res2.data)

        self.assertEqual(res2.status_code, 200)
        self.assertEqual(data2['success'], True)
        self.assertTrue(data2['total_questions'])
        self.assertEqual(len(data2['questions']), 1)
        
        # remove the question we added to keep the data consistent for the rest of the test
        question = Question.query.filter(Question.id == data["created"]).one_or_none()
        self.assertEqual(question.question, self.new_question['question'])

        res3 = self.client().delete(f'/questions/{data["created"]}')
        data3 = json.loads(res3.data)
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(data3['success'], True)
        self.assertTrue(data3['total_questions'])
        self.assertTrue(len(data3['questions']), 19)


    def test_get_questions_based_on_categories(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(len(data['questions']), 3)

    def test_404_if_question_based_on_categories_does_not_exist(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def test_quizzes_get_question_from_all_categories(self):
        res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': {'type': 'click', 'id': 0}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # the question is an object with 5 keys
        self.assertEqual(len(data['question']), 5)

    def test_quizzes_get_different_question_from_all_categories_with_previous_questions(self):
        res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': {'type': 'click', 'id': 0}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # the question is an object with 5 keys
        self.assertEqual(len(data['question']), 5)

        res2 = self.client().post('/quizzes', json={'previous_questions': [ data['question']['id'] ], 'quiz_category': {'type': 'click', 'id': 0}})
        data2 = json.loads(res2.data)

        self.assertEqual(res2.status_code, 200)
        self.assertEqual(data2['success'], True)
        # the question is an object with 5 keys
        self.assertEqual(len(data2['question']), 5)

        self.assertNotEqual(data['question']['id'], data2['question']['id'])

    def test_quizzes_get_question_from_one_categories(self):
        res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': {'type': 'Science', 'id': 1}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # the question is an object with 5 keys
        self.assertEqual(len(data['question']), 5)
        self.assertEqual(data['question']['category'], 1)

    def test_quizzes_get_different_question_from_one_categories(self):
        res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': {'type': 'Science', 'id': 1}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # the question is an object with 5 keys
        self.assertEqual(len(data['question']), 5)
        self.assertEqual(data['question']['category'], 1)

        res2 = self.client().post('/quizzes', json={'previous_questions': [ data['question']['id'] ], 'quiz_category': {'type': 'Science', 'id': 1}})
        data2 = json.loads(res2.data)

        self.assertEqual(res2.status_code, 200)
        self.assertEqual(data2['success'], True)
        # the question is an object with 5 keys
        self.assertEqual(len(data2['question']), 5)
        self.assertEqual(data2['question']['category'], 1)

        # questions are different
        self.assertNotEqual(data['question']['id'], data2['question']['id'])
        # but from the same category
        self.assertEqual(data['question']['category'], data2['question']['category'])

    def test_quizzes_get_no_question_if_category_doesnt_exist(self):
        res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': {'type': 'click', 'id': 10}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], None)

    def test_quizzes_return_no_question_when_previous_were_asked(self):
        res = self.client().post('/quizzes', json={'previous_questions': [10, 11], 'quiz_category': {'type': 'Sports', 'id': 6}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], None)        


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()