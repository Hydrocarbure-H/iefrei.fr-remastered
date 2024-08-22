from flask import Flask, render_template, request, jsonify, Response
from dotenv import load_dotenv

from utils.models import init_db, get_courses, update_course, add_course
from utils.markdown import process_markdown_files
import os
from typing import List, Dict, Any, Tuple
load_dotenv()
app = Flask(__name__)
app.config.from_object('config.Config')

@app.route('/')
def index() -> str:
    return render_template('index.html')

@app.route('/api/refresh', methods=['GET'])
def api_courses() -> Response | tuple[Response, int]:
    key: str = request.args.get('key', '')
    if key == app.config['REFRESH_KEY']:
        courses: List[Dict[str, Any]] = process_markdown_files(app.config['MD_FOLDER'])
        for course in courses:
            existing_course = get_courses(course['html_path'])
            if existing_course:
                if existing_course['size'] != course['size']:
                    update_course(course)
            else:
                add_course(course)
        return jsonify({"status": "success", "courses": courses})
    return jsonify({"status": "error", "message": "Invalid Refresh Key"}), 403

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
