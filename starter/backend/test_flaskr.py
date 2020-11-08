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
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres','1234','localhost:5432', self.database_name)
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
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_retrieve_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
    
    def test_retrieve_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertFalse(data['current_category'])
    
    def test_404_retrieve_questions_wrong_page(self):
        res = self.client().get('/questions?page=500')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')
    
    
    def test_404_delete_not_existed_question(self):
        res = self.client().delete('/questions/600')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_405_delete_question_wrong_method(self):
        res = self.client().post('/questions/1')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed')

    def test_get_category_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_Science_questions'])
        self.assertEqual(data['current_category'],{'1':'Science'})
    
    def test_404_retrieve_category_questions_wrong_id(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')


    def test_404_retrieve_category_questions_wrong_page(self):
        res = self.client().get('/categories/1/questions?page=500')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')
    
    def test_post_new_question(self):
        res = self.client().post('/questions',json={"question":"How many times Argentina won world cup","answer":"2","difficulty":"1","category":"6"})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['new_question'])

    def test_search_questions(self):
        res = self.client().post('/questions',json={"searchTerm":"body"})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])

    def test_play_quiz(self):
        res = self.client().post('/quizzes',json={"quiz_category":{},"previous_questions":["25"]})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
    
    def test_play_quiz_by_category(self):
        res = self.client().post('/quizzes',json={"quiz_category":{"id":"5","type":"Entertainment"},"previous_questions":[2,6]})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
    
    def test_play_quiz_by_category_checking_not_duplicating(self):
        res = self.client().post('/quizzes',json={"quiz_category":{"id":"5","type":"Entertainment"},"previous_questions":[2,4,6]})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertFalse(data['question'])
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()