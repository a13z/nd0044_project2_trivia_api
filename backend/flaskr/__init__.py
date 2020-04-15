import os, sys

from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import db, setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    
    '''
    @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS()
    cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    '''
    @DONE: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start =  (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    '''
    @DONE: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    @app.route('/categories')
    def get_categories():
      categories = Category.query.all()
      categories_formatted = {category.id:category.type for category in categories}
      return categories_formatted

    '''
    @DONE: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    @app.route('/questions',  methods=['GET'])
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_selection = paginate_questions(request, selection)

        categories = Category.query.all()
        categories_formatted = {category.id:category.type for category in categories}

        if len(current_selection) == 0:
            abort(404)
          
        return jsonify({
            "success": True,
            "questions": current_selection,
            "total_questions": len(selection),
            "current_category": None,
            "categories": categories_formatted
        })
    '''
    @DONE: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:question_id>',  methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()
        if question is None:
            abort(404)

        try:
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_selection = paginate_questions(request, selection)
            return jsonify({
                "success": True,
                "deleted": question.id,
                "questions": current_selection,
                "total_questions": len(selection),
                "current_category": None,
            })

        except exception as e:
            error = true
            print(sys.exc_info())
            print(e)
            abort(422)
        finally:
            db.session.close()

    '''
    @DONE: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions',  methods=['POST'])
    def add_question():
        body = request.get_json()

        question = body.get("question", None)
        answer = body.get("answer", None)
        category = int(body.get("category", "1"))
        difficulty = int(body.get("difficulty", "1"))

        try:
            question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_selection = paginate_questions(request, selection)

            return jsonify({
                "success": True,
                "created": question.id,
                "questions": current_selection,
                "total_questions": len(selection),
          })

        except exception as e:
            error = true
            print(sys.exc_info())
            print(e)
            abort(422)

    '''
    @DONE: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    @app.route('/questions/search',  methods=['POST'])
    def search_question():
      
        body = request.get_json()
        term = body.get('searchTerm', None)

        try:
            selection = Question.query.filter(Question.question.ilike(f'%{term}%')).order_by(Question.id).all()
            current_selection = paginate_questions(request, selection)

            return jsonify({
                "success": True,
                "questions": current_selection,
                "total_questions": len(selection),
                "current_category": None,
          })

        except exception as e:
            error = true
            print(sys.exc_info())
            print(e)
            abort(422)

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_per_category(category_id):
        try:
            selection = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
            current_selection = paginate_questions(request, selection)

            if len(current_selection) == 0:
                abort_code = 404
            else: 
                abort_code = None

            if abort_code is None:
                return jsonify({
                "success": True,
                "questions": current_selection,
                "total_questions": len(selection),
                "current_category": None,
                })

        except exception as e:
            error = true
            print(sys.exc_info())
            print(e)
            abort(422)
        finally:
            db.session.close()
        
        if abort_code:
            abort(abort_code)

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()

        previous_questions = body.get('previous_questions', [])            
        quiz_category = body.get('quiz_category', {'id': "0", 'type': "click"})
        quiz_category_id = int(quiz_category['id'])

        try:
            if quiz_category_id > 0:
                if len(previous_questions) == 0:
                    selection = Question.query.filter(Question.category == quiz_category_id).order_by(Question.id).all()
                else:
                    selection = Question.query.filter(Question.category == quiz_category_id, Question.id.notin_(previous_questions)).order_by(Question.id).all()
            else:
                if len(previous_questions) == 0:
                    selection = Question.query.order_by(Question.id).all()
                else:
                    selection = Question.query.filter(Question.id.notin_(previous_questions)).order_by(Question.id).all()

            if len(selection) == 0:
                return jsonify({
                    "success": True,
                    "question": None
                    })

            random_question = random.choice(selection).format()

            return jsonify({
              "success": True,
              "question": random_question
            })

        except Exception as e:
            error = True
            print(sys.exc_info())
            print(e)
            abort(422)

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400


    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422 

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500   

    return app

    