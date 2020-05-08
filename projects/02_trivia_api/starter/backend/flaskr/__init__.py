import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection_of_questions):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection_of_questions]
    formated_questions = questions[start:end]
    return formated_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,POST,DELETE')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        formated_categories = [category.type for category in categories]
        if len(formated_categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': formated_categories,
        })

    @app.route('/questions', methods=['GET'])
    def retrieve_questions():
        selection_of_questions = Question.query.order_by(Question.id).all()
        categories = Category.query.all()
        formated_categories = [category.type
                               for category in categories]
        formated_questions = paginate_questions(
            request, selection_of_questions)
        if len(formated_questions) == 0 and len(formated_categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': formated_questions,
            'total_questions': len(Question.query.all()),
            'categories': formated_categories,
            'current_category': None,
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            if question is None:
                abort(404)

            question.delete()
            selection_of_questions = Question.query.order_by(Question.id).all()
            formated_questions = paginate_questions(
                request, selection_of_questions)

            return jsonify({
                'success': True,

                'question_id_deleted': question_id
            })
        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', 0)

        try:
            question = Question(question=new_question, answer=new_answer,
                                category=new_category, difficulty=new_difficulty)
            question.insert()

            return jsonify({
                'success': True,
                'question_id_add': question.id
            })
        except:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():

        body = request.get_json()
        searchTerm = body.get('searchTerm', None)
        print(search_questions)
        questions = Question.query.filter(
            Question.question.like('%'+searchTerm+'%')).all()
        if questions is None:
            abort(404)

        formated_question = [question.format()
                             for question in questions]
        return jsonify({
            'success': True,
            'questions': formated_question
        })

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        try:
            category = Category.query.get(category_id)
            print(category.id)
            questions = Question.query.filter(
                Question.category == category.id).all()

            if questions is None:
                abort(404)

            formated_questions = [question.format() for question in questions]
            return jsonify({
                'success': True,
                'questions': formated_questions,
                'total_questions': len(formated_questions),
                'current_category': category_id
            })
        except:
            abort(422)

    @app.route('/quizzes', methods=['POST'])
    def get_next_question():
        body = request.get_json()
        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)
        categorie = Category.query.filter(
            Category.type == quiz_category.get('type')).first()
        questions = {}
        if categorie is None:
            queried_questions = Question.query.all()
            questions = [question.format()
                         for question in queried_questions]
            if questions is None:
                abort(404)
        else:
            queried_questions = Question.query.filter(
                Question.category == categorie.id).all()
            questions = [question.format()
                         for question in queried_questions]
            if questions is None:
                abort(404)

            if len(previous_questions) != 0:
                i = 0
                for j in questions:
                    try:
                        questions.remove(previous_questions[i])
                        if len(previous_questions) < i:
                            i = i + 1
                    except:
                        return jsonify({
                            'success': True,
                            'question': None,
                        })

        quizz_question = random.choice(questions)
        return jsonify({
            'success': True,
            'question': quizz_question,
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    return app
