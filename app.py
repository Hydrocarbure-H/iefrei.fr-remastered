import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    Response,
    redirect,
    url_for,
    send_from_directory,
    send_file,
    abort,
)

from utils.markdown import process_markdown_files
from utils.models import (
    get_all_courses,
    update_course,
    add_course,
    db,
    get_course,
    get_all_courses_by_semester,
)

load_dotenv()

# Setup the Flask App
app = Flask(__name__)
app.config.from_object("config.Config")

# Setup the database
db.init_app(app)

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.errorhandler(404)
def page_not_found(e) -> tuple[Response, int]:
    """
    Handle 404 errors by redirecting to /courses
    :param e: The exception instance
    :return: A redirection response to /courses
    """
    logger.warning(f"404: {request.url}")
    return jsonify({"status": "error", "message": "Page Not Found"}), 404


@app.errorhandler(500)
def internal_server_error(e) -> tuple[Response, int]:
    """
    Handle 500 errors by redirecting to /courses
    :param e: The exception instance
    :return: A redirection response to /courses
    """
    logger.error(f"500: {request.url}")
    return jsonify({"status": "error", "message": "Internal Server Error"}), 500


@app.route("/")
def root() -> Response:
    """
    Redirect from / to /courses
    :return: A redirection response to /courses
    """
    return redirect(url_for("index"))


@app.route("/courses", methods=["GET"])
def index() -> str:
    """
    Render the index page
    :return: The index page as str... I guess...
    """
    courses: list[dict[str, Any]] = get_all_courses()
    current_semester: str = os.getenv("SEMESTER")
    return render_template(
        "courses.html",
        courses=courses,
        current_year=datetime.now().year,
        current_semester=current_semester,
    )


@app.route("/courses/semester/<int:semester>", methods=["GET"])
def courses_by_semester(semester: int) -> str:
    """
    Render the index page with courses filtered by the selected semester.
    :param semester: The semester number
    :return: The index page with courses for the specified semester
    """
    # Assuming get_all_courses_by_semester is a function that returns the courses for a specific semester
    courses: list[dict[str, Any]] = get_all_courses_by_semester(semester)
    current_semester: str = str(semester)
    return render_template(
        "courses.html",
        courses=courses,
        current_year=datetime.now().year,
        current_semester=current_semester,
    )


@app.route("/assets/<semester>/<course_name>/<path:filename>")
def serve_assets(semester, course_name, filename):
    """
    Serve static asset files (e.g., images) from an external directory.

    This route handles requests for asset files stored in the external MD_FOLDER directory.
    The URL structure includes the semester and course name, which are used to locate the
    appropriate asset directory.

    :param semester: The semester identifier (e.g., s7, s8).
    :param course_name: The name of the course.
    :param filename: The name of the file to serve.
    :return: The file content served from the directory or redirect to index if not found.
    """
    # Construct the full path to the assets directory
    asset_folder = os.path.join(
        os.getenv("MD_FOLDER_LOCATION"), f"md_sync_s{semester}", "Cours", course_name
    )

    # Construct the full file path
    file_path = os.path.join(asset_folder, filename)

    # Check if the file exists and serve it, otherwise redirect to the index page
    if os.path.exists(file_path):
        return send_from_directory(asset_folder, filename)
    else:
        return redirect(url_for("index"))


@app.route("/courses/<int:course_id>", methods=["GET"])
def course(course_id: int) -> str | Response:
    """
    Render the course page with the HTML content of the course.
    :param course_id: The course id
    :return: The course page as Response
    """
    db_course: Optional[Dict[str, Any]] = get_course(id=course_id)

    if db_course:
        # Get the path of the HTML file from the course data
        html_file_path = db_course.get("html_path")

        if os.path.exists(html_file_path):
            # Read the content of the HTML file
            with open(html_file_path, "r", encoding="utf-8") as f:
                course_html_content = f.read()

            # Render the course.html template and pass the HTML content
            return render_template(
                "course.html",
                course=db_course,
                current_year=datetime.now().year,
                course_html_content=course_html_content,
            )

    # Redirect to index if the course is not found
    return redirect(url_for("index"))


@app.route("/download/<int:course_id>", methods=["GET"])
def download_pdf(course_id: int):
    """
    Serve the PDF file for the specified course.
    :param course_id: The ID of the course.
    :return: The PDF file if it exists, or a 404 error if it does not.
    """
    course = get_course(
        id=course_id
    )  # Assuming get_course returns the course data as a dictionary
    if course and os.path.exists(course["pdf_path"]):
        return send_file(
            course["pdf_path"],
            as_attachment=True,
            download_name=f"{course['title']}.pdf",
        )
    else:
        abort(404, description="Resource not found")


@app.route("/api/refresh", methods=["GET"])
def refresh() -> Response | tuple[Response, int]:
    """
    Refresh the courses in the database
    :return: The Flask Response
    """
    key: str = request.args.get("key", "")
    if key == app.config["REFRESH_KEY"]:
        # Refresh the courses
        try:
            courses: List[Dict[str, Any]] = process_markdown_files(
                os.path.join(
                    str(app.config["MD_FOLDER_LOCATION"]), app.config["MD_FOLDER_NAME"]
                )
            )
            for course in courses:
                existing_course: Optional[Dict[str, Any]] = get_course(
                    course["html_path"]
                )
                if existing_course:
                    if existing_course["size"] != course["size"]:
                        update_course(course)
                else:
                    add_course(course)
            return jsonify({"status": "success", "courses": courses})

        # If an error occurs, return an error message
        except ValueError as e:
            return jsonify({"status": "invalid", "message": str(e)}), 400
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    # If the key is invalid, return a forbidden message
    return jsonify({"status": "error", "message": "Invalid Refresh Key"}), 403


if __name__ == "__main__":
    with app.app_context():
        print("Creating all tables...", end="")
        db.create_all()
        print("Tables created!")
    app.run(debug=app.config["DEBUG"], host=app.config["HOST"], port=app.config["PORT"])
