import logging
from datetime import datetime
from typing import List, Dict, Any

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, Response, redirect, url_for

from utils.markdown import process_markdown_files
from utils.models import get_all_courses, update_course, add_course, db

load_dotenv()

# Setup the Flask App
app = Flask(__name__)
app.config.from_object('config.Config')

# Setup the database
db.init_app(app)

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/')
def root() -> Response:
    """
    Redirect from / to /courses
    :return: A redirection response to /courses
    """
    return redirect(url_for('index'))


@app.route('/courses', methods=['GET'])
def index() -> str:
    """
    Render the index page
    :return: The index page as str... I guess...
    """
    courses: list[dict[str, Any]] = get_all_courses()
    return render_template('courses.html', courses=courses, current_year=datetime.now().year)


@app.route('/api/refresh', methods=['GET'])
def api_courses() -> Response | tuple[Response, int]:
    """
    Refresh the courses in the database
    :return: The Flask Response
    """
    key: str = request.args.get('key', '')
    if key == app.config['REFRESH_KEY']:
        # Refresh the courses
        try:
            courses: List[Dict[str, Any]] = process_markdown_files(app.config['MD_FOLDER'])
            for course in courses:
                existing_course = get_courses(course['html_path'])
                if existing_course:
                    if existing_course['size'] != course['size']:
                        update_course(course)
                else:
                    add_course(course)
            return jsonify({"status": "success", "courses": courses})

        # If an error occurs, return an error message
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    # If the key is invalid, return a forbidden message
    return jsonify({"status": "error", "message": "Invalid Refresh Key"}), 403


@app.errorhandler(404)
def page_not_found(e) -> Response:
    """
    Handle 404 errors by redirecting to /courses
    :param e: The exception instance
    :return: A redirection response to /courses
    """
    logger.warning(f"404: {request.url}")
    return redirect(url_for('index'))


@app.errorhandler(500)
def internal_server_error(e) -> Response:
    """
    Handle 500 errors by redirecting to /courses
    :param e: The exception instance
    :return: A redirection response to /courses
    """
    logger.error(f"500: {request.url}")
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])
