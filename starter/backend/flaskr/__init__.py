import os
from flask import Flask, request, abort, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from flask_restful import reqparse, abort, Api, Resource
from flask_migrate import Migrate
from models import setup_db, Question, Category ,  db

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]
  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  migrate=Migrate(app,db)
  #TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  CORS(app, resources={r"/api/*": {"origins": "*"}})

  #TODO: Use the after_request decorator to set Access-Control-Allow
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,PATCH,DELETE,OPTIONS')
    return response
  
  
  #@TODO: Create an endpoint to handle GET requests for all available categories.
  @app.route('/categories')
  def get_categories():
    categories={}
    for category in Category.query.all():
      categories[str(category.id)]= category.type
    
    result={
      'categories': categories,
      'success':True
    }
    
    return jsonify(result)
  
  '''
 Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  
  
  @app.route('/questions')
  def get_questions():
    selection=db.session.query(Question).order_by(Question.id).all()
    current_questions=paginate_questions(request, selection)
    if len(current_questions)<=0:
      abort(404)  
    
    categories={}
    for category in Category.query.all():
      categories[str(category.id)]= category.type
    
    result={
      'success':True,
      'questions':current_questions,
      'total_questions':len(Question.query.all()),
      'categories': categories,
      'current_category':None
    }
    
    return jsonify(result)

  ''' 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>',methods=['DELETE'])
  def delete_question(question_id):
    question=Question.query.get(question_id)
    if not question:
      abort(404)
    question.delete()
    
    return jsonify({
      'success':True,
      'deleted_question':question_id,
      'total_questions':len(Question.query.all())
      })

    

  '''
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  '''
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
    body=request.get_json()
    new_question=body.get('question',None)
    new_answer=body.get('answer',None)
    new_difficulty=body.get('difficulty',None)
    new_category=body.get('category',None)
    searchTerm=body.get('searchTerm',None)
    categories={}
    for category in Category.query.all():
      categories[str(category.id)]= category.type
    
    try:      
      if searchTerm:
        selection=db.session.query(Question).order_by(Question.id).filter(Question.question.ilike('%{}%'.format(searchTerm))).all()
        current_questions=paginate_questions(request, selection)
        result={
          'questions':current_questions,
          'total_questions':len(Question.query.all()),
          }
      
      else:
        question=Question(question=new_question,answer=new_answer,difficulty=int(new_difficulty),category=new_category)
        question.insert()
        selection=db.session.query(Question).order_by(Question.id).all()
        current_questions=paginate_questions(request, selection)
        result={
          'success':True,
          'new_question':question.id,
          'questions':current_questions,
          'total_questions':len(Question.query.all()),
          }
      
      return jsonify(result)
    
    except:
      abort(422)
 

  '''
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
 
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    category=Category.query.get(category_id)
    selection=db.session.query(Question).order_by(Question.id).filter(Question.category==str(category_id)).all()
    current_questions=paginate_questions(request, selection)
    
    if not category or len(current_questions)<=0:
      abort(404)
    
    result={
      'success':True,
      'questions':current_questions,
      f'total_{category.type}_questions':len(selection),
      'current_category': {category.id:category.type}
      }
    
    return jsonify(result)
   
  
  '''
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
 
  @app.route('/quizzes',methods=['POST'])
  def play():
    body=request.get_json()
    category=body.get('quiz_category',None)
    category_id=category.get('id',None)
    previous_questions=body.get('previous_questions',None)
    questions=[]
    
    if category_id:
      total_questions=db.session.query(Question).filter_by(category=category_id).all()
      for question in total_questions:
        if previous_questions and (question.id in previous_questions):
          continue
        questions.append(question)
    
    else:
      total_questions=db.session.query(Question).all()
      for question in total_questions:
        if previous_questions and (question.id in previous_questions):
          continue
        questions.append(question)
    
    if len(questions)>0:
      currentQuestion=random.choice(questions).format()
    else:
      currentQuestion=None
    
    return jsonify({
      'question': currentQuestion,
      })    

  '''
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({'success':False,'message':'Resource not found','error':404}),404
  
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({'success':False,'message':'Unprocessable request','error':422}),422
  
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({'success':False,'message':'Bad request','error':400}),400
  
  @app.errorhandler(500)
  def server_error(error):
    return jsonify({'success':False,'message':'Server error','error':500}),500

  @app.errorhandler(405)
  def not_found(error):
    return jsonify({'success':False,'message':'Method not allowed','error':405}),405

  return app

    